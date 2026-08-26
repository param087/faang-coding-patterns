"""Gas Station — LeetCode 134."""

from __future__ import annotations

META = {
    "pattern": "greedy",
    "insight": "If you run dry between start and i, no station in between works either — so the next candidate is i + 1.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Stations in a circle; station `i` gives `gas[i]` and costs `cost[i]` to reach
the next. Return the starting index that lets you complete the circuit, or −1.

Ask: is the answer guaranteed unique (yes); is the circuit clockwise (yes);
can individual differences be negative (yes — the totals are what matter).
""",
        ),
        (
            "Two independent facts",
            """
Stating them separately is what makes the one-pass solution obvious.

**1. If total gas < total cost, no start works.** Conservation of fuel — over
a full loop you consume the total cost and receive the total gas, so a deficit
is fatal regardless of where you begin.

**2. If you run dry partway from `start`, no station between `start` and the
failure point works either.** Each of those stations would begin the journey
with *even less* fuel in the tank than you had when you passed it, because you
arrived there with a non-negative balance. So the next candidate is the
station **after** the failure.
""",
        ),
        (
            "Why that makes it O(n)",
            """
Fact 2 is what turns the obvious O(n²) — try every start — into a single pass.
Every failure lets you skip an entire block of candidates at once rather than
retrying them one at a time.

Fact 1 is what guarantees the single surviving candidate actually works, so no
verification pass is needed.

**Interviewers want fact 2 articulated.** The code is six lines; the argument
is the answer.
""",
        ),
        (
            "Dry run",
            """
`gas = [1,2,3,4,5]`, `cost = [3,4,5,1,2]`. Totals are both 15, so an answer
exists.

Differences: `-2, -2, -2, 3, 3`.

- Start 0: tank −2 → fail at index 0. Restart at 1.
- Start 1: −2 → fail. Restart at 2.
- Start 2: −2 → fail. Restart at 3.
- Start 3: +3, +3 → survives to the end.

Answer **3**. Watch `start` jump forward rather than increment by retrying.
""",
        ),
        (
            "Follow-ups",
            """
- **Return every valid start** — the uniqueness guarantee is what makes the
  single-pass version work; without it you need a different approach.
- **Prove the answer is unique** when it exists: a good whiteboard exercise,
  and it follows from fact 2.
""",
        ),
    ],
}


def can_complete_circuit(gas: list[int], cost: list[int]) -> int:
    if sum(gas) < sum(cost):
        return -1  # fact 1: a global deficit means no start works

    start = 0
    tank = 0
    for i in range(len(gas)):
        tank += gas[i] - cost[i]
        if tank < 0:
            # fact 2: nothing from `start` through `i` can work either
            start = i + 1
            tank = 0

    return start


CASES = [
    (([1, 2, 3, 4, 5], [3, 4, 5, 1, 2]), 3),
    (([2, 3, 4], [3, 4, 3]), -1),
    (([5], [4]), 0),
    (([3, 1, 1], [1, 2, 2]), 0),
    (([1, 2], [2, 1]), 1),
]


def solve(gas: list[int], cost: list[int]) -> int:
    return can_complete_circuit(gas, cost)
