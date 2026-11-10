#!/usr/bin/env python3
"""Run the Researchward benchmark: one paper, three ways of asking.

Arms (same model, same effort, same question):
  plain    the model alone
  skill    the model with the mcenerney-lens skill
  handout  the model with Handout 1 (the PDF) to apply

Each run happens in a fresh, empty home folder with account-synced and
bundled skills switched off, so the only difference between arms is the
skill or the handout. Results go to one JSON line per run.

Usage:
  python3 run.py --paper paper.pdf --pages 5 10 15 19 --runs 1 --out results.jsonl
"""
import argparse, json, os, re, shutil, subprocess, tempfile, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
HANDOUT = REPO / "docs/handouts/mcenerney-lens-handout.pdf"
_ver = re.search(r'version: "([^"]+)"', (REPO / "skills/mcenerney-lens/SKILL.md").read_text())
_commit = subprocess.run(["git", "-C", str(REPO), "log", "-1", "--format=%h", "--",
                          "skills/mcenerney-lens"],  # last commit that changed the skill
                         capture_output=True, text=True).stdout.strip()
SKILL_VERSION = f"mcenerney-lens {_ver.group(1) if _ver else '?'} ({_commit})"

QUESTION = (
    "I'm reading the paper in paper.pdf. Dissect it through Larry McEnerney's "
    "reader-value lens: who it is written for, its problem, its stance toward prior "
    "work, the stakes, the doubts it answers, its contribution, its structure and any "
    "pitfalls, with where each appears in the paper."
)
EXTRA = {
    "plain": "",
    "skill": "",
    "handout": " Apply the method in handout.pdf, which compiles McEnerney's lecture.",
}


def lens_plugin(tmp: Path) -> Path:
    """A plugin folder holding only mcenerney-lens, without its tests."""
    plug = tmp / "lens-plugin"
    (plug / ".claude-plugin").mkdir(parents=True)
    (plug / ".claude-plugin/plugin.json").write_text(json.dumps(
        {"name": "researchward-lens", "version": "0.0.0", "description": "mcenerney-lens"}))
    shutil.copytree(REPO / "skills/mcenerney-lens", plug / "skills/mcenerney-lens",
                    ignore=shutil.ignore_patterns("evals"))
    return plug


def truncate(paper: Path, pages: int, out: Path) -> Path:
    subprocess.run(["qpdf", "--empty", "--pages", str(paper), f"1-{pages}", "--", str(out)],
                   check=True)
    return out


def one_run(arm, pages, run, paper_cut, model, effort, plugin):
    work = Path(tempfile.mkdtemp(prefix=f"rw-{arm}-{pages}p-{run}-"))
    shutil.copy(paper_cut, work / "paper.pdf")
    if arm == "handout":
        shutil.copy(HANDOUT, work / "handout.pdf")
    cmd = ["claude", "-p", QUESTION + EXTRA[arm], "--model", model, "--effort", effort,
           "--output-format", "stream-json", "--verbose", "--no-session-persistence",
           "--max-turns", "40", "--tools", "Read,Skill", "--allowedTools", "Read,Skill",
           "--strict-mcp-config", "--no-chrome"]
    if arm == "skill":
        cmd += ["--plugin-dir", str(plugin)]
    env = dict(os.environ, HOME=str(work), CLAUDE_CODE_SYNC_SKILLS="0",
               CLAUDE_CODE_DISABLE_BUNDLED_SKILLS="1")
    t0 = time.time()
    proc = subprocess.run(cmd, cwd=work, env=env, capture_output=True, text=True, timeout=1800)
    events = [json.loads(l) for l in proc.stdout.splitlines() if l.strip().startswith("{")]
    result = next((e for e in reversed(events) if e.get("type") == "result"), {})
    tools = [b.get("name") for e in events if e.get("type") == "assistant"
             for b in e.get("message", {}).get("content", []) if b.get("type") == "tool_use"]
    skills = [b.get("input", {}).get("skill") for e in events if e.get("type") == "assistant"
              for b in e.get("message", {}).get("content", [])
              if b.get("type") == "tool_use" and b.get("name") == "Skill"]
    mu = next(iter((result.get("modelUsage") or {}).values()), {})
    tok = {
        "input": mu.get("inputTokens", 0),
        "cache_write": mu.get("cacheCreationInputTokens", 0),
        "cache_read": mu.get("cacheReadInputTokens", 0),
        "output": mu.get("outputTokens", 0),
    }
    report = result.get("result") or ""
    shutil.rmtree(work, ignore_errors=True)
    return {
        "arm": arm, "pages": pages, "run": run, "model": model, "effort": effort,
        "skill_version": SKILL_VERSION,
        "tokens_total": sum(tok.values()), "tokens": tok,
        "cost_usd": result.get("total_cost_usd"), "turns": result.get("num_turns"),
        "seconds": round(time.time() - t0, 1), "tools": tools, "skills": skills,
        "error": None if proc.returncode == 0 else proc.stderr[-500:],
        "report_words": len(report.split()), "report": report,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--paper", help="one paper, cut to each of --pages")
    ap.add_argument("--pages", type=int, nargs="+")
    ap.add_argument("--papers", nargs="+", help="several papers, each read in full")
    ap.add_argument("--arms", nargs="+", default=["plain", "skill", "handout"])
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--model", default="claude-opus-5-5")
    ap.add_argument("--effort", default="medium")
    ap.add_argument("-j", "--jobs", type=int, default=3)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    tmp = Path(tempfile.mkdtemp(prefix="rw-bench-"))
    plugin = lens_plugin(tmp)
    if a.papers:  # each paper at full length; key = paper file name
        inputs = {Path(p).name: Path(p) for p in a.papers}
    else:
        inputs = {f"{p}p": truncate(Path(a.paper), p, tmp / f"paper-{p}p.pdf") for p in a.pages}
    info = {}
    for key, pdf in inputs.items():
        pages = int(next(l.split()[-1] for l in subprocess.run(
            ["pdfinfo", str(pdf)], capture_output=True, text=True).stdout.splitlines()
            if l.startswith("Pages:")))
        words = len(subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True,
                                   text=True).stdout.split())
        info[key] = (pages, words)
    jobs = [(arm, k, r) for k in inputs for arm in a.arms for r in range(1, a.runs + 1)]
    with ThreadPoolExecutor(a.jobs) as pool, open(a.out, "a") as out:
        futs = [pool.submit(one_run, arm, info[k][0], r, inputs[k], a.model, a.effort, plugin)
                for arm, k, r in jobs]
        for (arm, k, r), f in zip(jobs, futs):
            row = f.result()
            row["paper"], row["words"] = k, info[k][1]
            out.write(json.dumps(row) + "\n")
            out.flush()
            print(f"{row['arm']:8} {row['pages']:3}p run {row['run']}: "
                  f"{row['tokens_total']:>9,} tokens  ${row['cost_usd'] or 0:.2f}  "
                  f"{row['turns']} turns  skill={row['skills']}  err={bool(row['error'])}",
                  flush=True)
    shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
