"""Roman to Integer — LeetCode 13."""

from __future__ import annotations

META = {
    "pattern": "string-manipulation",
    "insight": "A symbol is subtracted exactly when it is smaller than the one on its right — one lookahead, no pair table.",
    "time": "O(n)",
    "space": "O(1) — a fixed 7-entry map",
    "sections": [
        (
            "What it asks",
            """
Parse a Roman numeral (guaranteed valid, 1–3999) into an integer.

The one clarifying question worth the breath: **is the input guaranteed
valid?** On LeetCode it is. If it is not, this becomes a different and much
longer problem — `IIX`, `VX` and `IC` are all rejectable, and the rules for
rejecting them are fiddlier than the parse itself.
""",
        ),
        (
            "The insight",
            """
The wrong first answer is a second dictionary of the six two-character pairs
(`IV`, `IX`, `XL`, `XC`, `CD`, `CM`), matching two characters when you can and
advancing `i += 2`. It works, but it is twice the code and the index arithmetic
is where the off-by-one lives.

Collapse all six pairs into one rule instead:

> add each symbol's value, but **subtract** it if the symbol to its right is
> larger.

`IV` becomes `-1 + 5`. `MCMXCIV` becomes `1000 - 100 + 1000 - 10 + 100 - 1 + 5`.
No pairs, no lookahead table, no variable stride — a single left-to-right pass
with one peek.

This works precisely because Roman numerals are otherwise written in descending
order, so "smaller before larger" is unambiguous evidence of a subtractive
form. Say that sentence; it is the whole justification.
""",
        ),
        (
            "Edge cases",
            """
- **The last character has no right neighbour**, so the `i + 1 < len(s)` guard
  is load-bearing. Reversing the scan and comparing against the *previous* value
  avoids the bounds check entirely — same idea, slightly slicker, worth
  mentioning as a variant.
- **Never two subtractions in a row.** `MCMXCIX` = 1999 is the case to run: it
  fires the subtractive rule three separate times.
- **A validating version is a different problem.** If asked, the cheap trick is
  to convert back with Integer to Roman and compare strings — round-tripping is
  a complete validity check because the canonical encoding is unique.
- Single character (`"I"`) and the maximum (`"MMMCMXCIX"`) are the two cheap
  boundary tests.
""",
        ),
    ],
}

VALUES = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}


def roman_to_int(s: str) -> int:
    total = 0
    for i, char in enumerate(s):
        value = VALUES[char]
        # Smaller before larger is the only way a subtractive pair can appear.
        if i + 1 < len(s) and value < VALUES[s[i + 1]]:
            total -= value
        else:
            total += value
    return total


CASES = [
    (("I",), 1),
    (("III",), 3),
    (("IV",), 4),
    (("IX",), 9),
    (("LVIII",), 58),
    (("MCMXCIV",), 1994),
    (("MCMXCIX",), 1999),
    (("MMMCMXCIX",), 3999),
]


def solve(s: str) -> int:
    return roman_to_int(s)
