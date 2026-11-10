# Maintaining Researchward

Notes for whoever edits the skills and handouts. Not part of the skills.

## Keeping shared ideas in sync

The two handouts teach some ideas twice: once for a whole paper, once for a single paragraph. That duplication costs maintenance. If you change how one handout words a shared idea, such as costs and benefits, check its pair in the other handout and in both skills.

| Shared idea | Handout 1 · mcenerney-lens | Handout 2 · effective-writing |
|---|---|---|
| Costs and benefits (stakes) | M2, M10, L6 | EW-3 |
| Problem and the readers' belief | M3, M9, L4, L5 | EW-2 |
| Opening | M8, L12 | EW-1 |
| Contribution words | M1, L3, L8 | EW-4 |
| Explaining vs changing | M4, M7, L9 | EW-10 |
| Value and tension words | M1, M6, L2, L11 | EW-2 turn words, EW-3 tension words |
| Who the readers are | M2, L1 | the reader card, G1 |

Overlap map, written into both McEnerney skills: L12 ↔ EW-1 · L4, L5 ↔ EW-2 · L6 ↔ EW-3 · L8 ↔ EW-4.

**Rule: change one, check its pair.** The pull-request template asks for it. Also:

- IDs never change: L1–L12, M1–M10, R1–R6, EW-1–EW-10, P1–P7, G1–G6. New items are appended at the end. (Handout 1's fields were renumbered once, on 6 Nov 2026, before the repo went public.)
- A handout and its skill change in the same pull request, and the PDF is recompiled from `docs/handouts/`.
- The status lines (what counts as STRONG, PARTIAL or MISSING) are derived from the handouts and live only in the skills: `mcenerney-lens/references/self-check.md`, and the Status lines in `effective-writing/SKILL.md`. When you edit a criterion, check its status line too.
- The worked examples are the tests' expected answers. When one changes, update its test case.

## What loads, and when

| Moment | What the agent reads | About |
|---|---|---|
| Every session | each skill's name and description | 250 tokens per skill |
| Lens, dissect | `mcenerney-lens/SKILL.md`, plus the whole paper | 3,400 tokens + the paper |
| Lens, self-check | that, plus `references/self-check.md` | 4,800 tokens + the paper |
| Effective writing | `effective-writing/SKILL.md` | 3,500 tokens |

Each skill is read again for every report, so the report format can't drift. The handouts, worked examples and tests are never loaded during a run.

## Repository layout

```
researchward/
├── README.md
├── .github/pull_request_template.md
├── skills/
│   ├── mcenerney-lens/
│   │   ├── SKILL.md                  scope, modes, fields, rules, report
│   │   ├── references/self-check.md  status lines and M1–M10, self-check only
│   │   └── evals/                    tests (not uploaded)
│   └── effective-writing/
│       ├── SKILL.md                  scope, reader card, EW-1–EW-10, report
│       └── evals/                    tests (not uploaded)
├── tests/                            cross-skill test and how to run all tests
└── docs/
    ├── maintaining.md                this file
    └── handouts/                     both handouts, .tex source and PDF
```

`effective-writing` is a single file because every part of it is needed on every run; `mcenerney-lens` keeps its status lines in a separate file because dissect mode doesn't use them.

## Tests

Seven cases built from the handouts' worked examples, including one that runs both skills on one draft and checks the opening is flagged once, and one that checks the report format holds after a drifted earlier report. See [tests/README.md](../tests/README.md). When zipping a skill to upload, leave out its `evals/` folder: it holds the tests and their expected answers.

## Publishing

This repo (`researchward-dev`, private) holds the full history and work not yet released. The public repo, `FASTMANMO/researchward`, is built from `main` by `tools/export_public.py`:

```
python3 tools/export_public.py ../researchward      # a clone of the public repo
cd ../researchward && git diff --stat               # review, then commit and push
```

It copies every tracked file except the script itself, and drops the report texts from `benchmarks/data/runs.jsonl` (they quote the benchmark papers, which are copyrighted); every number stays. It stops if any file still mentions unreleased work.

## Releases

The README's Claude-app and ChatGPT install links point to the zip files of the latest GitHub release of the public repo. After changing a skill, build fresh zips (each holds the skill folder without `evals/`) and attach them to a new release:

```
cd skills
for s in mcenerney-lens effective-writing; do zip -q -r -X ../$s.zip $s -x "$s/evals/*"; done
gh release create vX.Y.Z ../mcenerney-lens.zip ../effective-writing.zip --repo FASTMANMO/researchward --title "Researchward X.Y.Z"
```

Bump the plugin `version` in `.claude-plugin/marketplace.json` at the same time, so Claude Code users get the update.
