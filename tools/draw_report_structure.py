#!/usr/bin/env python3
"""Draw docs/images/report-structure.svg: the layout of both reports, side by side.

The diagram follows the report templates in skills/mcenerney-lens/SKILL.md (section 5)
and skills/effective-writing/SKILL.md (section 6); field and criterion labels are copied
exactly. Statuses and sample text are illustrative. Redraw it whenever a template changes:
  python3 tools/draw_report_structure.py
The script measures every label with Liberation Sans (Arial's metrics) and stops if one
would not fit its space.
"""
import sys
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import ImageFont

OUT = Path(__file__).resolve().parents[1] / "docs/images/report-structure.svg"
FONTS = "/usr/share/fonts/truetype/liberation/LiberationSans-{}.ttf"
# Layout units; the SVG is drawn ZOOM times larger. Each panel is only as wide as its
# longest row needs, so the text is as large as the figure's width allows.
COL_LENS, COL_EW, PAD, GAP, ZOOM = 518, 584, 28, 40, 1.125
W = 2 * PAD + COL_LENS + GAP + COL_EW
COL = COL_LENS
INK, SOFT, RULE = "#1f2328", "#424a53", "#8c959f"
STATUS = {"Met": "#1a7f37", "Partly met": "#9a6700", "Not met": "#cf222e",
          "Does not apply": "#57606a", "Avoided": "#1a7f37", "Present": "#cf222e"}
FAMILY = "Helvetica, Arial, sans-serif"
RH = 21  # table row height

out, problems = [], []


def font(size, bold=False, italic=False):
    style = {(False, False): "Regular", (True, False): "Bold",
             (False, True): "Italic", (True, True): "BoldItalic"}[(bold, italic)]
    return ImageFont.truetype(FONTS.format(style), size)


def width(segs, size, italic=False):
    return sum(font(size, b, italic).getlength(s) for s, b in segs)


def text(x, y, segs, size=12, color=INK, anchor="start", italic=False, room=None, bold=False):
    """segs: a string, or a list of (text, bold) pieces for mixed weight."""
    if isinstance(segs, str):
        segs = [(segs, bold)]
    if room is not None and width(segs, size, italic) > room:
        problems.append(f"too wide ({width(segs, size, italic):.0f} > {room:.0f}px): "
                        + "".join(s for s, _ in segs))
    spans = "".join(f'<tspan font-weight="{"bold" if b else "normal"}">{escape(s)}</tspan>'
                    for s, b in segs)
    out.append(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FAMILY}" font-size="{size}" '
               f'fill="{color}" text-anchor="{anchor}"'
               f'{" font-style=\"italic\"" if italic else ""}>{spans}</text>')


def line(x1, y1, x2, y2, sw=1, color=INK, dash=None):
    out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" '
               f'stroke-width="{sw}"{f" stroke-dasharray=\"{dash}\"" if dash else ""}/>')


def fit(s, size, room):
    """Cut s with an ellipsis so it fits room."""
    if font(size).getlength(s) <= room:
        return s
    words = s.split()
    while font(size).getlength(" ".join(words) + " …") > room:
        words.pop()
    return " ".join(words).rstrip(",") + " …"


def heading(x, y, title):
    text(x, y, title, 14, bold=True, room=COL)
    return y + 12


def table(x, y, cols, rows, status_col=None, group=None):
    """Booktabs-style table. group: (row index, label) starts a labeled group of rows."""
    line(x, y, x + COL, y, 1.4)
    cx = x
    for h, cw in cols:
        text(cx + 2, y + 15, h, 12, bold=True, room=cw - 8)
        cx += cw
    y += 22
    line(x, y, x + COL, y, 0.7)
    for i, row in enumerate(rows):
        if group and i == group[0]:
            line(x, y + 1, x + COL, y + 1, 0.7, RULE, "3 3")
            text(x + 2, y + 16, group[1], 11.5, SOFT, italic=True)
            y += RH
        cx = x
        for j, (cell, (_, cw)) in enumerate(zip(row, cols)):
            if j == status_col:
                text(cx + 2, y + 15, cell, 12, STATUS[cell], bold=True, room=cw - 8)
            else:
                text(cx + 2, y + 15, cell, 12, room=cw - 8)
            cx += cw
        y += RH
    line(x, y + 4, x + COL, y + 4, 1.4)
    return y + 4


