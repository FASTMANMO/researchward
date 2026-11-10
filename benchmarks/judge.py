#!/usr/bin/env python3
"""Judge whether repeat reports on the same paper reach the same reading of it.

For every pair of runs of one setup on one paper, a judge model reads the two
reports, without being told which setup wrote them, and answers same / partly /
different for four things: the paper's readers, its problem, its stakes and its
contribution. Layout, length and wording are ignored. Results go to one JSON line
per pair, so the graphs can be redrawn without judging again.

Usage:
  python3 judge.py data/runs.jsonl --source variation-12-papers --out data/judgments.jsonl
Pairs already in --out are skipped.
"""
import argparse, json, os, random, re, shutil, subprocess, tempfile
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from itertools import combinations
from pathlib import Path

ITEMS = ["readers", "problem", "stakes", "contribution"]
SCORE = {"same": 1.0, "partly": 0.5, "different": 0.0}
PROMPT = """Two reports below were written about the same research paper. Judge whether \
they reach the same reading of the paper. Ignore layout, length, wording and tone; compare \
only what each report says about the paper. If one report does not address an item, answer \
"different" for that item.

For each item, answer "same" (both identify essentially the same thing), "partly" (they \
overlap, but one names something central that the other misses or contradicts) or \
"different":
- readers: who the paper is written for
- problem: what the paper says is wrong, missing or not yet understood
- stakes: what it costs those readers if the problem is left alone
- contribution: what the paper offers to resolve the problem

Reply with JSON only, no other text:
{"readers": "...", "problem": "...", "stakes": "...", "contribution": "..."}

<report_a>
%s
</report_a>

<report_b>
%s
</report_b>
"""


def judge(pair, model):
    a, b = pair["a"], pair["b"]
    first, second = (a, b) if random.Random(pair["key"]).random() < 0.5 else (b, a)
    home = Path(tempfile.mkdtemp(prefix="rw-judge-"))
    env = dict(os.environ, HOME=str(home), CLAUDE_CODE_SYNC_SKILLS="0",
               CLAUDE_CODE_DISABLE_BUNDLED_SKILLS="1")
    cmd = ["claude", "-p", "--model", model, "--output-format", "json", "--tools", "",
           "--strict-mcp-config", "--no-chrome", "--no-session-persistence", "--max-turns", "1"]
    verdict, err, cost = None, None, None
    for _ in range(2):  # one retry on a malformed answer
        proc = subprocess.run(cmd, input=PROMPT % (first["report"], second["report"]),
                              cwd=home, env=env, capture_output=True, text=True, timeout=600)
        try:
            out = json.loads(proc.stdout)
            cost = out.get("total_cost_usd")
            m = re.search(r"\{[^{}]*\}", out.get("result", ""))
            v = json.loads(m.group(0)) if m else {}
            if all(str(v.get(k, "")).lower() in SCORE for k in ITEMS):
                verdict = {k: v[k].lower() for k in ITEMS}
                break
            err = "malformed: " + out.get("result", "")[:200]
        except Exception as e:  # noqa: BLE001
            err = f"{type(e).__name__}: {proc.stderr[-200:] or proc.stdout[-200:]}"
    shutil.rmtree(home, ignore_errors=True)
    row = {k: pair[k] for k in ("source", "arm", "paper", "run_a", "run_b")}
    row.update(judge_model=model, verdict=verdict, error=None if verdict else err,
               cost_usd=cost,
               agreement=None if not verdict else sum(SCORE[verdict[k]] for k in ITEMS) / 4)
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("results", nargs="+")
    ap.add_argument("--source", nargs="+", help="batches to judge (default: all)")
    ap.add_argument("--judge-model", default="claude-sonnet-5-5")
    ap.add_argument("-j", "--jobs", type=int, default=4)
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, help="judge at most this many pairs (for a test)")
    a = ap.parse_args()

    runs = [json.loads(l) for f in a.results for l in open(f) if l.strip()]
    runs = [r for r in runs if r.get("report") and not r.get("error")
            and (not a.source or r.get("source") in a.source)]
    groups = defaultdict(list)
    for r in runs:
        groups[(r.get("source"), r["arm"], r["paper"])].append(r)
    done = set()
    if Path(a.out).exists():
        for l in open(a.out):
            d = json.loads(l)
            if d.get("verdict"):
                done.add((d["source"], d["arm"], d["paper"], d["run_a"], d["run_b"],
                          d["judge_model"]))
    pairs = []
    for (src, arm, paper), rs in sorted(groups.items()):
        rs = sorted(rs, key=lambda r: r["run"])
        for x, y in combinations(rs, 2):
            k = (src, arm, paper, x["run"], y["run"], a.judge_model)
            if k not in done:
                pairs.append({"source": src, "arm": arm, "paper": paper, "run_a": x["run"],
                              "run_b": y["run"], "a": x, "b": y, "key": "|".join(map(str, k))})
    pairs = pairs[: a.limit] if a.limit else pairs
    print(f"{len(pairs)} pairs to judge ({len(done)} already done)", flush=True)
    with ThreadPoolExecutor(a.jobs) as pool, open(a.out, "a") as out:
        for row in pool.map(lambda p: judge(p, a.judge_model), pairs):
            out.write(json.dumps(row) + "\n")
            out.flush()
            print(f"{row['arm']:8} {row['paper'][:24]:24} {row['run_a']}-{row['run_b']}: "
                  f"{row['agreement']}  {row['verdict'] or row['error']}", flush=True)


if __name__ == "__main__":
    main()
