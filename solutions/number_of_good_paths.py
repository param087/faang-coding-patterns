"""Number of Good Paths — LeetCode 2421."""

from __future__ import annotations

META = {
    "pattern": "advanced-graphs",
    "insight": "Add the edges in increasing order of their larger endpoint, and every component only ever contains paths whose maximum is already legal.",
    "time": "O(n log n) — the edge sort dominates the union-find",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
A tree with a value on each node. A path is **good** when its two endpoints
have the same value and no node on it exceeds that value. Count good paths;
single nodes count, and a path and its reverse are the same path.

So `n` single-node paths are free, and the real question is how many *pairs* of
equal-valued nodes see each other over a path whose maximum is that shared
value.

The brute force is to fix a pair and walk the path: `n` reaches `3 × 10⁴`, so
that is 4.5 × 10⁸ pairs before you have walked a single edge. Not viable.
""",
        ),
        (
            "The insight",
            """
Turn the constraint around. Instead of asking "is this path legal?", build the
graph so that **only legal paths exist**.

Sort the edges by `max(val[u], val[v])` and add them in that order. After you
have added every edge whose larger endpoint is `≤ t`, each connected component
contains exactly the nodes reachable using nodes of value `≤ t` — so *any* path
inside a component is automatically capped at `t`.

Then, at the moment an edge with threshold `t` merges two components, count the
good paths that edge creates. Only nodes whose value equals the component's
maximum can be endpoints at this threshold, so keep two numbers per component:

- `top_value` — the largest value in it;
- `top_count` — how many nodes hold that value.

If the two components' `top_value`s are equal, the merge creates
`top_count[a] × top_count[b]` new good paths — every pairing across the join,
and each is counted exactly once because two components merge exactly once.
If they differ, the smaller side's top nodes are now blocked by the larger
value and can never be endpoints again; the merged component simply inherits
the larger side's pair.

Union-find with path compression and union by size, plus one sort:
**O(n log n)**, and the counting is a single multiplication per merge.

The alternative framing — group nodes by value ascending, and for each value
union its nodes with all lower-valued neighbours before counting — is the same
algorithm; sorting edges by their larger endpoint is fewer moving parts.
""",
        ),
        (
            "Pitfalls",
            """
- **Count at merge time, not afterwards.** Sweeping components at the end and
  counting equal values inside them massively over-counts: by then the
  component holds nodes joined at every threshold, and pairs blocked by a
  higher-valued node in between get counted anyway.
- **Sort by the larger endpoint**, not by either endpoint's value on its own —
  the edge is only usable once *both* ends are permitted.
- **Duplicate values are the whole problem.** `vals = [1,1,1]` in a path gives
  6 (three singles plus three pairs). Any solution that treats values as unique
  answers 3.
- **A higher value in the middle blocks the path.** `vals = [1,2,1]` in a path
  answers 3, not 4 — the two 1s cannot see each other. This is the case to
  check first against any candidate solution.
- **The count grows fast.** `n` equal-valued nodes give `n(n−1)/2` paths, about
  4.5 × 10⁸ at `n = 3 × 10⁴`; fine in Python, an overflow question in C++/Java.
- Path compression alone is enough here in practice, but union by size keeps the
  bound honest, and the merged `top_value`/`top_count` must be written to the
  **surviving root**, whichever side that turns out to be.
""",
        ),
    ],
}


def number_of_good_paths(vals: list[int], edges: list[list[int]]) -> int:
    n = len(vals)
    parent = list(range(n))
    size = [1] * n
    top_value = list(vals)  # largest value in the component
    top_count = [1] * n  # how many nodes hold it

    def find(node: int) -> int:
        while parent[node] != node:
            parent[node] = parent[parent[node]]  # path halving
            node = parent[node]
        return node

    total = n  # every single node is a good path

    for u, v in sorted(edges, key=lambda edge: max(vals[edge[0]], vals[edge[1]])):
        root_u, root_v = find(u), find(v)
        if root_u == root_v:
            continue  # a tree never hits this; harmless on general graphs

        if top_value[root_u] == top_value[root_v]:
            total += top_count[root_u] * top_count[root_v]
            merged_value = top_value[root_u]
            merged_count = top_count[root_u] + top_count[root_v]
        elif top_value[root_u] > top_value[root_v]:
            merged_value, merged_count = top_value[root_u], top_count[root_u]
        else:
            merged_value, merged_count = top_value[root_v], top_count[root_v]

        if size[root_u] < size[root_v]:
            root_u, root_v = root_v, root_u
        parent[root_v] = root_u
        size[root_u] += size[root_v]
        top_value[root_u] = merged_value
        top_count[root_u] = merged_count

    return total


CASES = [
    (([1, 3, 2, 1, 3], [[0, 1], [0, 2], [2, 3], [2, 4]]), 6),
    (([1, 1, 2, 2, 3], [[0, 1], [1, 2], [2, 3], [2, 4]]), 7),
    (([1], []), 1),
    (([2, 2], [[0, 1]]), 3),
    # A larger value in the middle blocks the two 1s.
    (([1, 2, 1], [[0, 1], [1, 2]]), 3),
    # Every value equal: all three pairs are good.
    (([1, 1, 1], [[0, 1], [1, 2]]), 6),
    # Alternating 3,1,3,1,3 along a path: the three 3s all see each other.
    (([3, 1, 3, 1, 3], [[0, 1], [1, 2], [2, 3], [3, 4]]), 8),
    # A star whose centre is the maximum: the leaves never pair up.
    (([1, 5, 1, 1], [[1, 0], [1, 2], [1, 3]]), 4),
]


def solve(vals: list[int], edges: list[list[int]]) -> int:
    return number_of_good_paths(vals, edges)
