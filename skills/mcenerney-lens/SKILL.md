---
name: mcenerney-lens
description: "Reads a whole research paper, or a draft, through Larry McEnerney's reader-value lens (fields L1-L12): its readers, value words in context, the value it offers, the problem, its stance toward prior work, the stakes, the doubts it answers, its contribution, its structure and its pitfalls, each with an exact location in any section. Two modes: dissect someone else's paper (describes what it does, never grades it) or self-check your own draft (each field met, partly met or not met, with one fix). Use it whenever someone wants to dissect, break down, analyze or learn from a paper, asks whether a paper is worth reading closely or what problem, stakes or contribution it sets up, wants their own draft reviewed before submission or asks whether it makes readers care, or mentions McEnerney, value words, or the gap vs error model. Load it afresh for every paper, even later in a conversation. For sentence-level checks of one paragraph use effective-writing."
license: MIT
metadata:
  version: "0.8.5"
  author: "Mohammed Meligy, Mechanical and Aerospace Engineering, Arizona State University"
  source: "Handout 1, Expert Academic Writing Methods (docs/handouts in the repo)"
---

# McEnerney lens

Expert readers look for a problem in something they care about, what it costs them, and what the authors claim in response. Papers state these in the introduction, and often again, or more sharply, in later sections. This skill records those moves across a whole paper someone else wrote, or checks them in the user's own draft. It follows Handout 1, *Expert Academic Writing Methods*, compiled from McEnerney's lecture *The Craft of Writing Effectively*. Field IDs (L1–L12), method IDs (M1–M10) and rule IDs (R1–R6) are the handout's and never change.

## Scope

- **Covers:** the whole paper: readers, value, problem, stance, stakes, doubts, contribution, structure and pitfalls (L1–L12).
- **Leaves to effective-writing:** everything at sentence level: subjects, stress, payoff, rereads, friction, changing vs demonstrating (EW-5–EW-10). Don't comment on sentence craft.
- **Leaves out:** a venue's rules, voice and layout.
- **Shared with effective-writing, owned here at paper level:** L12 ↔ EW-1, L4 and L5 ↔ EW-2, L6 ↔ EW-3, L8 ↔ EW-4. When effective-writing runs on the same draft after this report, it marks EW-1–EW-4 for the opening paragraph "covered by lens" instead of flagging the opening again.

## 1. Choose the mode (R1)

- **DISSECT**: a paper the user is reading. Fields L1–L10. Record what the paper does, and where.
- **SELF-CHECK**: a draft the user is writing. Fields L1–L12. One status and at most one fix move per field.

If it is unclear whose text it is, ask once. If you can't ask, choose (the user calls it "my" paper or draft → SELF-CHECK; otherwise DISSECT); the report's header shows the choice.

## 2. Read the whole paper (R6)

- Read the abstract and introduction first, then every section through the conclusion. Fields L1–L10 cover the whole paper: record each finding wherever it is stated, and give every location it appears in.
- Skip the reference list, and skim long derivations, tables of numbers and appendices for statements of problem, value, stakes and doubts.
- If you can't read the file, ask for the paper as text. Never reconstruct a paper from memory or from its title.
- **Only part of a paper given** (for example, just the introduction): judge each field on what is there, say in the Text line which sections are missing, and never mark a field down for a missing section. A check that needs a missing section is left out of that field's verdict.
- **Locations (R2):** section, paragraph and the sentence's first words, so the user can search for it, written out in full: `Section 2, paragraph 3: "Existing EV and PT…"`. Use `Abstract` for the abstract, and figures and tables by number, as in `Figure 1`. Count paragraphs within their section. Where the user numbered the sentences, sentence numbers do.

## 3. Fill the fields, in order

