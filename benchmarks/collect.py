#!/usr/bin/env python3
"""Gather benchmark runs into benchmarks/data/, so the graphs can be redrawn
or restyled later without running anything again.

Writes:
  data/runs.jsonl   every run, in full: tokens, cost, turns, time, tools, report text
  data/runs.csv     the same runs without the report text, one row per run
  data/papers.csv   the papers (title, pages, words); the PDFs themselves are not stored

Usage:
  python3 collect.py <results.jsonl> [more.jsonl ...] [--tag NAME --skill-version V]
Runs already in data/runs.jsonl are kept; a run is identified by
(source, arm, paper, pages, run).
"""
import argparse, csv, json
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data"
TITLES = {  # file key -> title, for papers whose PDF has no title field
    "11p-Towery_et_al_-_PRE_on_Spectral_kinetic_e.pdf":
        "Spectral kinetic energy transfer in turbulent premixed reacting flows",
    "22p-B._P._Murray_and_M._D._Bustamante_Energy.pdf":
        "Energy flux enhancement, intermittency and turbulence via Fourier triad phase "
        "dynamics in the 1-D Burgers equation",
    "25p-Multiscale_energy_transfer_in_the_extend.pdf":
        "Multiscale energy transfer in the extended buffer layer of dilute viscoelastic "
        "channel flows",
}
FIELDS = ["source", "skill_version", "arm", "paper", "pages", "words", "run", "model", "effort",
          "tokens_total", "tokens_input", "tokens_cache_write", "tokens_cache_read",
          "tokens_output", "cost_usd", "turns", "seconds", "skill_used", "report_words", "error"]


def key(r):
    return (r.get("source"), r["arm"], r.get("paper"), r["pages"], r["run"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("results", nargs="+")
    ap.add_argument("--tag", help="source name for these runs (default: file name)")
    ap.add_argument("--skill-version", default="")
    ap.add_argument("--titles", help="optional papers.csv-style file of file,title")
    a = ap.parse_args()
    DATA.mkdir(exist_ok=True)

    store = DATA / "runs.jsonl"
    rows = [json.loads(l) for l in store.open()] if store.exists() else []
    seen = {key(r): i for i, r in enumerate(rows)}
    for f in a.results:
        for line in open(f):
            if not line.strip():
                continue
            r = json.loads(line)
            r.setdefault("source", a.tag or Path(f).stem)
            if a.skill_version:
                r.setdefault("skill_version", a.skill_version)
            r.setdefault("paper", f"{r['pages']}p-cut")
            k = key(r)
            if k in seen:
                rows[seen[k]] = r
            else:
                seen[k] = len(rows)
                rows.append(r)
    with store.open("w") as out:
        for r in rows:
            out.write(json.dumps(r) + "\n")

    with (DATA / "runs.csv").open("w", newline="") as out:
        w = csv.DictWriter(out, fieldnames=FIELDS)
        w.writeheader()
        for r in rows:
            t = r.get("tokens", {})
            w.writerow({
                "source": r.get("source"), "skill_version": r.get("skill_version", ""),
                "arm": r["arm"], "paper": r.get("paper"), "pages": r["pages"],
                "words": r.get("words", ""), "run": r["run"], "model": r.get("model"),
                "effort": r.get("effort"), "tokens_total": r.get("tokens_total"),
                "tokens_input": t.get("input"), "tokens_cache_write": t.get("cache_write"),
                "tokens_cache_read": t.get("cache_read"), "tokens_output": t.get("output"),
                "cost_usd": r.get("cost_usd"), "turns": r.get("turns"), "seconds": r.get("seconds"),
                "skill_used": bool(r.get("skills")), "report_words": r.get("report_words"),
                "error": bool(r.get("error")),
            })

    papers = {}
    for r in rows:
        p = r.get("paper")
        if p and p not in papers:
            papers[p] = {"paper": p, "title": TITLES.get(p, ""), "pages": r["pages"],
                         "words": r.get("words", "")}
    old = DATA / "papers.csv"
    if old.exists():
        for row in csv.DictReader(old.open()):
            if row["paper"] in papers and row.get("title"):
                papers[row["paper"]]["title"] = row["title"]
    with old.open("w", newline="") as out:
        w = csv.DictWriter(out, fieldnames=["paper", "title", "pages", "words"])
        w.writeheader()
        w.writerows(sorted(papers.values(), key=lambda p: (int(p["pages"]), p["paper"])))
    print(f"{len(rows)} runs, {len(papers)} papers in {DATA}")


if __name__ == "__main__":
    main()
