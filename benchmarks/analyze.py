#!/usr/bin/env python3
"""Turn benchmark runs into numbers and graphs (MATLAB style).

Reads data/runs.jsonl (or any results.jsonl from run.py) and, for the judged measure,
data/judgments.jsonl from judge.py. Writes, into --csv:
  tokens.csv      tokens per setup and paper (mean over runs)
  deviation.csv   how much repeat reports differ, per setup and paper, plus mean and SD
and into --out:
  tokens.svg      tokens per report vs paper length, least-squares fit per setup
  deviation.svg   how much repeat reports on the same paper differ

Deviation, over every pair of runs of one setup on the same paper (0 = identical):
  layout    share of pairs whose skeletons differ (headings, bold labels, and each table's
            header row and row count)
  length    spread in word count: standard deviation over mean
  quotes    share of quoted passages from the paper that the other run does not quote
  reading   1 - agreement judged blind by judge.py on readers, problem, stakes and
            contribution (same = 1, partly = 0.5, different = 0)
  wording, vocabulary   exact three-word phrases not shared, and 1 - TF-IDF cosine; CSV only
Each measure is computed per paper, then averaged over papers; error bars are one SD.

Usage:
  python3 analyze.py data/runs.jsonl --tokens-source tokens-12-papers \
      --deviation-source variation-12-papers --out ../docs/images --csv data
Without --*-source, every run in the files is used.
"""
import argparse, csv, json, re, statistics
from collections import defaultdict
from itertools import combinations
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

ARMS = ["plain", "skill", "handout"]
NAMES = {"plain": "Model (no skill)", "skill": "mcenerney-lens skill",
         "handout": "McEnerney PDF handout"}
plt.rcParams["svg.fonttype"] = "none"  # keep text as text in the SVG
plt.rcParams["svg.hashsalt"] = "researchward"  # same ids on every redraw, so diffs stay small


def layout(report: str) -> tuple:
    """The report's skeleton: headings, bold labels at line start, and each table's
    header row and row count, in order, with numbers and quotes stripped. Table cells
    below the header are content, not layout."""
    keys, rows = [], None
    for line in report.splitlines() + [""]:
        s = line.strip()
        if s.startswith("|"):
            if rows is None:  # header row of a new table
                keys.append("T:" + "|".join(c.strip().lower() for c in s.strip("|").split("|")))
                rows = 0
            elif not re.match(r"^\|[\s:|-]+\|?$", s):
                rows += 1
            continue
        if rows is not None:
            keys.append(f"N:{rows}")
            rows = None
        if s.startswith("#"):
            keys.append("H:" + s.lstrip("#").strip().lower())
        elif s.startswith("**") and s.count("**") >= 2:
            keys.append("B:" + s.split("**")[1].strip().lower())
    return tuple(k if k.startswith("N:") else re.sub(r"[\d\"“”'‘’…*]", "", k) for k in keys)


def trigrams(text: str) -> set:
    w = re.findall(r"\w+", text.lower())
    return set(zip(w, w[1:], w[2:]))


def quotes(report: str) -> list:
    """Quoted passages of five words or more, each as a set of three-word phrases."""
    qs = re.findall(r'[“"]([^”"\n]{20,400})[”"]', report)
    return [g for g in (trigrams(q) for q in qs) if len(g) >= 3]


def quotes_not_shared(a: list, b: list):
    """Share of each run's quotes that the other run does not quote (a quote counts as
    shared when 60% of the shorter one's three-word phrases appear in the other)."""
    if not a or not b:
        return None
    def found(q, others):
        return any(len(q & o) / min(len(q), len(o)) >= 0.6 for o in others)
    return 1 - (sum(found(q, b) for q in a) / len(a) + sum(found(q, a) for q in b) / len(b)) / 2


def deviation(runs, agreements):
    reports = [r["report"] for r in runs]
    n = len(reports)
    pairs = list(combinations(range(n), 2))
    shapes = [layout(r) for r in reports]
    words = [len(r.split()) for r in reports]
    grams = [trigrams(r) for r in reports]
    qs = [quotes(r) for r in reports]
    q_pairs = [d for d in (quotes_not_shared(qs[i], qs[j]) for i, j in pairs) if d is not None]
    tf = TfidfVectorizer().fit_transform(reports)
    return {
        "runs": n,
        "layouts": len(set(shapes)),
        "layout": statistics.mean(shapes[i] != shapes[j] for i, j in pairs),
        "length": statistics.pstdev(words) / statistics.mean(words),
        "quotes": statistics.mean(q_pairs) if q_pairs else None,
        "reading": 1 - statistics.mean(agreements) if agreements else None,
        "wording": 1 - statistics.mean(len(grams[i] & grams[j]) / len(grams[i] | grams[j])
                                       for i, j in pairs),
        "vocabulary": 1 - statistics.mean(cosine_similarity(tf[i], tf[j])[0, 0]
                                          for i, j in pairs),
        "words_mean": statistics.mean(words),
        "quotes_per_report": statistics.mean(len(q) for q in qs),
        "judged_pairs": len(agreements),
    }


