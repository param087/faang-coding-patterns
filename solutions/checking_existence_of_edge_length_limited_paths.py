"""Checking Existence of Edge Length Limited Paths — LeetCode 1697."""

from __future__ import annotations

META = {
    "pattern": "union-find",
    "insight": "Nothing says you must answer queries in order — sort them by limit, sort edges by weight, and sweep both once with a DSU that only grows.",
    "time": "O(E log E + Q log Q + (E + Q) · α(n))",
    "space": "O(n + Q)",
    "sections": [
        (
            "What it asks",
            """
An undirected weighted graph on `n` nodes, then queries `[p, q, limit]`: is
there a path from `p` to `q` using **only** edges of weight strictly less than
`limit`?

Ask three things, all of which change the code. Are there **parallel edges**
(yes — the same pair can appear several times at different weights, so you
cannot key edges by pair). Is the graph **connected** (no). And is the bound
strict — `< limit`, not `≤`. The graph is static and all queries are handed to
you up front, which is the permission slip for everything below.
""",
        ),
        (
            "The insight",
            """
Answering each query on its own means a BFS over the edges under that query's
limit: O(Q · (n + E)). At `Q = E = 10⁵` that is 10¹⁰ edge visits, and it also
redoes almost identical work for two queries whose limits differ by one.

The unlock is that you are given **all** the queries at once, so you may answer
them in whatever order suits you and permute the results back at the end. This
is the offline trick, and it is the whole question.

Sort queries by `limit` ascending, sort edges by weight ascending, and walk a
single pointer through the edges:

- before answering a query, union every edge with weight `< limit`;
- the answer is `find(p) == find(q)`.

The pointer never rewinds, because the limits only increase — an edge admitted
for one query stays admitted for every later one. So every edge is unioned
**once in total**, not once per query, and the sweep costs O(E + Q) after the
two sorts.

This is Kruskal's algorithm with the queries interleaved into it: the same
"process edges cheapest-first and let the DSU absorb them" skeleton, stopped at
a series of checkpoints.
""",
        ),
        (
            "The three traps",
            """
**Sorting the queries destroys the output order.** The result must line up
with the *input* query list, so sort an array of indices (or decorate each
query with its position) and write into `answers[original_index]`. Returning
the answers in sorted-limit order is the single most common way to fail this,
and the sample tests happen not to catch it because their queries are already
sorted — the case that catches it is `[[0,2,5],[0,1,2]]`.

**`<` versus `≤`.** An edge of weight exactly `limit` is not allowed. Getting
this wrong changes the answer only when a query's limit coincides with an edge
weight, which is a small fraction of tests, so it survives a casual check.

**Resetting the edge pointer per query.** If it is a local variable inside the
loop instead of outside it, the code is still correct but back to O(Q · E) —
and it will look right while timing out.

Two smaller notes: a node with no edges is simply never unioned, so
`find(p) == find(q)` is false for it without any special case; and there is no
point de-duplicating parallel edges, since the cheapest one is reached first
and the rest cost one no-op `union` each.

Follow-up worth naming: **"what if the queries arrive online?"** Then offline
sorting is unavailable and you build a Kruskal reconstruction tree, which turns
the question into "what is the maximum edge weight on the tree path between `p`
and `q`" — answerable in O(log n) with binary lifting.
""",
        ),
    ],
}


class UnionFind:
    def __init__(self, n: int) -> None:
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x: int) -> int:
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:  # path compression
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a: int, b: int) -> bool:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True


def distance_limited_paths_exist(
    n: int, edge_list: list[list[int]], queries: list[list[int]]
) -> list[bool]:
    edges = sorted(edge_list, key=lambda edge: edge[2])  # sorted(), not .sort()
    order = sorted(range(len(queries)), key=lambda i: queries[i][2])

    dsu = UnionFind(n)
    answers = [False] * len(queries)
    next_edge = 0  # outside the loop: each edge is consumed once in total

    for i in order:
        p, q, limit = queries[i]
        while next_edge < len(edges) and edges[next_edge][2] < limit:  # strict
            u, v, _ = edges[next_edge]
            dsu.union(u, v)
            next_edge += 1
        answers[i] = dsu.find(p) == dsu.find(q)  # back into the original slot

    return answers


CASES = [
    ((3, [[0, 1, 2], [1, 2, 4], [2, 0, 8], [1, 0, 16]], [[0, 1, 2], [0, 2, 5]]), [False, True]),
    ((5, [[0, 1, 10], [1, 2, 5], [2, 3, 9], [3, 4, 13]], [[0, 4, 14], [1, 4, 13]]), [True, False]),
    # Queries out of limit order — catches answering in sorted order.
    ((3, [[0, 1, 2], [1, 2, 4]], [[0, 2, 5], [0, 1, 2], [0, 1, 3]]), [True, False, True]),
    # limit == weight is excluded: strictly less than.
    ((2, [[0, 1, 5]], [[0, 1, 5], [0, 1, 6]]), [False, True]),
    # Parallel edges: the cheap one decides.
    ((3, [[0, 1, 10], [0, 1, 3], [1, 2, 4]], [[0, 2, 5], [0, 2, 4]]), [True, False]),
    # Isolated node 3, and a graph with no edges at all.
    ((4, [[0, 1, 1], [1, 2, 1]], [[0, 2, 2], [0, 3, 100]]), [True, False]),
    ((2, [], [[0, 1, 1000000]]), [False]),
]


def solve(n: int, edge_list: list[list[int]], queries: list[list[int]]) -> list[bool]:
    return distance_limited_paths_exist(n, edge_list, queries)
