"""Integer to English Words — LeetCode 273."""

from __future__ import annotations

META = {
    "pattern": "math-geometry",
    "insight": "English numerals repeat every three digits, so write one renderer for 0–999 and stitch the chunks with scale words.",
    "time": "O(d) in the digit count — at most 10 digits, so effectively O(1)",
    "space": "O(d) for the word list",
    "sections": [
        (
            "What it asks",
            """
Spell a non-negative 32-bit integer in English: `1234567` becomes
`"One Million Two Hundred Thirty Four Thousand Five Hundred Sixty Seven"`.

This is a **specification** problem, not an algorithm problem, so front-load
the clarifications and get them agreed before writing a line:

- Upper bound is 2³¹ − 1, so `"Billion"` is the largest scale you need. If they
  say "arbitrary precision", add `Trillion`, `Quadrillion` and keep going.
- No `"and"` (British usage would say "one hundred and five"; LeetCode does
  not), no hyphens (`"Twenty One"`, not `"Twenty-One"`), single spaces, no
  trailing space.
- Zero is the only input that produces `"Zero"` — it never appears inside a
  larger number.

Interviewers use this to watch you decompose a messy spec cleanly. Rushing
into string concatenation is how it goes wrong.
""",
        ),
        (
            "The insight",
            """
English numerals are **periodic with period three**. Every group of three
digits is read identically — "four hundred eighty three" — and then labelled
with a scale word that depends only on which group it is.

So the whole problem is one function over `0..999` plus a loop:

```
while num:
    num, chunk = divmod(num, 1000)
    if chunk: emit(three(chunk) + scale)
```

`three` itself is three cases and recurses at most twice: under 20 is a lookup
(the teens are irregular and no rule generates them), under 100 is a tens word
plus the remainder, otherwise a hundreds word plus the remainder.

Because the loop walks from the **least** significant group, collect the groups
and reverse at the end. That is cheaper to reason about than working out how
many groups there are up front.
""",
        ),
        (
            "The edge cases that fail people",
            """
- **Zero chunks.** `1_000_000` must not render `"One Million Zero Thousand"`,
  and `1_000_010` must be `"One Million Ten"` with the empty thousands group
  skipped entirely. The `if chunk:` guard is the whole fix, and every naive
  attempt at this problem is missing it.
- **Trailing whitespace.** Anything built with `result += words + " "` ends
  with a space and fails on a string comparison. Build a **list** and
  `" ".join` once — that also makes "no double spaces" free.
- **Zero itself.** `while num:` never runs for 0, returning `""`. Guard it as
  the first line.
- **Tens with a zero unit.** 20 is `"Twenty"`, not `"Twenty Zero"` — falls out
  of `three` returning `[]` for 0, which is why it returns a list rather than
  a string.
- **The upper bound.** `2147483647` exercises every branch at once; keep it as
  a test rather than trusting a walkthrough.
""",
        ),
    ],
}

BELOW_TWENTY = [
    "",
    "One",
    "Two",
    "Three",
    "Four",
    "Five",
    "Six",
    "Seven",
    "Eight",
    "Nine",
    "Ten",
    "Eleven",
    "Twelve",
    "Thirteen",
    "Fourteen",
    "Fifteen",
    "Sixteen",
    "Seventeen",
    "Eighteen",
    "Nineteen",
]

TENS = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]

SCALES = ["", "Thousand", "Million", "Billion"]


def _under_thousand(value: int) -> list[str]:
    """Words for 0 <= value < 1000. Returns [] for 0 so callers can splat it."""
    if value == 0:
        return []
    if value < 20:
        return [BELOW_TWENTY[value]]
    if value < 100:
        return [TENS[value // 10], *_under_thousand(value % 10)]
    return [BELOW_TWENTY[value // 100], "Hundred", *_under_thousand(value % 100)]


def number_to_words(num: int) -> str:
    if num == 0:
        return "Zero"

    groups: list[str] = []
    scale = 0
    while num:
        num, chunk = divmod(num, 1000)
        if chunk:  # skips "Zero Thousand" entirely
            words = _under_thousand(chunk)
            if SCALES[scale]:
                words.append(SCALES[scale])
            groups.append(" ".join(words))
        scale += 1

    return " ".join(reversed(groups))


CASES = [
    ((0,), "Zero"),
    ((20,), "Twenty"),
    ((123,), "One Hundred Twenty Three"),
    ((12345,), "Twelve Thousand Three Hundred Forty Five"),
    ((1000000,), "One Million"),
    ((1000010,), "One Million Ten"),
    (
        (1234567,),
        "One Million Two Hundred Thirty Four Thousand Five Hundred Sixty Seven",
    ),
    (
        (2147483647,),
        "Two Billion One Hundred Forty Seven Million "
        "Four Hundred Eighty Three Thousand Six Hundred Forty Seven",
    ),
]


def solve(num: int) -> str:
    return number_to_words(num)