# MATLAB-style figures: white, boxed axes, ticks inward, light solid grid, hollow markers.
MATLAB = {"plain": ("#0072BD", "o", "-"), "skill": ("#D95319", "s", "--"),
          "handout": ("#7E2F8E", "^", "-.")}  # MATLAB colors 1, 2 and 4; validated all-pairs
INK = "#262626"
# Liberation Sans has Arial's metrics, so the SVG lays out the same with Arial or Helvetica.
FONT = {"font.family": "sans-serif",
        "font.sans-serif": ["Liberation Sans", "Arial", "Helvetica", "DejaVu Sans"]}


def matlab_axes(ax):
    ax.set_facecolor("white")
    for side in ax.spines.values():
        side.set_visible(True)
        side.set_color(INK)
        side.set_linewidth(0.6)
    ax.tick_params(direction="in", top=True, right=True, colors=INK, labelsize=10,
                   length=4, width=0.6)
    ax.grid(False)


def plot_tokens(rows, out, model, subtitle):
    with plt.rc_context(FONT):
        fig, ax = plt.subplots(figsize=(6.4, 4.4), dpi=150)
        fig.patch.set_facecolor("white")
        matlab_axes(ax)
        for arm in ARMS:
            pts = sorted((r["pages"], r["tokens_mean"] / 1000) for r in rows if r["arm"] == arm)
            if not pts:
                continue
            x, y = map(np.array, zip(*pts))
            color, marker, line = MATLAB[arm]
            fit = None
            if len(set(x)) >= 2:
                slope, icept = np.polyfit(x, y, 1)
                fit = np.array([x.min(), x.max()])
                ax.plot(fit, slope * fit + icept, color=color, linestyle=line, linewidth=1.5,
                        zorder=3)
            ax.plot(x, y, linestyle="none", marker=marker, markersize=7, markerfacecolor="white",
                    markeredgecolor=color, markeredgewidth=1.5, zorder=4)
            ax.plot([], [], color=color, linestyle=line, linewidth=1.5, marker=marker,
                    markersize=7, markerfacecolor="white", markeredgewidth=1.5,
                    label=NAMES[arm])  # legend entry: marker on its fit line
        ax.set_xlabel("Paper length (pages)", color=INK, fontsize=11)
        ax.set_ylabel("Tokens per report", color=INK, fontsize=11)
        ax.text(0, 1.01, "×10³", transform=ax.transAxes, ha="left", va="bottom", color=INK,
                fontsize=10)  # MATLAB-style axis exponent
        ax.set_xlim(5, 26)
        ax.set_xticks(range(5, 26, 5))
        ax.set_ylim(0, 140)
        ax.set_title(f"Tokens usage Vs Paper length ({model})", color=INK,
                     fontsize=12, fontweight="bold", pad=34)
        ax.text(0.5, 1.065, subtitle, transform=ax.transAxes, ha="center", va="bottom",
                color=INK, fontsize=8.5)
        leg = ax.legend(loc="lower right", fontsize=9, frameon=True, fancybox=False,
                        edgecolor=INK, framealpha=1, borderpad=0.5, handlelength=2.6)
        leg.get_frame().set_linewidth(0.6)
        fig.tight_layout()
        fig.savefig(out, facecolor="white", metadata={"Date": None})
        plt.close(fig)


# Plotted measures; quotes, reading, wording and vocabulary stay in deviation.csv only.
MEASURES = [("layout", "Different layout"), ("length", "Change in report length")]


