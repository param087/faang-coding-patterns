"""Minimum Number of Vertices to Reach All Nodes — LeetCode 1557."""

from __future__ import annotations

META = {
    "pattern": "advanced-graphs",
    "insight": "A node with no incoming edge can only be reached by starting there, and in a DAG those sources already reach everything else.",
    "time": "O(n + e)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
A **directed acyclic** graph on `n` nodes. Return the smallest set of nodes
from which every node is reachable. The answer is guaranteed unique.

The word doing all the work is *acyclic*, and the first thing to say is that
you noticed it — because the answer is simply "every node with in-degree 0", no
traversal at all, and that is only true without cycles.

Uniqueness is also a hint worth reading aloud: minimum sets are usually not
unique, so being told this one is says the answer is forced rather than chosen.
""",
        ),
        (
            "The insight",
            """
Two halves, and an interviewer will want both.

**Necessary.** If node `v` has no incoming edge, nothing can ever walk into it,
so `v` must be in the set — no choice involved.

**Sufficient.** Take any node `u`. If it has an incoming edge, step backwards
along it; repeat. Each step moves to a different node because the graph is
acyclic and a repeat would close a cycle, and there are only `n` nodes, so the
walk must halt — and it can only halt at a node with in-degree 0. So every node
is reachable from some source, and the sources alone suffice.

That leaves nothing to compute but in-degrees: one pass over the edges marking
every destination, then collect the unmarked. The nodes you never see on the
right-hand side of an edge are the answer.

The instinct to run BFS from every candidate, or to greedily pick the node with
the largest reachable set, is `O(n · e)` and buys nothing here. Save that
reflex for the version below where the graph may have cycles.
""",
        ),
        (
            "When the DAG guarantee is removed",
            """
The whole argument rests on acyclicity, so the natural follow-up is "what if
there are cycles?" — and now the answer changes shape.

A cycle has no node of in-degree 0, yet you still have to pay to enter it. The
correct generalisation: **condense the graph into its strongly connected
components** (Tarjan or Kosaraju). The condensation is a DAG, so apply exactly
this rule to it, and pick any single node from each source component. The count
is the number of source SCCs; the set is no longer unique, which is precisely
why LeetCode had to promise a DAG to promise uniqueness.

Other things to have straight:

- Isolated nodes have in-degree 0 and are in the answer. `n = 3`, no edges →
  `[0, 1, 2]`.
- `n = 1` → `[0]`, never the empty list.
- Nothing about **out**-degree matters; counting the wrong end is the usual
  slip. A boolean `has_incoming` array is clearer than an integer count and
  makes that harder to get wrong.
- Order does not matter to the judge, but returning ascending indices is free.
""",
        ),
    ],
}


def find_smallest_set_of_vertices(n: int, edges: list[list[int]]) -> list[int]:
    has_incoming = [False] * n
    for _source, destination in edges:
        has_incoming[destination] = True

    return [node for node in range(n) if not has_incoming[node]]


CASES = [
    ((6, [[0, 1], [0, 2], [2, 5], [3, 4], [4, 2]]), [0, 3]),
    ((5, [[0, 1], [2, 1], [3, 1], [1, 4], [2, 4]]), [0, 2, 3]),
    # No edges: everybody is a source.
    ((3, []), [0, 1, 2]),
    ((1, []), [0]),
    # A single chain: one source reaches the lot.
    ((4, [[0, 1], [1, 2], [2, 3]]), [0]),
    # Two edges into the same node — counting destinations, not out-degrees.
    ((3, [[0, 1], [0, 2], [1, 2]]), [0]),
    # An isolated node alongside a chain.
    ((4, [[1, 2], [2, 3]]), [0, 1]),
]


def solve(n: int, edges: list[list[int]]) -> list[int]:
    return find_smallest_set_of_vertices(n, edges)
