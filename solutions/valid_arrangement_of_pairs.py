"""Valid Arrangement of Pairs — LeetCode 2097."""

from __future__ import annotations

from collections import Counter, defaultdict

META = {
    "pattern": "advanced-graphs",
    "insight": "Chaining every pair end-to-start is an Eulerian path, and the start is the one node whose out-degree exceeds its in-degree.",
    "time": "O(e)",
    "space": "O(e)",
    "sections": [
        (
            "What it asks",
            """
Reorder the given `pairs` so that the second element of each equals the first
element of the next. A valid arrangement is guaranteed to exist; **any** valid
one is accepted.

Say the translation immediately: each pair `[u, v]` is a directed edge, and
chaining all of them end-to-start is an **Eulerian path** — every edge used
exactly once, vertices reused freely. The numbers are up to `10⁹` but there are
at most `10⁵` pairs, so the graph is a hash map keyed by the labels themselves;
do not allocate an array of size `10⁹`.

This is *Reconstruct Itinerary* (LC 332) with two differences: the start is not
handed to you, and there is no lexicographic tie-break to worry about.
""",
        ),
        (
            "The insight",
            """
**Finding the start is half the problem.** Track `out(x) − in(x)` for every
node while building the graph:

- exactly one node with `out − in = +1` → an Eulerian *path*, and that node is
  the only possible start;
- every node balanced at `0` → an Eulerian *circuit*, so start anywhere that
  has an outgoing edge.

Starting at `pairs[0][0]` "because it is first" is the wrong answer that looks
right on the samples: on `[[2,3],[1,2]]` it walks `2 → 3`, strands itself, and
leaves `[1,2]` unused. The correct start is 1.

**Then Hierholzer.** Walk greedily, consuming each edge as you take it. When a
node has no outgoing edges left, it is finished — append it to the output and
step back. Every skipped detour is a closed loop, and stepping back walks it,
splicing it into the route at the right place. Reverse the output at the end to
get the node sequence, then read consecutive nodes off as the pairs.

Because the input is promised valid, the only place you can get stranded is the
required endpoint, so no backtracking is ever needed and every edge is pushed
and popped once — **O(e)**.

Write it with an explicit stack: `e` reaches `10⁵` and recursive Hierholzer
overflows CPython's frame limit long before that.
""",
        ),
        (
            "Edge cases",
            """
- **Parallel edges are normal.** `[[1,2],[1,2],[2,1]]` has two copies of the
  same edge and both must appear. Anything set-based silently drops one.
- **Self-loops.** `[[7,7]]` is a one-pair answer; the walk visits 7, consumes
  its own edge, and finishes.
- **Node labels are values, not indices.** `defaultdict(list)` and a `Counter`
  of degrees, never a list of size `max(label)`.
- **Reverse at the end, not as you go.** The first node appended is the *last*
  node of the route. Forgetting the reversal yields a chain that is valid read
  backwards, which passes a hand-check and fails the judge.
- **Output shape.** The judge wants `e` pairs, so the reversed route of `e + 1`
  nodes turns into `[route[i], route[i+1]]` — an off-by-one here drops the final
  pair.
""",
        ),
    ],
}


def valid_arrangement(pairs: list[list[int]]) -> list[list[int]]:
    if not pairs:
        return []

    outgoing: defaultdict[int, list[int]] = defaultdict(list)
    balance: defaultdict[int, int] = defaultdict(int)  # out-degree − in-degree
    for source, destination in pairs:
        outgoing[source].append(destination)
        balance[source] += 1
        balance[destination] -= 1

    start = pairs[0][0]  # a circuit may start anywhere with an edge
    for node, difference in balance.items():
        if difference == 1:  # at most one such node, and it must go first
            start = node
            break

    route: list[int] = []
    stack = [start]
    while stack:
        while outgoing[stack[-1]]:
            stack.append(outgoing[stack[-1]].pop())
        route.append(stack.pop())  # no edges left here, so this node is done

    route.reverse()
    return [[route[i], route[i + 1]] for i in range(len(route) - 1)]


INPUTS = [
    [[5, 1], [4, 5], [11, 9], [9, 4]],
    [[1, 3], [3, 2], [2, 1]],
    # Start is forced: node 1 has out − in = 1.
    [[1, 2], [1, 3], [2, 1]],
    # pairs[0][0] is 2, but starting there strands the walk.
    [[2, 3], [1, 2]],
    # Duplicate edge: both copies must be used.
    [[1, 2], [1, 2], [2, 1]],
    # A circuit with a side loop that greedy order will leave for later.
    [[1, 2], [2, 3], [3, 1], [1, 4], [4, 1]],
    [[7, 7]],
    [[1, 2]],
]


def check() -> None:
    for pairs in INPUTS:
        original = [list(pair) for pair in pairs]
        arrangement = valid_arrangement(pairs)

        assert pairs == original, f"input mutated: {pairs} != {original}"
        assert len(arrangement) == len(pairs), (pairs, arrangement)
        assert Counter(map(tuple, arrangement)) == Counter(map(tuple, pairs)), (
            pairs,
            arrangement,
        )
        for before, after in zip(arrangement, arrangement[1:], strict=False):
            assert before[1] == after[0], (pairs, arrangement)

    assert valid_arrangement([]) == []
