#!/usr/bin/env python3
"""Trigger test: which wordings make each skill fire, and which leave both alone.

Each prompt in trigger_prompts.json runs --runs times, each in a fresh, empty home
folder with only mcenerney-lens and effective-writing installed (account-synced and
bundled skills off, so nothing else competes). A run stops as soon as the model calls
a skill, or when it answers without one, so no full report is written.

Usage:
  python3 triggers.py --paper short-paper.pdf --runs 3 --out data/triggers.jsonl
  python3 triggers.py --summary data/triggers.jsonl     # per-prompt table only
Runs already in --out (same prompt, run and model) are skipped.
"""
import argparse, csv, json, os, re, shutil, subprocess, tempfile, time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
SKILLS = ["mcenerney-lens", "effective-writing"]


def versions() -> str:
    out = []
    for s in SKILLS:
        m = re.search(r'version: "([^"]+)"', (REPO / "skills" / s / "SKILL.md").read_text())
        out.append(f"{s} {m.group(1) if m else '?'}")
    return ", ".join(out)


VERSIONS = versions()
OLD = "mcenerney-lens 0.8.0, effective-writing 0.6.0"  # runs saved before versions were stamped


def plugin(tmp: Path) -> Path:
    """One plugin folder holding both skills, without their tests."""
    plug = tmp / "researchward-plugin"
    (plug / ".claude-plugin").mkdir(parents=True)
    (plug / ".claude-plugin/plugin.json").write_text(json.dumps(
        {"name": "researchward", "version": "0.0.0", "description": "Researchward skills"}))
    for s in SKILLS:
        shutil.copytree(REPO / "skills" / s, plug / "skills" / s,
                        ignore=shutil.ignore_patterns("evals"))
    return plug


def skill_name(raw: str) -> str:
    raw = (raw or "").split(":")[-1]
    return raw if raw in SKILLS else (raw or "?")


def one(p, run, model, effort, plug, paper, max_turns):
    work = Path(tempfile.mkdtemp(prefix=f"rw-trig-{p['id']}-{run}-"))
    if "paper.pdf" in p["text"]:
        shutil.copy(paper, work / "paper.pdf")
    cmd = ["claude", "-p", p["prompt"], "--model", model, "--effort", effort,
           "--output-format", "stream-json", "--verbose", "--no-session-persistence",
           "--max-turns", str(max_turns), "--tools", "Read,Skill", "--allowedTools",
           "Read,Skill", "--strict-mcp-config", "--no-chrome", "--plugin-dir", str(plug)]
    env = dict(os.environ, HOME=str(work), CLAUDE_CODE_SYNC_SKILLS="0",
               CLAUDE_CODE_DISABLE_BUNDLED_SKILLS="1")
    t0, fired, tools, ended = time.time(), [], [], "answered"
    proc = subprocess.Popen(cmd, cwd=work, env=env, stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL, text=True)
    try:
        for line in proc.stdout:
            if not line.startswith("{"):
                continue
            e = json.loads(line)
            if e.get("type") == "assistant":
                for b in e.get("message", {}).get("content", []):
                    if b.get("type") == "tool_use":
                        tools.append(b.get("name"))
                        if b.get("name") == "Skill":
                            fired.append(skill_name(b.get("input", {}).get("skill")))
                if fired:  # the decision is made; no need to let it write the report
                    ended = "skill called"
                    break
            elif e.get("type") == "result":
                ended = "answered" if e.get("subtype") == "success" else e.get("subtype", "?")
                break
    finally:
        proc.kill()
        proc.wait()
        shutil.rmtree(work, ignore_errors=True)
    first = fired[0] if fired else "none"
    return {"id": p["id"], "kind": p["kind"], "expect": p["expect"], "run": run,
            "skills": VERSIONS,
            "model": model, "effort": effort, "fired": first, "all_fired": fired,
            "correct": first == p["expect"], "tools_before": tools, "ended": ended,
            "seconds": round(time.time() - t0, 1)}


