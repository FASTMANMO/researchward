---
type: regex
target: last_message
match: not_contains
flags: m
---

^\|\s*\d+- [^|\n]*\|[^|\n]*\|(?![^|\n]*\bS\d)[^|\n]*\|
