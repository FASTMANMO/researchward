# Tests

The handouts' worked examples are the expected answers. They live here and in each skill's `evals/` folder, never in the skill instructions, so a run can't copy the answer.

| Case | Skill | Input | Expected answer comes from |
|---|---|---|---|
| `dissect-backscatter-intro` | mcenerney-lens | the Section 6 introduction | Handout 1, Section 6, dissect table |
| `self-check-backscatter-intro` | mcenerney-lens | the Section 6 introduction | Handout 1, Section 6, self-check table |
| `self-check-version-a` | effective-writing | Version A and its reader card | Handout 2, Section 4, Version A column |
| `self-check-version-b` | effective-writing | Version B and its reader card | Handout 2, Section 4, Version B column (EW-3 PARTIAL, as settled) |
| `dissect-published-paragraph` | effective-writing | Version B, framed as someone else's | G6: describe, don't grade |
| `dissect-after-drift` | mcenerney-lens | the Section 6 introduction, after an earlier chat whose report drifted | the fixed format in SKILL.md, Section 5 |
| `combined-opening-flagged-once` | both | the Section 6 introduction | the scope lines: the opening is flagged once |

The first six sit in `skills/<skill>/evals/`; the combined case sits here in `tests/` because it needs both skills.

Each case folder holds `prompt.md` (run settings, then the prompt exactly as a user would type it), `case.yaml` (what a good result looks like), `graders/` (one checkable statement per file) and, when the case has an input file, `files/` and `place-files.sh`.

## Running them

- **Claude Code** (v2.1.269 or later): from a skill folder, run `claude plugin eval . --allow-tools Read --scaffold --trust-plugin --runs 3 --judge-model claude-sonnet-5-5`. The default judge model fails true statements too often to trust. It runs each case with and without the skill and reports pass rate, time and tokens. These are real, billed model runs.
- **By hand, in any assistant** (ChatGPT included): install the skill, open a fresh chat, paste the prompt and attach the input file if there is one, then check the reply against each statement in `graders/`.
- **Combined case:** install both skills, run it by hand in one conversation.

When a handout's worked example changes, update its case in the same pull request.

## Checking that the format holds

- **Late in a conversation:** `dissect-after-drift` hands the skill an earlier chat whose report drifted (field IDs, long cells, a verdict, extra sections) and checks that the next report follows the template anyway. By hand: dissect one paper, discuss it at length, then dissect another in the same chat and check the second report against the case's graders.
- **Same paper, many times:** run `dissect-backscatter-intro` five times, each in a fresh chat, and compare the reports row by row. Labels, row counts, locations and quotes should match; the wording of a cell may differ, since chat assistants don't produce identical text twice.

## Checking that the skills fire

`benchmarks/triggers.py` sends each prompt in `benchmarks/trigger_prompts.json` to a fresh session with both skills installed and nothing else, and records which skill the model calls first. The run stops at that call, so no report is written and a full pass takes about 15 minutes. The prompts come in four kinds: naming the skill, saying "McEnerney", everyday wording with neither, and near misses that should fire neither skill (a summary, a translation, a typo fix, a LaTeX table).

```
python3 benchmarks/triggers.py --paper short-paper.pdf --runs 5 --model claude-opus-5-5 claude-sonnet-5-5 claude-haiku-5-5
```

Results, 26 prompts × 5 runs × 3 models (Opus, Sonnet and Haiku 5.5, medium effort):

| Skills | Lens prompts | Effective-writing prompts | Neither | Wrong skill |
|---|---|---|---|---|
| mcenerney-lens 0.8.0 | 157 of 165 | 105 of 105 | 120 of 120 | 0 |
| mcenerney-lens 0.8.1 | 165 of 165 | 105 of 105 | 120 of 120 | 0 |
| mcenerney-lens 0.8.2, effective-writing 0.6.1 | 165 of 165 | 105 of 105 | 120 of 120 | 0 |

Under 0.8.0, two wordings missed: "is this paper worth reading closely? What does it offer me?" (Haiku, 1 of 5) and "this is my manuscript; review it before I submit it" (Sonnet and Haiku, 3 of 5). 0.8.1 adds both to the description, and every prompt then fired correctly on all three models. 0.8.2 and 0.6.1 shorten both descriptions; every prompt still fired correctly. Per-prompt counts are in `benchmarks/data/triggers.csv` (current version) and `triggers-lens-0.8.0.csv`. When a description changes, rerun the whole set, not only the prompts that missed, to catch new false fires.

## Results so far

Three runs per case, 9 Nov 2026, Opus 5.5 for the skills and Sonnet 5.5 as the judge. Layout, statuses and codes are checked by exact patterns; the judge only reads reasons and findings.

| Case | Runs passing every check |
|---|---|
| `dissect-backscatter-intro` | 3 of 3 |
| `self-check-backscatter-intro` | 3 of 3 |
| `dissect-after-drift` | 3 of 3 |
| `dissect-published-paragraph` | 3 of 3 |
| `self-check-version-a` | 3 of 3 (one judged check failed once; that check is now an exact pattern and passes all three reports) |
| `self-check-version-b` | 3 of 3 |
| `combined-opening-flagged-once` | 3 of 3 |

The last two lens and effective-writing cases were rerun after the final rule changes; the other five ran on the version just before them.

**10 Nov 2026, lens 0.8.5** (pitfalls table now reads Avoided / Present): the three lens cases, three runs each. Every pitfalls check passed in all nine runs, including after drift. `self-check-backscatter-intro` and `dissect-after-drift` passed 3 of 3. `dissect-backscatter-intro` passed every check in 1 of 3 runs. One miss was the test's fault: a row labeled "Community word and problem word", which the skill's rules allow, didn't match the pattern, which now accepts it. The two others are content calls missed once each, within the 2-of-3 bar: the stakes row (judged), and Figure 1 left uncited in one report.

Not yet done: cases from other fields, a whole paper rather than an introduction, and runs in ChatGPT.
