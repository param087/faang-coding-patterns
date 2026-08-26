"""Longest Cycle in a Graph — LeetCode 2360."""

from __future__ import annotations

META = {
    "pattern": "advanced-graphs",
    "insight": "One outgoing edge per node means every walk ends in a cycle, so stamp each node with a visit time and subtract when you revisit.",
    "time": "O(n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
`edges[i]` is the single node that `i` points at, or `-1` for no outgoing edge.
Return the length of the longest cycle, or `-1` if there is none.

"At most one outgoing edge" is the entire problem statement. That makes this a
**functional graph**: from any node the future is a single deterministic walk —
a tail followed by a cycle, or a tail that dies at `-1`. There is no branching,
so there is no DFS tree, no recursion, and no backtracking. `n` reaches `10⁵`,
so recursion would be a liability anyway.

Worth confirming: `edges[i] == i` (a self-loop) is allowed and counts as a cycle
of length 1.
""",
        ),
        (
            "The insight",
            """
Because each node has one successor, every cycle is disjoint from every other
cycle, and the total work is bounded if — and only if — no node is ever walked
twice.

Give every node a **global visit timestamp** from a counter that never resets,
and remember the timestamp at which the current walk started. Walk forward
until you fall off the end (`-1`) or hit a node that already has a stamp. Then:

- stamp `>= start of this walk` → you have closed a loop **inside this walk**,
  and its length is `now − stamp[node]`, since timestamps increment once per
  step;
- stamp `< start of this walk` → you have merged into territory some earlier
  walk already covered. Its cycle, if any, was already measured. Stop.

That single comparison is what replaces the usual "visited" plus "on the current
stack" pair of sets, and it is why the whole thing is one pass and O(n) total:
each node is stamped once and never revisited.
""",
        ),
        (
            "The trap: one shared visited set",
            """
The wrong version uses a single boolean `visited` and computes the cycle length
by re-walking from the node where it stopped. Two ways that goes wrong:

- **Counting a cycle you did not enter.** `edges = [1, 2, 0, 0]`. The walk from
  0 finds the 3-cycle `0 → 1 → 2 → 0`. Then node 3 starts a fresh walk and
  immediately lands on node 0, which is visited — a naive "visited means cycle"
  test reports a bogus cycle, and a naive "re-walk from here" measures the same
  cycle a second time. The `stamp < start` test rejects it in O(1).
- **Quadratic blow-up.** Re-walking to measure the length turns a long tail
  feeding a long cycle into O(n) work per start node.

Other edges of the problem: `edges = [-1, -1, -1]` must return `-1`, not `0`;
`edges = [0]` is a self-loop of length 1; and a walk that runs off a `-1` must
not be counted at all. Watch the order of the terminating test — `node != -1`
has to be checked before indexing `stamp[node]`.
""",
        ),
    ],
}


def longest_cycle(edges: list[int]) -> int:
    n = len(edges)
    stamp = [0] * n  # 0 = never visited; otherwise the step it was seen at
    clock = 1
    best = -1

    for source in range(n):
        if stamp[source]:
            continue

        start = clock
        node = source
        while node != -1 and stamp[node] == 0:
            stamp[node] = clock
            clock += 1
            node = edges[node]

        # Stopped on a stamped node from *this* walk → that is a fresh cycle.
        if node != -1 and stamp[node] >= start:
            best = max(best, clock - stamp[node])

    return best


CASES = [
    (([3, 3, 4, 2, 3],), 3),
    (([2, -1, 3, 1],), -1),
    (([-1, -1, -1],), -1),
    # Self-loop.
    (([0],), 1),
    (([1, 0],), 2),
    # Two disjoint 3-cycles.
    (([1, 2, 0, 4, 5, 3],), 3),
    # A tail of length 3 feeding a 3-cycle: the tail must not be counted.
    (([1, 2, 3, 4, 5, 3],), 3),
    # A later walk merges into an earlier walk's cycle — must not re-count.
    (([1, 2, 0, 0],), 3),
]


def solve(edges: list[int]) -> int:
    return longest_cycle(edges)
