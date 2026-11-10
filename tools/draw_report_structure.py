#!/usr/bin/env python3
"""Draw docs/images/report-structure.svg: the layout of both reports, side by side.

The diagram follows the report templates in skills/mcenerney-lens/SKILL.md (section 5)
and skills/effective-writing/SKILL.md (section 6); field and criterion labels are copied
exactly. The statuses shown are illustrative. Redraw it whenever a template changes:
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
W, PAD, GAP = 1000, 24, 28
COL = (W - 2 * PAD - GAP) // 2          # panel width
IN = COL - 32                            # content width inside a panel
INK, MUTED, LINE, FILL, HEAD = "#1f2328", "#59636e", "#d1d9e0", "#f6f8fa", "#eef1f4"
STATUS = {"Met": "#2e7d32", "Partly met": "#a15c00", "Not met": "#c62828",
          "Does not apply": "#6b7280", "Avoided": "#2e7d32", "Present": "#c62828"}
FAMILY = "Helvetica, Arial, sans-serif"

out, problems = [], []


def width(s, size, bold=False):
    return ImageFont.truetype(FONTS.format("Bold" if bold else "Regular"), size).getlength(s)


def text(x, y, s, size=12, bold=False, color=INK, anchor="start", italic=False, room=None):
    if room is not None and width(s, size, bold) > room:
        problems.append(f"too wide ({width(s, size, bold):.0f} > {room:.0f}px): {s}")
    out.append(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FAMILY}" font-size="{size}" '
               f'font-weight="{"bold" if bold else "normal"}" fill="{color}" '
               f'text-anchor="{anchor}"{" font-style=\"italic\"" if italic else ""}>'
               f'{escape(s)}</text>')


def rect(x, y, w, h, fill="none", stroke=LINE, r=0, sw=1):
    out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{r}" '
               f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def chip(x, y, status):
    w = width(status, 10.5, True) + 16
    rect(x, y - 12, w, 17, fill=STATUS[status], stroke="none", r=8.5)
    text(x + w / 2, y + 1, status, 10.5, True, "#ffffff", "middle")


def heading(x, y, title, note=""):
    text(x, y, title, 13, True, room=IN * 0.62)
    if note:
        text(x + IN, y, note, 11, color=MUTED, anchor="end", room=IN * 0.38)
    return y + 10


def table(x, y, cols, rows, chip_col=None, shade=()):
    rh = 22
    rect(x, y, IN, rh, fill=HEAD)
    cx = x
    for h, cw in cols:
        text(cx + 8, y + 15, h, 11.5, True, MUTED, room=cw - 12)
        cx += cw
    y += rh
    for i, row in enumerate(rows):
        rect(x, y, IN, rh, fill=FILL if i in shade else "#ffffff")
        cx = x
        for j, (cell, (_, cw)) in enumerate(zip(row, cols)):
            if j == chip_col:
                chip(cx + 8, y + 15, cell)
            else:
                text(cx + 8, y + 15, cell, 11.5, color=INK if j == 0 else MUTED, room=cw - 12)
            cx += cw
        y += rh
    return y


def note(x, y, s):
    text(x, y, s, 10.5, color=MUTED, room=IN)
    return y


def lines(x, y, items, size=11.5, step=17):
    for s in items:
        text(x, y, s, size, color=MUTED, room=IN)
        y += step
    return y


def fixes(x, y, example):
    h = 104
    rect(x, y, IN, h, fill=FILL, stroke=LINE, r=6)
    text(x + 12, y + 21, "How to fix", 12.5, True)
    text(x + IN - 12, y + 21, "self-check only", 11, color=MUTED, anchor="end")
    lines(x + 12, y + 42, ["One line for each one not fully met, such as", example,
                           "Priority fix: the one that most limits value, and why",
                           "Untouched: numbers, results and technical claims"], 11.5, 16)
    return y + h


def panel(x, name, works_on, title, build):
    text(x, PAD + 20, name, 20, True)
    text(x + COL, PAD + 20, works_on, 13, color=MUTED, anchor="end")
    top = PAD + 34
    start = len(out)
    text(x + 16, top + 26, title, 13.5, True, room=IN)
    y = build(x + 16, top + 50)
    out.insert(start, f'<rect x="{x}" y="{top}" width="{COL}" height="{y - top + 16}" rx="8" '
                      f'fill="#ffffff" stroke="{LINE}" stroke-width="1.2"/>')
    return y + 16


def lens(x, y):
    y = lines(x, y, ["Text: title, venue, sections read",
                     "Readers: research community; wider readers"])
    y = heading(x, y + 12, "Main table", "10 rows (dissect), 12 (self-check)")
    fields = [("1- Readers", "Met"), ("2- Value words", "Met"),
              ("3- Value offered", "Partly met"), ("4- Problem", "Met"),
              ("5- Stance toward prior work", "Met"), ("6- Stakes", "Not met"),
              ("7- Doubts answered", "Partly met"), ("8- Contribution", "Met"),
              ("9- Structure", "Met"), ("10- Pitfalls", "Partly met"),
              ("11- Value words in the first two paragraphs", "Met"),
              ("12- Opening states the problem", "Partly met")]
    y = table(x, y, [("Field", 310), ("Met?", IN - 310)], fields, chip_col=1, shade=(10, 11))
    note(x, y + 15, "Each row also says what the paper does, with a quote and its location.")
    note(x, y + 30, "Dissect leaves out Met? and the shaded rows.")
    y = heading(x, y + 56, "2- Value words in context", "up to 10 rows")
    y = table(x, y, [("Kind", 112), ("Sentence, value word in bold", 176), ("Where", IN - 288)],
              [("Problem word", "“…is incomplete…”", "Section 1, paragraph 1"),
               ("Community word", "“Most practitioners…”", "Section 1, paragraph 1")])
    y = heading(x, y + 28, "Reusable frames", "up to 3")
    y = lines(x, y + 8, ["Sentence patterns to borrow, with the specifics as [slots]"])
    y = heading(x, y + 14, "10- Pitfalls", "4 checks")
    y = table(x, y, [("Pitfall", 300), ("Avoided?", IN - 300)],
              [("Background opening", "Avoided"),
               ("The writers' interest as the reason", "Avoided"),
               ("Originality as the value", "Avoided"),
               ("Results without consequence", "Present")], chip_col=1)
    note(x, y + 15, "Each present pitfall gets a quote and its location.")
    return fixes(x, y + 32, "“6- Stakes: say what the problem costs these readers.”")


def ew(x, y):
    y = lines(x, y, ["Reader card: readers · what they believe now · what they value ·",
                     "what they should think or do after reading · how they read"])
    y = heading(x, y + 12, "The paragraph", "one sentence per line")
    for s, w in (("S1", 300), ("S2", 370), ("S3", 250), ("S4", 330)):
        text(x, y + 14, s, 12, True)
        rect(x + 30, y + 5, w, 10, fill=HEAD, stroke="none", r=3)
        y += 22
    y = heading(x, y + 20, "Criteria table", "all 10 rows, both modes")
    rows = [("1- Opening gives readers a role", "Not met"),
            ("2- Names and challenges what readers believe", "Partly met"),
            ("3- Shows what is at stake for readers", "Not met"),
            ("4- Offers something readers can use", "Met"),
            ("5- Sentence subjects are what readers care about", "Partly met"),
            ("6- Sentence endings carry the key point", "Met"),
            ("7- Long sentences pay off early", "Does not apply"),
            ("8- No sentence needs a reread", "Met"),
            ("9- Nothing slows readers down", "Met"),
            ("10- Changes what readers think, not only shows knowledge", "Partly met")]
    y = table(x, y, [("Criterion", 324), ("Met?", IN - 324)], rows, chip_col=1)
    note(x, y + 15, "Each row also says what the paragraph does, citing S1, S2, …")
    note(x, y + 30, "Dissect, for someone else's paragraph: the same table, no fixes.")
    return fixes(x, y + 48, "“1- Opening gives readers a role: start S1 from their question.”")


def main():
    y1 = panel(PAD, "mcenerney-lens", "a whole paper",
               "McEnerney-lens report · Dissect or Self-check", lens)
    y2 = panel(PAD + COL + GAP, "effective-writing", "one paragraph",
               "Effective-writing report · Self-check or Dissect", ew)
    H = max(y1, y2) + 40
    text(W / 2, H - 16, "The same layout, in the same order, every time. "
         "Statuses here are examples.", 12, color=MUTED, anchor="middle", room=W - 2 * PAD)
    if problems:
        sys.exit("\n".join(problems))
    OUT.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H:.0f}" '
                   f'viewBox="0 0 {W} {H:.0f}">\n<rect width="{W}" height="{H:.0f}" '
                   f'fill="#ffffff"/>\n' + "\n".join(out) + "\n</svg>\n")
    print(f"wrote {OUT} ({W}x{H:.0f})")


if __name__ == "__main__":
    main()
