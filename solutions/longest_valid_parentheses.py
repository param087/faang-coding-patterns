"""Longest Valid Parentheses — LeetCode 32."""

from __future__ import annotations

META = {
    "pattern": "stack",
    "insight": "Keep the index of the last unmatched character on the stack; every valid run is measured from that barrier, not counted pair by pair.",
    "time": "O(n)",
    "space": "O(n), reducible to O(1)",
    "sections": [
        (
            "What it asks",
            """
Given a string of `(` and `)`, return the length of the longest **contiguous**
substring that is well formed.

The word doing the work is *contiguous*. Confirm it out loud, because the
obvious counting answer solves a different question.
""",
        ),
        (
            "The insight",
            """
The wrong first answer is to run the Valid Parentheses matcher and return
`2 × pairs matched`. On `"()(()"` that gives 4; the longest valid substring is
`"()"`, length **2**. Total matched characters is not the longest run — the runs
have to be separated by something.

What separates them is an **unmatched character**, and its position is exactly
what the stack should hold. Seed the stack with `-1` as a virtual barrier before
the string, then:

- `(` → push its index, a candidate barrier;
- `)` → pop. If the stack is now empty, this `)` matched nothing and *becomes*
  the new barrier: push its index. Otherwise everything from the new top+1
  through `i` is valid, so the run length is `i - stack[-1]`.

The subtraction is what makes this different from counting. It measures from the
last barrier, so adjacent valid blocks merge for free: in `"()()"`, the barrier
stays at `-1` and the second `)` reports `3 - (-1) = 4` without any extra logic
to join the two pairs.

Everything left on the stack at the end is unmatched by construction, so no
final pass is needed.
""",
        ),
        (
            "The base index, and the O(1)-space follow-up",
            """
The `-1` seed is the whole trick and the usual bug. Without it you need a
special case for "the valid run starts at index 0", and `"()"` reports 0 or
crashes on the pop. Two rules keep it straight: **the stack always holds the
index of the last unmatched character**, and it is **never empty after a step**
— a `)` that empties it immediately pushes itself back.

Note that the stack stores indices even for `(`, and those indices are used
purely as barriers. Storing characters loses the distance and there is no way
back.

**Follow-up: O(1) space.** Sweep left to right tracking `open` and `close`
counts. When they are equal, record `2 × close`; when `close > open`, reset
both to zero. Then sweep right to left with the reset condition flipped to
`open > close`. Two passes are needed because a single left-to-right sweep can
never resolve `"(()"` — the counters never come level, and nothing tells it the
prefix `(` is dead. That asymmetry is the point of the follow-up, and the reason
DP over `dp[i] = ` "longest valid run ending at `i`" is the third accepted
answer: it needs the `dp[i - dp[i - 1] - 2]` jump to handle nesting.
""",
        ),
    ],
}


def longest_valid_parentheses(s: str) -> int:
    best = 0
    stack = [-1]  # index of the last unmatched character

    for i, char in enumerate(s):
        if char == "(":
            stack.append(i)
            continue
        stack.pop()
        if not stack:
            stack.append(i)  # this ')' matched nothing; it is the new barrier
        else:
            best = max(best, i - stack[-1])

    return best


CASES = [
    (("(()",), 2),
    ((")()())",), 4),
    (("",), 0),
    (("()(()",), 2),  # 4 matched characters, but the longest run is 2
    (("()(())",), 6),  # adjacent blocks must merge
    (("()()",), 4),
    ((")))(((",), 0),
    (("(()))())(",), 4),
]


def solve(s: str) -> int:
    return longest_valid_parentheses(s)
