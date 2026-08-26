"""Ternary Expression Parser — LeetCode 439."""

from __future__ import annotations

META = {
    "pattern": "stack",
    "insight": "The operator is right-associative, so scan right to left and every '?' already has both of its branches sitting on the stack.",
    "time": "O(n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
This one is premium, so the statement is not public — described here in my own
words. You are given a string holding a nested ternary expression built from
single-character atoms (`T`, `F`, and the digits `0`–`9`), the operator `?` and
the separator `:`, with no whitespace and no parentheses. Evaluate it and return
the resulting single character as a string. `T` is true, `F` is false, and only
a condition position is ever `T`/`F`-tested — a branch may itself be a digit,
a `T`/`F`, or another whole ternary.

The clarifying question is **associativity**, and it decides the problem:
`T?T?F:5:3` groups as `T?(T?F:5):3`, giving `F`. Grouping it the other way gives
`5`. Ternary is right-associative in every language that has it, and the input
is guaranteed valid — worth confirming both before writing anything.
""",
        ),
        (
            "The insight",
            """
The wrong first answer is to split on `:` or find the first `?` and cut. Both
die on nesting: in `F?1:T?4:5` the first `:` does not separate the two branches
of the first `?` at all.

Right-associativity means the **rightmost** `?` is the innermost expression —
the one whose branches are guaranteed to be plain atoms. Evaluate it first and
it collapses into a single atom, which is then a branch of the next `?` to its
left. That is a stack, scanned right to left:

- an atom → push it;
- `:` → skip, it carries no information once you are scanning this way;
- `?` → the top of the stack is the true branch and the one beneath it is the
  false branch (true was pushed later because it sits further left). The
  condition is the character immediately before the `?`, so read it, discard
  the losing branch, push the winner, and step the index back by **two** to
  consume the condition as well.

One pass, one atom left on the stack at the end. Scanning left to right instead
means recursive descent with an explicit "skip the branch I am not taking" walk,
which needs its own depth counter — the right-to-left scan gets the same result
with no bookkeeping at all.
""",
        ),
        (
            "Edge cases and the shape of the bugs",
            """
- **A bare atom.** `"T"` or `"5"` has no `?` at all; the loop pushes once and
  returns the single element. Do not special-case it, just do not index
  `stack[-2]` unconditionally.
- **`T` and `F` as values, not conditions.** `"T?F:1"` evaluates to `F`. Code
  that maps every `T`/`F` it sees to a boolean loses the answer.
- **Stepping the index.** On `?` the index must move back two, not one; moving
  by one re-reads the condition character as an atom and pushes it. This is the
  bug that shows up as an extra element left on the stack.
- **Which pop is which.** Swapping the two pops silently inverts the whole
  expression and still returns a plausible character, so it survives the sample
  and fails the nested case. Test with a nested input where the branches differ.

Multi-digit or multi-character atoms are the obvious follow-up: keep the same
scan but tokenise first, since a two-character atom breaks the "one index, one
atom" assumption everywhere.
""",
        ),
    ],
}


def parse_ternary(expression: str) -> str:
    stack: list[str] = []
    i = len(expression) - 1

    while i >= 0:
        char = expression[i]
        if char == ":":
            i -= 1  # separators carry nothing once scanning right to left
        elif char == "?":
            on_true = stack.pop()  # pushed later, so it is the left branch
            on_false = stack.pop()
            stack.append(on_true if expression[i - 1] == "T" else on_false)
            i -= 2  # skip the condition too
        else:
            stack.append(char)
            i -= 1

    return stack[-1]


CASES = [
    (("T?2:3",), "2"),
    (("F?1:T?4:5",), "4"),
    (("T?T?F:5:3",), "F"),  # right-associative: T?(T?F:5):3
    (("T?F?1:2:3",), "2"),  # nested in the true branch
    (("F?T?T?1:2:3:4",), "4"),  # three deep, condition short-circuits it all
    (("T?F:1",), "F"),  # F used as a value, not a condition
    (("F",), "F"),  # bare atom, no operator
    (("F?T:F",), "F"),
]


def solve(expression: str) -> str:
    return parse_ternary(expression)