def plot_deviation(dev, out, model, subtitle, notes=None):
    """One panel per measure, each with its own y-scale, and a shared legend.
    notes: {(measure, arm): text} to point at a bar, e.g. what a small value comes from."""
    measures = [(k, label) for k, label in MEASURES
                if any(dev[a].get(k) is not None for a in dev)]
    arms = [a for a in ARMS if a in dev]
    with plt.rc_context(FONT):
        fig, axes = plt.subplots(1, len(measures), figsize=(6.4, 4.4), dpi=150, squeeze=False)
        fig.patch.set_facecolor("white")
        for ax, (k, label) in zip(axes[0], measures):
            matlab_axes(ax)
            ax.tick_params(axis="x", top=False, bottom=False, labelbottom=False)
            top, tops = 0, []
            for i, arm in enumerate(arms):
                m = 100 * (dev[arm][k] or 0)
                e = 100 * (dev[arm].get(k + "_sd") or 0)
                ax.bar(i, m, width=0.7, color=MATLAB[arm][0], edgecolor=INK, linewidth=0.6,
                       label=NAMES[arm], zorder=3)
                if e:
                    ax.errorbar(i, m, yerr=[[min(m, e)], [e]], fmt="none", ecolor=INK,
                                elinewidth=0.8, capsize=3, capthick=0.8, zorder=4)
                top = max(top, m + e)
                tops.append((i, m, e))
            ax.set_xlim(-0.6, len(arms) - 0.4)
            nice = next(v for v in (5, 10, 15, 20, 25, 30, 40, 50, 60, 80, 100)
                        if v >= top * 1.12) if top < 90 else 100
            ylim = nice * 1.12 if nice == 100 else nice
            ax.set_ylim(0, ylim)
            ax.set_yticks(np.linspace(0, nice, 6 if nice % 5 == 0 and nice >= 20 else nice // 1 + 1)
                          if nice >= 20 else range(0, nice + 1, 1))
            for i, m, e in tops:  # value labels just above each error bar
                ax.text(i, m + e + ylim * 0.015, f"{m:.0f}%", ha="center", va="bottom",
                        color=INK, fontsize=9)
                note = (notes or {}).get((k, arms[i]))
                if note:  # MATLAB-style text arrow pointing at the value label
                    ax.annotate(note, xy=(i, m + e + ylim * 0.07), xytext=(i, ylim * 0.5),
                                ha="center", va="center", color=INK, fontsize=7.5,
                                linespacing=1.25, zorder=5,
                                bbox=dict(boxstyle="square,pad=0.3", fc="white", ec=INK, lw=0.6),
                                arrowprops=dict(arrowstyle="->", color=INK, lw=0.7))
            ax.set_xlabel(label, color=INK, fontsize=11, labelpad=6)
            ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))
        axes[0][0].set_ylabel("Difference between repeat runs", color=INK, fontsize=11)
        fig.text(0.5, 0.99, f"Consistency check for repeated runs ({model})", ha="center",
                 va="top", color=INK, fontsize=12, fontweight="bold")
        fig.text(0.5, 0.905, subtitle, ha="center", va="bottom", color=INK, fontsize=8.5)
        handles, labels = axes[0][0].get_legend_handles_labels()
        leg = fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 0.895),
                         ncol=len(arms), fontsize=9, frameon=True, fancybox=False,
                         edgecolor=INK, framealpha=1, handlelength=1.4, columnspacing=1.2)
        leg.get_frame().set_linewidth(0.6)
        fig.tight_layout(rect=(0, 0, 1, 0.835), w_pad=2.5)
        fig.savefig(out, facecolor="white", metadata={"Date": None})
        plt.close(fig)