| ID | Field | What to record |
|---|---|---|
| L1 | Readers | Two parts. Research community: whose understanding the paper sets out to change; there may be several, each with its own stake. Count the practitioners of each rival approach the paper discusses as part of the research community. Wider readers: only those the text names as users of the work, such as practitioners, engineers or policy makers; if it names none, write "not named". Plus the journal |
| L2 | Value words in context | Each value word quoted in its sentence, the word in **bold**, sorted as instability (however, nonetheless, inconsistent, problematic, anomaly, fail, cannot…) or community (widely, accepted, reported, most…). Flow words (because, and, if, unless) don't count; "gap" and "rarely" often signal a gap claim (M6). Bold every value word in the quoted sentence, not just one, and label the row with each kind it holds. Favor the sentences that carry the problem and stakes. Add a reusable frame (the sentence with the paper's specifics replaced by slots) for the best ones |
| L3 | Value offered | What the authors say readers gain overall, quoted. Quote what readers can do or gain with the contribution, not the contribution itself, which belongs to L8. A type label (verification, method, benchmark, correction, theory, practical use…) is an interpretation: mark it "(interpretation)" |
| L4 | Problem | Three parts, each with its location. Current state: what the community does or believes. Where it breaks: each approach or assumption, and how it fails. What remains open: the question the paper answers. Explicit or implicit |
| L5 | Stance toward prior work | Who the authors say got the problem wrong (the dominant view, rival approaches, the community itself), and how: directly (names the view and says it is wrong or incomplete) or deferentially (credits it first, then names its limit, M9). Saying what prior work addressed or achieved ("Two lines of work have addressed backscatter") counts as credit |
| L6 | Stakes | The cost of ignoring the problem and the benefit of solving it, as the text states them. Note whether the cost is stated as a cost to these readers (their predictions, results, decisions) or only as a fact about the world. Not knowing something is the problem (L4), not its cost; a cost names what goes wrong in the readers' own work. A cost stated as what the model or the physics does is a fact about the world, even when it is the readers' own model |
| L7 | Doubts answered | The doubts readers would raise about this paper's own claims (is the method valid, do the results hold, how far does it apply) that the text names, and where it answers them. Shortcomings of prior work belong to L5, not here |
| L8 | Contribution | What the paper offers in response to the problem: named as something readers can use (a tool, test, method) or only as an activity ("X is analyzed") |
| L9 | Structure | Whether the paper builds from instability (problem, then prior work that sharpens it, then contribution); whether explanation (definitions, background, method) comes only after value is established; whether the literature review builds the problem or lists who said what; error model or gap model (M5); whether the discussion and conclusion return to the problem |
| L10 | Pitfalls | Four checks, listed below. Each is reported as avoided, or present (quoted, with its location) |
| L11 | Value count | Self-check only: distinct value words in the first two paragraphs of the introduction |
| L12 | Opening | Self-check only: whether the first sentence states the problem the paper ended up solving. Check it against L4: if a later section states the problem more sharply, the opening should carry it |

A figure or table is a location, not a field: when one shows the problem, the stakes or the value (for example, the accepted view failing), cite it in that field's Where column, as in `Figure 1`.

**L10 checks.** Each comes from one of the handout's Common Pitfalls (in brackets):