def fields(x, y, items):
    indent = 0
    for label, value in items:
        if label:
            indent = font(12.5, True).getlength(label + "  ")
            text(x, y, [(label + "  ", True), (value, False)], 12.5, room=COL)
        else:
            text(x + indent, y, value, 12.5, room=COL - indent)
        y += 19
    return y


def fixes(x, y, example):
    y = heading(x, y, "How to fix")
    for segs in ([(example, False)],
                 [("Priority fix: ", True), ("the gap that most limits value, and why", False)],
                 [("Untouched: ", True), ("numbers, results and technical claims", False)]):
        y += 19
        text(x, y, segs, 12.5, room=COL)
    return y


def title(x, y, name, sub):
    text(x, y, name, 22, bold=True)
    text(x, y + 22, sub, 13, SOFT, room=COL)
    line(x, y + 34, x + COL, y + 34, 1.2)
    return y + 62


def lens(x, y):
    y = title(x, y, "mcenerney-lens", "A whole paper · Dissect or Self-check")
    y = fields(x, y, [("Text", "title, venue, sections read"),
                      ("Readers", "the research community; wider readers")])
    y = heading(x, y + 16, "Main table")
    rows = [("1- Readers", "Met", "“…” (Section 1, paragraph 1)"),
            ("2- Value words", "Met", "See the table below"),
            ("3- Value offered", "Partly met", "“…” (Abstract)"),
            ("4- Problem", "Met", "“…” (Section 1, paragraph 2)"),
            ("5- Stance toward prior work", "Met", "“…” (Section 2, paragraph 3)"),
            ("6- Stakes", "Not met", "No cost to readers is stated"),
            ("7- Doubts answered", "Partly met", "“…” (Section 4, paragraph 2)"),
            ("8- Contribution", "Met", "“…” (Section 1, paragraph 4)"),
            ("9- Structure", "Met", "Section headings 1–5"),
            ("10- Pitfalls", "Partly met", "See the table below"),
            ("11- Value words in the first two paragraphs", "Met", "“…” (Section 1, paragraph 1)"),
            ("12- Opening states the problem", "Partly met", "“…” (Section 1, paragraph 1)")]
    y = table(x, y, [("Field", COL - 270), ("Met?", 76), ("What the paper does, and where", 194)],
              rows, status_col=1, group=(10, "Self-check only"))
    y = heading(x, y + 30, "2- Value words in context")
    vw = [(112, "Kind"), (COL - 306, "Sentence, value word in bold"), (194, "Where")]
    line(x, y, x + COL, y, 1.4)
    cx = x
    for cw, h in vw:
        text(cx + 2, y + 15, h, 12, bold=True, room=cw - 8)
        cx += cw
    y += 22
    line(x, y, x + COL, y, 0.7)
    for kind, segs, where in (("Problem word", [("“…the models are ", False), ("incomplete", True),
                                                ("…”", False)], "Section 1, paragraph 1"),
                              ("Community word", [("“", False), ("Most practitioners", True),
                                                  (" assume…”", False)], "Section 1, paragraph 1")):
        text(x + 2, y + 15, kind, 12)
        text(x + vw[0][0] + 2, y + 15, segs, 12, room=vw[1][0] - 8)
        text(x + vw[0][0] + vw[1][0] + 2, y + 15, where, 12, room=vw[2][0] - 4)
        y += RH
    line(x, y + 4, x + COL, y + 4, 1.4)
    y = heading(x, y + 34, "Reusable frames")
    y = fields(x, y + 7, [("e.g.", "[Approach] is standard for [task], but it [fails when …].")])
    y = heading(x, y + 14, "10- Pitfalls")
    y = table(x, y, [("Pitfall", COL - 270), ("Avoided?", 76), ("What the paper does, and where", 194)],
              [("Background opening", "Avoided", "–"),
               ("The writers' interest as the reason", "Avoided", "–"),
               ("Originality as the value", "Avoided", "–"),
               ("Results without consequence", "Present", "“…” (Section 4, paragraph 5)")],
              status_col=1)
    return fixes(x, y + 30, "6- Stakes: say what the problem costs these readers.")