def load(files, sources):
    runs = [json.loads(l) for f in files for l in open(f) if l.strip()]
    runs = [r for r in runs if not r.get("error") and r.get("report")]
    return [r for r in runs if not sources or r.get("source") in sources]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("results", nargs="+")
    ap.add_argument("--tokens-source", nargs="+", help="batches for the tokens graph")
    ap.add_argument("--deviation-source", nargs="+", help="batches for the deviation graph")
    ap.add_argument("--out", required=True, help="folder for the graphs")
    ap.add_argument("--csv", help="folder for tokens.csv and deviation.csv (default: --out)")
    ap.add_argument("--skill-layout-note", help="text pointing at the skill's layout bar")
    ap.add_argument("--judgments", default=str(Path(__file__).parent / "data/judgments.jsonl"),
                    help="judge.py output for the judged-reading measure")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    csv_dir = Path(a.csv or a.out)
    csv_dir.mkdir(parents=True, exist_ok=True)

    by_tok = by = defaultdict(list)
    for r in load(a.results, a.tokens_source):
        by[(r["arm"], r.get("paper") or f"{r['pages']}p")].append(r)
    tok_rows = [{"arm": arm, "paper": paper, "pages": rs[0]["pages"],
                 "words": rs[0].get("words", ""), "runs": len(rs),
                 "tokens_mean": round(statistics.mean(r["tokens_total"] for r in rs)),
                 "output_mean": round(statistics.mean(r["tokens"]["output"] for r in rs)),
                 "cost_mean": round(statistics.mean(r["cost_usd"] or 0 for r in rs), 3)}
                for (arm, paper), rs in sorted(by.items(), key=lambda kv: (
                    ARMS.index(kv[0][0]), kv[1][0]["pages"], kv[0][1]))]
    with open(csv_dir / "tokens.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(tok_rows[0]))
        w.writeheader()
        w.writerows(tok_rows)

    agree = defaultdict(list)
    if Path(a.judgments).exists():
        for l in open(a.judgments):
            j = json.loads(l)
            if j.get("agreement") is not None and (
                    not a.deviation_source or j.get("source") in a.deviation_source):
                agree[(j["arm"], j["paper"])].append(j["agreement"])
    by = defaultdict(list)
    for r in load(a.results, a.deviation_source):
        by[(r["arm"], r.get("paper") or f"{r['pages']}p")].append(r)
    per_paper = {k: deviation(rs, agree.get(k, [])) for k, rs in sorted(by.items())
                 if len(rs) >= 2}
    cols = ["layout", "length", "quotes", "reading", "wording", "vocabulary", "words_mean",
            "quotes_per_report"]
    dev = {}
    for arm in ARMS:
        ds = [d for (a_, _), d in per_paper.items() if a_ == arm]
        if not ds:
            continue
        dev[arm] = {"papers": len(ds)}
        for c in cols:
            vals = [d[c] for d in ds if d[c] is not None]
            dev[arm][c] = statistics.mean(vals) if vals else None
            dev[arm][c + "_sd"] = statistics.stdev(vals) if len(vals) >= 2 else None
    if per_paper:
        def f(v, nd=3):
            return "" if v is None else f"{v:.{nd}f}"
        with open(csv_dir / "deviation.csv", "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["arm", "paper", "runs", "distinct_layouts", "judged_pairs", *cols])
            for (arm, paper), d in per_paper.items():
                w.writerow([arm, paper, d["runs"], d["layouts"], d["judged_pairs"],
                            *(f(d[c]) for c in cols)])
            for arm, d in dev.items():
                w.writerow([arm, "mean", "", "", "", *(f(d[c]) for c in cols)])
                w.writerow([arm, "sd", "", "", "", *(f(d[c + "_sd"]) for c in cols)])
    def model_name(groups):
        name = next(iter(groups.values()))[0].get("model", "").replace("claude-", "").split("-")
        return f"{name[0].title()} {'.'.join(name[1:])}"

    def model(groups):
        effort = next(iter(groups.values()))[0].get("effort", "")
        return f"{model_name(groups)}, {effort} effort"

    def count(n, word):
        return f"{n} {word}{'' if n == 1 else 's'}"

    runs_tok = sorted({r["runs"] for r in tok_rows})
    runs_tok = (count(runs_tok[0], "run") if len(runs_tok) == 1
                else f"{runs_tok[0]}–{runs_tok[-1]} runs")
    effort = next(iter(by_tok.values()))[0].get("effort", "")
    tok_sub = (f"{effort.capitalize()} effort · {count(len({r['paper'] for r in tok_rows}), 'paper')}, "
               f"{runs_tok} per setup and paper · lines are least-squares fits")
    plot_tokens(tok_rows, out / "tokens.svg", model_name(by_tok), tok_sub)
    if dev:
        runs_dev = max(d["runs"] for d in per_paper.values())
        effort = next(iter(by.values()))[0].get("effort", "")
        dev_sub = (f"{effort.capitalize()} effort · {count(len({p for _, p in per_paper}), 'paper')}, "
                   f"{runs_dev} fresh runs per setup on each · bars: mean over papers, error bars: ±1 SD")
        notes = {("layout", "skill"): a.skill_layout_note} if a.skill_layout_note else None
        plot_deviation(dev, out / "deviation.svg", model_name(by), dev_sub, notes)
    summary = {arm: {"papers": sum(r["arm"] == arm for r in tok_rows),
                     "tokens_mean": round(statistics.mean(
                         r["tokens_mean"] for r in tok_rows if r["arm"] == arm))}
               for arm in ARMS if any(r["arm"] == arm for r in tok_rows)}
    print(json.dumps({"tokens": summary, "deviation": dev}, indent=1))


if __name__ == "__main__":
    main()
