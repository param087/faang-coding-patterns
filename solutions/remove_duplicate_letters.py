"""Remove Duplicate Letters — LeetCode 316."""

from __future__ import annotations

META = {
    "pattern": "monotonic-stack",
    "insight": "Drop a stacked letter for a smaller one only when that letter reappears later; last-occurrence indices are what make the greed safe.",
    "time": "O(n)",
    "space": "O(1) — at most 26 letters on the stack",
    "sections": [
        (
            "What it asks",
            """
Keep exactly one copy of every distinct letter in the string, deleting the rest,
so that the result is the **lexicographically smallest** string achievable. The
surviving letters must stay in their original relative order — it is a
subsequence, not a sort. (Identical to Smallest Subsequence of Distinct
Characters, LeetCode 1081.)

Worth stating aloud: the output length is fixed — it is the number of distinct
letters — so the choice is purely *which occurrence* of each letter to keep.
""",
        ),
        (
            "The insight",
            """
Build the answer left to right on a stack that you try to keep increasing. When
letter `c` arrives and the stack top is larger than `c`, popping the top makes
the string smaller at the earliest differing position, which dominates
everything to its right.

But you may only pop a letter you can **get back**. Precompute each letter's
last index; if the top reappears later, dropping it now is free. If this is its
final occurrence, it is stuck, and the scan stops there.

```python
while stack and stack[-1] > c and last[stack[-1]] > i:
    seen.discard(stack.pop())
```

Every character is pushed and popped at most once: O(n), with a stack bounded
by 26.

Both fixed-occurrence heuristics fail on the same string, `cbacdcbc`, whose
answer is `acdb`: keeping each letter's **first** occurrence gives `cbad`, and
keeping each letter's **last** occurrence gives `adbc`. The choice is per
letter and depends on what else is still to come, which is why it has to be a
stack rather than a rule.
""",
        ),
        (
            "The two guards",
            """
Both conditions carry weight, and dropping either produces a solution that
passes the sample.

**The `in seen` skip.** If the letter is already on the stack, ignore this
occurrence entirely. Without it you emit duplicates. Note that `seen` must
track *what is on the stack right now*, so it has to be updated on every pop —
a `set` mirroring the stack, or a 26-slot boolean array.

**The `last[top] > i` guard.** Popping a letter whose final occurrence has
passed loses it forever. `bbcaac` is the case: at the `a` (index 3) you happily
pop `c`, because `c` returns at index 5, but you must **not** pop `b` — its last
copy was index 1. The answer is `bac`, and an implementation without the guard
returns `ac`, missing a letter.

Checking `last[...]` against the current index rather than a remaining-count
map is equivalent; counts just cost an extra decrement per character. Either is
fine, but keep only one of them — carrying both is how the off-by-one creeps in.
""",
        ),
    ],
}


def remove_duplicate_letters(s: str) -> str:
    last = {ch: i for i, ch in enumerate(s)}
    stack: list[str] = []
    on_stack: set[str] = set()

    for i, ch in enumerate(s):
        if ch in on_stack:  # this letter is already placed; a later copy adds nothing
            continue
        # Pop a bigger letter only if it reappears after i, so it can be re-added.
        while stack and stack[-1] > ch and last[stack[-1]] > i:
            on_stack.discard(stack.pop())
        stack.append(ch)
        on_stack.add(ch)

    return "".join(stack)


CASES = [
    (("bcabc",), "abc"),
    (("cbacdcbc",), "acdb"),
    # The last-occurrence guard: `b` cannot be popped, so the answer is not "ac".
    (("bbcaac",), "bac"),
    (("leetcode",), "letcod"),
    (("abacb",), "abc"),
    # Already decreasing and all distinct: nothing can move.
    (("edcba",), "edcba"),
    (("aaaa",), "a"),
    (("a",), "a"),
    (("",), ""),
]


def solve(s: str) -> str:
    return remove_duplicate_letters(s)
