# Benchmark data

Everything the graphs are drawn from, so they can be redrawn or restyled without running anything again:

```
python3 analyze.py data/runs.jsonl --tokens-source tokens-12-papers --deviation-source variation-12-papers --out ../docs/images --csv data
```

The graph styling (colors, sizes, titles, the measures) lives in `analyze.py`; change it there and rerun the line above. The graphs go to `docs/images/`, which the README shows.

| File | What it holds |
|---|---|
| `runs.jsonl` | Every run in full: setup (`plain`, `skill`, `handout`), paper, pages, words, model, effort, token counts by kind, cost at list price, turns, seconds, tools and skills used, and report length. The report texts themselves are not published, because they quote the benchmark papers; `deviation.csv` holds the measures computed from them |
| `runs.csv` | The same runs, one row each, without the report text |
| `papers.csv` | The papers: file key, title, pages, words. The PDFs are not stored here |
| `tokens.csv` | The numbers in the tokens graph: mean tokens, output tokens and cost per setup and paper |
| `deviation.csv` | The numbers in the repeat-run graph, per setup and paper, with their mean and SD |
| `triggers.jsonl` | One line per trigger-test run: prompt, model, skill versions, which skill fired first (from `triggers.py`) |
| `triggers.csv`, `triggers-lens-0.8.0.csv` | Per-prompt fire counts for the current skills and for lens 0.8.0 |
| `judgments.jsonl` | One line per pair of repeat runs: the judge model's same / partly / different verdict on readers, problem, stakes and contribution (from `judge.py`) |

Each run records `source` (which batch it came from) and `skill_version` (the mcenerney-lens version and commit it used). `tokens_total` is input + cache writes + cache reads + output, summed over every turn of the run; cost is the CLI's list-price figure, not a bill.

Batches so far:

- `pilot-19p`: one run per setup on the 19-page *Composites Part B* paper (lens 0.6.0).
- `tokens-12-papers`: one run per setup on each of 12 papers, 7 to 25 pages (lens 0.7.0). Drawn in the tokens graph.
- `variation-12-papers`: five runs per setup on each of the 12 papers (lens 0.8.0). Drawn in the repeat-run graph; its pairs of runs are judged by `judge.py` (Sonnet 5.5, blind to the setup).

Judge new pairs with `python3 judge.py data/runs.jsonl --source variation-12-papers --out data/judgments.jsonl` (pairs already judged are skipped). Add a batch with `python3 collect.py <results.jsonl> --tag NAME --skill-version "mcenerney-lens X (commit)"`.