def summary(path, out_csv=None, version=None):
    rows = [json.loads(l) for l in open(path) if l.strip()]
    for r in rows:
        r.setdefault("skills", OLD)
    version = version or rows[-1]["skills"]
    rows = [r for r in rows if r["skills"] == version]
    print(f"Skills: {version}")
    by = defaultdict(list)
    for r in rows:
        by[(r["model"], r["id"])].append(r)
    prompts = {p["id"]: p for p in json.loads((HERE / "trigger_prompts.json").read_text())["prompts"]}
    table = []
    for (model, pid), rs in by.items():
        p = prompts.get(pid, {"text": "?", "kind": "?", "expect": rs[0]["expect"]})
        fired = defaultdict(int)
        for r in rs:
            fired[r["fired"]] += 1
        table.append({"skills": version, "model": model, "id": pid, "kind": p["kind"], "expect": p["expect"],
                      "runs": len(rs), "correct": sum(r["correct"] for r in rs),
                      "fired": "; ".join(f"{k} {v}" for k, v in sorted(fired.items())),
                      "prompt": p["text"].split("\n")[0][:90]})
    ids = list(prompts)
    table.sort(key=lambda t: (t["model"], ids.index(t["id"]) if t["id"] in ids else 99))
    if out_csv:
        with open(out_csv, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(table[0]))
            w.writeheader()
            w.writerows(table)
    for t in table:
        mark = "ok " if t["correct"] == t["runs"] else ("~  " if t["correct"] else "NO ")
        print(f"{mark}{t['correct']}/{t['runs']}  {t['model'][7:]:11} {t['id']:16} expect {t['expect']:17} got: "
              f"{t['fired']:32} | {t['prompt']}")
    for model in sorted({t["model"] for t in table}):
        for exp in ("mcenerney-lens", "effective-writing", "none"):
            ts = [t for t in table if t["model"] == model and t["expect"] == exp]
            if ts:
                c, n = sum(t["correct"] for t in ts), sum(t["runs"] for t in ts)
                print(f"{model} · expect {exp}: {c}/{n} correct ({100 * c / n:.0f}%)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--paper", help="a short paper PDF, used for prompts that mention paper.pdf")
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--model", nargs="+", default=["claude-opus-5-5"])
    ap.add_argument("--effort", default="medium")
    ap.add_argument("--max-turns", type=int, default=4)
    ap.add_argument("--only", nargs="+", help="prompt ids to run")
    ap.add_argument("-j", "--jobs", type=int, default=6)
    ap.add_argument("--out", default=str(HERE / "data/triggers.jsonl"))
    ap.add_argument("--summary", help="print the per-prompt table for this file and stop")
    ap.add_argument("--version", help="with --summary: which skill versions (default: latest)")
    a = ap.parse_args()
    if a.summary:
        summary(a.summary, Path(a.summary).with_suffix(".csv"), a.version)
        return

    spec = json.loads((HERE / "trigger_prompts.json").read_text())
    prompts = [p for p in spec["prompts"] if not a.only or p["id"] in a.only]
    for p in prompts:
        p["prompt"] = p["text"].format(paragraph=spec["paragraph"], sentence=spec["sentence"])
    done = set()
    if Path(a.out).exists():
        done = {(r["id"], r["run"], r["model"], r.get("skills", OLD))
                for r in map(json.loads, open(a.out))}
    jobs = [(p, r, m) for m in a.model for r in range(1, a.runs + 1) for p in prompts
            if (p["id"], r, m, VERSIONS) not in done]
    print(f"{len(jobs)} runs to do ({len(done)} already done)", flush=True)
    tmp = Path(tempfile.mkdtemp(prefix="rw-trig-"))
    plug = plugin(tmp)
    with ThreadPoolExecutor(a.jobs) as pool, open(a.out, "a") as out:
        futs = [pool.submit(one, p, r, m, a.effort, plug, a.paper, a.max_turns)
                for p, r, m in jobs]
        for f in futs:
            row = f.result()
            out.write(json.dumps(row) + "\n")
            out.flush()
            print(f"{'ok' if row['correct'] else 'XX'} {row['id']:16} run {row['run']} "
                  f"{row['model']}: fired {row['fired']} ({row['ended']}, {row['seconds']}s)",
                  flush=True)
    shutil.rmtree(tmp, ignore_errors=True)
    summary(a.out, Path(a.out).with_suffix(".csv"))


if __name__ == "__main__":
    main()