1. **Background opening** (starting with background): the introduction's first paragraph has no instability word. Either way, give the location of the first one.
2. **The writers' interest as the reason** (starting with personal curiosity): a sentence gives the authors' interest or aim as the reason for the work ("we are interested in", "it is interesting to", "this study aims to explore") before the introduction states any problem.
3. **Originality as the value** (believing originality guarantees value): "novel", "new", "first", "for the first time" or "unique" is offered as the reason to read, and the same paragraph does not say what it changes for readers.
4. **Results without consequence** (writing to express your thoughts, not to change the readers'): a results, discussion or conclusion paragraph says what a figure, table or case shows, and neither it nor the next paragraph says what that changes for the problem (L4) or for the readers. List up to three, then "and n more". For an introduction alone, write "does not apply".

The handout's fourth pitfall, writing to preserve ideas, is a belief that doesn't show in a text, so it has no check.

**SELF-CHECK:** before giving statuses, read `references/self-check.md`. It holds the status line for each field and the methods (M1–M10) that fix moves name.

## 4. Rules

- **R2** Every finding cites a location, written so the user can find it.
- **R3** DISSECT describes; it never grades. "Not present" and "stated only in Section 5" are facts and may be reported. Statuses, verdicts, praise and advice may not.
- **R4** SELF-CHECK gives each field one status and at most one fix move, chosen from the method behind it (M1–M10) but written in plain words, and leaves numbers, results and technical claims untouched.
- **R5** At most one quoted sentence per finding, trimmed to about 25 words with "…".
- Keep the authors' hedging: "suggests" stays "suggests". Write "(not stated)" instead of guessing.

## 5. Report (fixed format)

The report has one format. It is the same for the first paper in a conversation and the hundredth, whatever was discussed in between, and the same each time a paper is given again.

**Every report, every time:**

1. Re-read this section before writing, even if this skill ran earlier in the conversation; invoke the skill again if its text is not in view. For a self-check, re-read `references/self-check.md` too.
2. Build the report from this template and the paper, never from an earlier report in the conversation. Earlier reports drift, and copying one carries its drift forward.
3. What was said in discussion (more detail, another emphasis, an extra section) applied to that reply only and does not carry into a later report.
4. Anything the user asks besides the report, such as an explanation, an opinion or a comparison with another paper, goes after the report below a horizontal rule, never inside it.
5. If the user asks to change the report itself, change that one report and add a line under the header: "Format changed at your request: …". The next report returns to this template.

**Plain words only.** A reader who has never seen the handout must be able to follow the report.

- No IDs or codes: no L1, M8, R2 or EW-1. Field labels are numbers and names.
- No abbreviations: write Section, paragraph and Figure in full; no "N/A".
- No handout terms without their meaning: say "shows that prior work is wrong or incomplete", not "error model"; "only says the topic hasn't been studied", not "gap model"; "opens on background before any problem", not "martini glass"; "problem words" and "community words", not "instability words".
- Statuses read Met, Partly met, Not met and Does not apply, never STRONG, PARTIAL, MISSING or N/A. In the pitfalls table, the Avoided? column reads Avoided, Present or Does not apply, never Found or Not found. Fixes are plain instructions, without method codes.

**Hard limits.** Count; don't estimate.

- Ordinary chat formatting (bold labels, Markdown tables), never a code block. Nothing before the header: no preamble and no summary of the paper.
- Field labels exactly as listed: 1- Readers, 2- Value words, 3- Value offered, 4- Problem, 5- Stance toward prior work, 6- Stakes, 7- Doubts answered, 8- Contribution, 9- Structure, 10- Pitfalls, 11- Value words in the first two paragraphs, 12- Opening states the problem.
- Main table: exactly 10 rows (Dissect) or 12 (Self-check), in that order.
- Each cell of "What the paper does": aim for about 45 words so no cell passes 60. "4- Problem": at most 40 words for each of its three parts. Each fix under "How to fix": at most 20 words.
- Value-words table: at most 10 rows; reusable frames: at most 3. Pitfalls table: exactly 4 rows, in the order of the checks.
- Each quote: one sentence, at most 25 words (R5). The Where column holds locations only (R2).

**Same paper, same report.** Pick findings by these rules, so repeat runs agree:

- Quote the first sentence, in reading order (abstract, then the sections in order), that states the finding in full; list the other places as locations without quoting them.
- Value-words rows: sentences that build the problem (4-) first, then the stakes (6-), then the rest, each group in reading order, up to ten. Frames come from the first rows that take slots.
- The value label (3-) is the first label that fits from the list in L3.
- Results without consequence: the first three paragraphs in reading order.

**Before sending, check:** the row counts, the labels, a status on every self-check row (rows 2 and 10 too), every cell's word count, a location on every finding, every figure that shows the problem or stakes cited in its row, no code or abbreviation, and nothing outside the template. Fix any miss first.

**DISSECT** — use this layout:

**McEnerney-lens report** · Dissect
**Text:** title, venue, sections read
**Readers:** research community; wider readers

| Field | What the paper does | Where |
|---|---|---|
| 1- Readers | … | Section 1, paragraph 1: "Most LES…" |
| 2- Value words | See the table below | |
| 3- Value offered | "…" Label (interpretation): … | … |
| 4- Problem | **Current state:** … **Where it breaks:** … **Open:** … | … |
| … | … | … |
| 10- Pitfalls | See the table below | |

**2- Value words in context**
Problem words (however, cannot, incomplete…) show that something is wrong or unsettled; community words (widely, accepted, most…) show that readers already care.

| Kind | Sentence (value word in bold) | Where |
|---|---|---|
| Problem word | "…this assumption is **incomplete**…" | Section 1, paragraph 1: "A priori tests…" |
| Community word | "**Most** LES practitioners close…" | Section 1, paragraph 1: "Most LES…" |

Then **Reusable frames** (sentence patterns to borrow, with the paper's specifics replaced by [slots]), each with its location.

**10- Pitfalls**

| Pitfall | Avoided? | What the paper does, and where |
|---|---|---|
| Background opening | Avoided | The first problem word, "**incomplete**", is in the first paragraph (Section 1, paragraph 1: "A priori tests…") |
| The writers' interest as the reason | Avoided | – |
| Originality as the value | Present | "…the **first** a posteriori test of…", and the paragraph does not say what it changes for readers (Section 1, paragraph 4: "We present…") |
| Results without consequence | Present | Two paragraphs describe a figure and stop (Section 4, paragraph 2: "Figure 6 shows…"; Section 4, paragraph 5: "As seen in…") |

**SELF-CHECK** — the same header and the same two tables, then:

| Field | Met? | What the paper does, and where |
|---|---|---|
| 1- Readers | Met | … (Section 1, paragraph 1: "…") |
| 2- Value words | Met | Problem words wherever the problem is built; see the table below |
| … | … | … |
| 10- Pitfalls | Met | All four avoided; see the table below |
| … | … | … |
| 12- Opening states the problem | Partly met | … |

**How to fix**
- 6- Stakes: say what the problem costs these readers in their own work.
- … one line for each field that is partly met or not met, in order.

**Priority fix:** the one field that most limits value, by number and name (as in "6- Stakes"), and why.
**Untouched:** numbers, results and technical claims are not changed.

If the user already asked for effective-writing, run it right after this report instead of offering it. Otherwise, after a self-check, add exactly one closing sentence offering effective-writing on the opening paragraph: it checks whether that paragraph's sentences keep readers reading, since this report already covers its opening, problem, stakes and contribution.
