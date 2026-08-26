"""Remove All Adjacent Duplicates In String — LeetCode 1047."""

from __future__ import annotations

META = {
    "pattern": "stack",
    "insight": "Deleting a pair exposes a new pair, so the structure you need is one that re-examines the character you just uncovered — the stack top.",
    "time": "O(n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Repeatedly delete two adjacent equal letters until none remain, and return
what is left. The result is unique regardless of the order you delete in —
worth stating, because it is what licenses a single left-to-right pass.

Ask whether the alphabet is lowercase-only (it is) and how long the string can
get (10⁵, which rules out the obvious approach below).
""",
        ),
        (
            "The insight",
            """
The naive reading is literal: scan for an adjacent pair, delete it, start
over. Each deletion is an O(n) string rebuild and there can be n/2 of them, so
that is O(n²) — at n = 10⁵ roughly 5 × 10⁹ character copies. `s.replace(c+c, "")`
in a loop is the same shape and just as dead.

The fix is to notice what a deletion actually does: it makes the character
*before* the pair adjacent to the character *after* it. So the only position
that can newly become a match is the one you just uncovered — which is the top
of a stack of survivors.

Push each character unless it equals the top, in which case pop instead. The
cascade in `"abccba"` falls out with no rescanning: `c` cancels `c`, which
uncovers `b` for the incoming `b`, which uncovers `a` for the incoming `a`.

Every character is pushed once and popped at most once, so the whole thing is
one pass and `"".join(stack)` at the end.
""",
        ),
        (
            "Edge cases",
            """
- `""` → `""`. The `if stack and ...` guard is what stops an `IndexError` on
  the first character of any input.
- `"a"` → `"a"`; `"aa"` → `""`; `"aaaaa"` → `"a"`. Odd runs leave one behind,
  and a candidate who wrote "delete whole runs" instead of "delete pairs" gets
  `""` here.
- `"abccba"` → `""` is the cascade case, and the one that separates the stack
  from any single-pass filter over the original string.
- **Follow-up: Remove All Adjacent Duplicates II**, where you delete runs of
  exactly `k`. Same stack, but each entry becomes `(char, count)` and you pop
  when the count reaches `k` — the natural next question, so have the shape
  ready.
""",
        ),
    ],
}


def remove_duplicates(s: str) -> str:
    stack: list[str] = []

    for char in s:
        if stack and stack[-1] == char:
            stack.pop()  # the pop uncovers the only newly-adjacent pair
        else:
            stack.append(char)

    return "".join(stack)


CASES = [
    (("abbaca",), "ca"),
    (("azxxzy",), "ay"),
    (("abccba",), ""),  # a full cascade
    (("aaaaa",), "a"),  # odd run: pairs, not runs
    (("aa",), ""),
    (("a",), "a"),
    (("abcdef",), "abcdef"),
    (("",), ""),
]


def solve(s: str) -> str:
    return remove_duplicates(s)
