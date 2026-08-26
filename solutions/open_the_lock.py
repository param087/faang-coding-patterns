"""Open the Lock — LeetCode 752."""

from __future__ import annotations

from collections import deque

META = {
    "pattern": "graph-traversal",
    "insight": "It is not a puzzle, it is a 10000-node graph where each state has eight neighbours — plain BFS.",
    "time": "O(10⁴ · 8) — bounded by the state space, not the input",
    "space": "O(10⁴)",
    "sections": [
        (
            "What it asks",
            """
Four wheels, each `0`–`9` and wrapping both ways. Start at `"0000"`, reach
`target` in the fewest single-wheel clicks, never passing **through** a
deadend. Return −1 if it cannot be done.

The clarifying question that matters: is a deadend forbidden as a
*destination* only, or as any state you occupy? Any state — which means
`"0000"` itself being a deadend is an instant −1, before the loop starts.
""",
        ),
        (
            "The insight",
            """
Stop seeing a lock. The state space is every four-digit string: **10 000
nodes**, each with exactly 8 neighbours (4 wheels × 2 directions), every edge
costing 1. That is the definition of unweighted shortest path, so it is BFS
and nothing cleverer. Dijkstra here is a heap you do not need.

The whole thing fits: 10 000 states is small enough that you can enumerate
blindly, and the deadends are just nodes deleted from the graph. Seed
`visited` with the deadend set and there is no second membership test in the
inner loop — a deadend and an already-seen state are handled by the same
check.

Wrapping is `(d + 1) % 10` and `(d - 1) % 10`; Python's modulo makes the
second one work on `0 - 1` without a special case, which C++ answers usually
get wrong first time.
""",
        ),
        (
            "Edge cases, and the follow-up they ask next",
            """
- `target == "0000"` → **0**, and you must return it before doing any work.
- `"0000"` in `deadends` → **−1**, even if the target is `"0000"`.
- Target unreachable because it is walled in (all eight neighbours are
  deadends) → −1, which the queue draining naturally gives you.
- `deadends` can contain the target; then it is −1.

The follow-up is **bidirectional BFS**: expand from `"0000"` and from `target`
alternately, always the smaller frontier, and stop when they meet. Branching
factor 8 and diameter ~16 means each side only explores about `8^(d/2)`,
turning a worst case of 10 000 visited states into a few hundred. Say this;
with a fixed 10⁴ state space it is not needed, but it is the answer they want
when they raise the wheel count to eight and the space to 10⁸.
""",
        ),
    ],
}


def open_lock(deadends: list[str], target: str) -> int:
    visited = set(deadends)
    if "0000" in visited:
        return -1
    if target == "0000":
        return 0

    visited.add("0000")
    queue: deque[str] = deque(["0000"])
    turns = 0

    while queue:
        turns += 1
        for _ in range(len(queue)):  # one level == one click
            state = queue.popleft()
            for wheel in range(4):
                digit = int(state[wheel])
                for step in (1, -1):
                    nxt = f"{state[:wheel]}{(digit + step) % 10}{state[wheel + 1:]}"
                    if nxt in visited:  # seen, or a deadend seeded up front
                        continue
                    if nxt == target:
                        return turns
                    visited.add(nxt)
                    queue.append(nxt)

    return -1


CASES = [
    ((["0201", "0101", "0102", "1212", "2002"], "0202"), 6),
    ((["8888"], "0009"), 1),
    ((["8887", "8889", "8878", "8898", "8788", "8988", "7888", "9888"], "8888"), -1),
    (([], "0000"), 0),
    ((["0000"], "0000"), -1),  # start is a deadend beats target == start
    ((["0000"], "8888"), -1),
    (([], "9999"), 4),  # wrapping down beats nine clicks up, four times over
    ((["1234"], "1234"), -1),  # the target itself is blocked
]


def solve(deadends: list[str], target: str) -> int:
    return open_lock(deadends, target)
