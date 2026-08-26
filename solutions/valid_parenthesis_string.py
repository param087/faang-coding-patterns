"""Valid Parenthesis String — LeetCode 678."""

from __future__ import annotations

META = {
    "pattern": "string-manipulation",
    "insight": "You cannot decide what a '*' is when you meet it, so carry the whole range of possible open-bracket counts instead.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
A string of `(`, `)` and `*`, where each `*` may stand for `(`, `)` or the
empty string. Is there **some** assignment that makes it a balanced sequence?

Ask whether `*` choices are independent (yes — each star decides for itself)
and whether the string can be empty (yes, and it is valid). Confirm there are
no other bracket types; with `[` and `{` in play the counter argument collapses
and you are back to a stack.
""",
        ),
        (
            "The insight",
            """
The brute force is exponential: three choices per star, `3^n`, so at n = 20
that is already `3.5 × 10⁹`. Backtracking with memo on `(index, open)` gets you
to `O(n²)`, which is a fine intermediate answer and worth saying out loud.

But you never need to *commit*. Scan left to right and track an **interval** of
how many brackets could be open right now:

- `low` — the count if every star so far were `)` or empty (the most closing
  interpretation);
- `high` — the count if every star so far were `(`.

`(` bumps both, `)` drops both, `*` drops `low` and lifts `high`. Every value
between `low` and `high` is achievable — the reachable set is a contiguous
range, because flipping one star's interpretation changes the count by exactly
one. That is why one interval suffices instead of a set.

Two checks close it out:

- if `high < 0`, there are more `)` than can ever be matched even with every
  star an opener — **fail immediately**;
- at the end, the string is valid iff `low == 0`, i.e. zero open brackets is
  one of the achievable counts.
""",
        ),
        (
            "The clamp is the whole problem",
            """
`low = max(low, 0)` after each character. Without it, a star counted as `)`
that had nothing to close drives `low` negative and permanently poisons the
final `low == 0` test.

Concretely, `"()*"`. Unclamped: `(` → `low = 1`, `)` → `low = 0`, `*` →
`low = -1`, and the answer comes out **false** even though the star can simply
be empty. Clamping says exactly that: a star we optimistically read as a
closer can always be re-read as empty instead, so `low` never needs to go below
zero.

Two more that separate a real solution from a remembered one:

- **`")("`** — balanced by count, invalid by order. Any solution that just
  compares totals gets this wrong. The `high < 0` early exit catches it.
- **`"(((("`** — no stars at all, `low` ends at 4, so `low == 0` fails.
  Returning `high == 0` instead of `low == 0` would wrongly accept `"*"`-heavy
  strings; the final test must be on `low`.

Follow-up: **return one valid assignment**, not just a yes/no. Now you need the
two-pass greedy — left to right treating stars as `(` to record which are
needed, then right to left — or a stack of star indices alongside a stack of
`(` indices.
""",
        ),
    ],
}


def check_valid_string(s: str) -> bool:
    low = high = 0  # tightest and loosest possible open-bracket counts

    for char in s:
        if char == "(":
            low += 1
            high += 1
        elif char == ")":
            low -= 1
            high -= 1
        else:  # '*': could close, could open, could vanish
            low -= 1
            high += 1

        if high < 0:
            return False  # more ')' than any reading can match

        low = max(low, 0)  # a star read as ')' can always be empty instead

    return low == 0  # zero open brackets is achievable


CASES = [
    (("",), True),
    (("*",), True),
    (("()",), True),
    (("()*",), True),
    (("(*))",), True),
    (("(*()",), True),
    ((")(",), False),
    ((")*(",), False),
    (("((((",), False),
]


def solve(s: str) -> bool:
    return check_valid_string(s)
