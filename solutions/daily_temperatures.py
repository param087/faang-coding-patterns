"""Daily Temperatures — LeetCode 739."""

from __future__ import annotations

META = {
    "pattern": "monotonic-stack",
    "insight": "Rather than each day searching forward for a warmer one, each day answers everyone still waiting on it.",
    "time": "O(n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Given daily temperatures, return for each day how many days you must wait for
a warmer one. Zero if none comes.

Worth asking: are temperatures bounded? LeetCode says 30–100, which is a hint
that a 71-bucket approach exists — mention it, then write the stack.
""",
        ),
        (
            "Brute force, and why it fails",
            """
For each day, scan right until you find something warmer. O(n²), and at
n = 10⁵ that is 10¹⁰ operations.
""",
        ),
        (
            "The insight",
            """
When you reach day `i`, that day resolves **every** earlier day that was still
waiting for something warmer — and those days are exactly the ones sitting on
a stack in decreasing order of temperature.

So instead of each day searching forward, each day answers everyone waiting on
it. The stack holds indices whose answer is not yet known.

The `while` loop looks like it makes this quadratic. It does not: every index
is pushed exactly once and popped at most once, so across the whole scan the
inner loop runs at most n times in total. **Amortised O(n)** — say this out
loud, because interviewers ask.
""",
        ),
        (
            "Why indices, not values",
            """
The question asks for a **distance**, so you need to know where each waiting
day was. Storing temperatures instead of indices throws that away and you will
have to rewrite the loop.

This is the general rule for monotonic stacks: store indices unless you are
certain you will never need a position or a width.
""",
        ),
        (
            "Dry run",
            """
`[73, 74, 75, 71, 69, 72, 76, 73]`

- Push 73.
- 74 arrives, pops 73 → answer 1.
- 75 pops 74 → answer 1.
- 71 and 69 stack up behind 75.
- 72 pops 69 → answer 1, then pops 71 → answer 2.
- 76 pops 72, then pops 75 → **answer 4** for the day at index 2.

That last one is the case that catches anyone who stored values instead of
indices.
""",
        ),
        (
            "Follow-ups",
            """
- **"O(1) extra space?"** Not in general — but with the 30–100 bound you can
  walk a 71-element array of last-seen positions. That bound was in the
  problem for a reason.
- **Next Greater Element II**, where the array is circular: run the same loop
  over `2n` iterations using `i % n`, pushing only during the first pass.
""",
        ),
    ],
}


def daily_temperatures(temperatures: list[int]) -> list[int]:
    result = [0] * len(temperatures)
    stack: list[int] = []  # indices, temperatures decreasing bottom -> top

    for i, temperature in enumerate(temperatures):
        while stack and temperatures[stack[-1]] < temperature:
            previous = stack.pop()
            result[previous] = i - previous  # a distance, hence indices
        stack.append(i)

    return result  # anything left on the stack keeps its 0


CASES = [
    (([73, 74, 75, 71, 69, 72, 76, 73],), [1, 1, 4, 2, 1, 1, 0, 0]),
    (([30, 40, 50, 60],), [1, 1, 1, 0]),
    (([30, 60, 90],), [1, 1, 0]),
    (([90, 80, 70],), [0, 0, 0]),
    (([50, 50, 50],), [0, 0, 0]),
    (([],), []),
]


def solve(temperatures: list[int]) -> list[int]:
    return daily_temperatures(temperatures)