PARAGRAPH = ["First sentence, exactly as written.",
             "Second sentence, exactly as written.",
             "Third sentence, exactly as written.",
             "… one line per sentence, to the end of the paragraph."]


def ew(x, y):
    y = title(x, y, "effective-writing", "One paragraph · Self-check or Dissect")
    y = fields(x, y, [("Reader card", "who reads · what they believe now · what they value"),
                      ("", "what they should think or do after · how they read")])
    y = heading(x, y + 16, "The paragraph")
    for i, s in enumerate(PARAGRAPH, 1):
        y += 19
        text(x, y, f"S{i}", 12.5, bold=True)
        text(x + 28, y, fit(s, 12.5, COL - 28), 12.5)
    y = heading(x, y + 30, "Criteria table")
    rows = [("1- Opening gives readers a role", "Not met", "S1 names a topic only"),
            ("2- Names and challenges what readers believe", "Partly met", "S2 implies the belief"),
            ("3- Shows what is at stake for readers", "Not met", "Nothing at risk in S1–S4"),
            ("4- Offers something readers can use", "Met", "S4: “…”"),
            ("5- Sentence subjects are what readers care about", "Partly met", "S2, S3: “this study”"),
            ("6- Sentence endings carry the key point", "Met", "S1–S4 end on content"),
            ("7- Long sentences pay off early", "Does not apply", "S1–S4 are short"),
            ("8- No sentence needs a reread", "Met", "S1–S4 read once"),
            ("9- Nothing slows readers down", "Met", "No friction in S1–S4"),
            ("10- Changes what readers think, not only shows knowledge", "Partly met",
             "S3 only reports")]
    y = table(x, y, [("Criterion", COL - 258), ("Met?", 104), ("What the paragraph does", 154)],
              rows, status_col=1)
    return fixes(x, y + 30, "1- Opening gives readers a role: start S1 from their question.")


def main():
    global COL
    COL = COL_LENS
    y1 = lens(PAD, PAD + 22)
    COL = COL_EW
    y2 = ew(PAD + COL_LENS + GAP, PAD + 22)
    mid = PAD + COL_LENS + GAP / 2
    line(mid, PAD + 6, mid, max(y1, y2), 0.7, "#d0d7de")
    y = max(y1, y2) + 34
    line(PAD, y - 16, W - PAD, y - 16, 0.7, "#d0d7de")
    caption = [
        [("Report layouts. ", True), ("Both skills return this layout, in this order, for every "
                                      "paper or paragraph; statuses and sample text are examples.", False)],
        [("Dissect mode leaves out How to fix; for mcenerney-lens it also leaves out the Met? column "
          "and rows 11–12.", False)]]
    for segs in caption:
        text(PAD, y, segs, 12.5, SOFT, room=W - 2 * PAD)
        y += 19
    H = y + PAD - 18
    if problems:
        sys.exit("\n".join(problems))
    OUT.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W * ZOOM:.0f}" '
                   f'height="{H * ZOOM:.0f}" '
                   f'viewBox="0 0 {W} {H:.0f}">\n<rect width="{W}" height="{H:.0f}" '
                   f'fill="#ffffff"/>\n' + "\n".join(out) + "\n</svg>\n")
    print(f"wrote {OUT} ({W * ZOOM:.0f}x{H * ZOOM:.0f})")


if __name__ == "__main__":
    main()
