"""Remove Max Number of Edges to Keep Graph Fully Traversable — LeetCode 1579."""

from __future__ import annotations

META = {
    "pattern": "minimum-spanning-tree",
    "insight": "Shared edges are worth two edges each, so run Kruskal on both users at once with type-3 edges given priority over everything else.",
    "time": "O(E · α(N))",
    "space": "O(N)",
    "sections": [
        (
            "What it asks",
            """
An undirected graph on `n` nodes where each edge is type 1 (Alice only), type 2
(Bob only) or type 3 (both). Remove as many edges as possible while keeping the
graph fully traversable for **both** Alice and Bob independently — each must
still be able to reach every node from every node using the edges they can
walk. Return the maximum number removable, or `-1` if the graph is not fully
traversable to begin with.

Restating it as a minimisation is the first useful move: maximising removals
means **minimising the number of edges kept**, and the answer is
`len(edges) - kept`. Now it is a spanning-structure problem — you need Alice's
edges to contain a spanning tree and Bob's edges to contain a spanning tree,
sharing as much as possible.

Ask whether the graph may contain parallel edges (it may — including two
identical type-3 edges) and whether nodes are 1-indexed (they are).
""",
        ),
        (
            "The insight",
            """
This is Kruskal, but the "weight" is not a number in the input — it is how much
an edge is worth to you. A type-3 edge counts once towards the kept total but
contributes to *both* spanning trees; a type-1 or type-2 edge costs the same
one slot and helps only one user. So type-3 edges have weight 0 and the others
weight 1, and Kruskal says: **take every useful type-3 edge first**.

Concretely, run two DSUs — one for Alice, one for Bob — and make two passes:

1. **Type 3 first.** Union the endpoints in both DSUs. If either union actually
   merged something, the edge is kept; if neither did, both users already had
   that connection and the edge is free to delete.
2. **Then types 1 and 2**, each against its own DSU, keeping only the unions
   that merge.

Finally, if either DSU is not down to a single component, some node is
unreachable for that user and the answer is `-1`. Otherwise return
`len(edges) - kept`.

The greedy is safe for the usual exchange-argument reason: taking a type-3 edge
that merges two components can never be worse than taking the type-1 and type-2
edges that would otherwise be needed to merge those same components for each
user separately — it buys two merges for the price of one.
""",
        ),
        (
            "The ordering trap, and two smaller ones",
            """
**Order is the entire problem.** Process the edges in the given order in a
single pass and you will spend a type-1 edge joining two components, then find
a type-3 edge that would have joined them for both users, and end up keeping
one edge too many. The judge's first sample is built to catch exactly that. Two
passes, type 3 first, is not a micro-optimisation — it is the algorithm.

**Do not short-circuit the two unions.** Writing

```python
if alice.union(u, v) or bob.union(u, v):   # WRONG
```

skips Bob's union whenever Alice's succeeds, and the two DSUs silently diverge.
Evaluate both into variables first, then combine. (During the type-3 pass the
two DSUs are in identical states so the results always agree — but the code
should not depend on a reader noticing that.)

**Component counting with 1-indexed nodes.** A DSU sized `n + 1` starts with
`n + 1` components, and node 0 is never merged into anything, so "fully
connected" means `components == 2`, not `1`. Comparing against 1 makes every
input return `-1`.

Smaller edges worth mentioning: duplicate type-3 edges — the second one merges
nothing and is correctly counted as removable; and `n = 1`, where zero edges
are already fully traversable.
""",
        ),
    ],
}


class UnionFind:
    """DSU by rank with path compression, tracking live component count."""

    def __init__(self, size: int) -> None:
        self.parent = list(range(size))
        self.rank = [0] * size
        self.components = size

    def find(self, x: int) -> int:
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:  # path compression
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a: int, b: int) -> bool:
        """False means a and b were already connected — a removable edge."""
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        self.components -= 1
        return True


def max_num_edges_to_remove(n: int, edges: list[list[int]]) -> int:
    alice = UnionFind(n + 1)  # nodes are 1-indexed; slot 0 stays its own root
    bob = UnionFind(n + 1)
    kept = 0

    # Pass 1: shared edges are worth two merges for one slot, so take them all.
    for kind, u, v in edges:
        if kind == 3:
            merged_alice = alice.union(u, v)
            merged_bob = bob.union(u, v)  # never short-circuit this
            if merged_alice or merged_bob:
                kept += 1

    # Pass 2: private edges only fill in what the shared ones could not.
    for kind, u, v in edges:
        if kind == 3:
            continue
        owner = alice if kind == 1 else bob
        if owner.union(u, v):
            kept += 1

    # Node 0 is a permanent singleton, so a spanning graph leaves 2 components.
    if alice.components != 2 or bob.components != 2:
        return -1
    return len(edges) - kept


CASES = [
    ((4, [[3, 1, 2], [3, 2, 3], [1, 1, 3], [1, 2, 4], [1, 1, 2], [2, 3, 4]]), 2),
    ((4, [[3, 1, 2], [3, 2, 3], [1, 1, 4], [2, 1, 4]]), 0),
    # Bob can never reach node 1, so nothing is removable.
    ((4, [[3, 2, 3], [1, 1, 2], [2, 3, 4]]), -1),
    # Both private edges are needed; neither user has a shared alternative.
    ((2, [[1, 1, 2], [2, 1, 2]]), 0),
    # Duplicate shared edge: the second merges nothing.
    ((2, [[3, 1, 2], [3, 1, 2]]), 1),
    # Shared edges cover everything, so both private edges go.
    ((3, [[3, 1, 2], [3, 2, 3], [1, 1, 3], [2, 1, 3]]), 2),
    # A single node is trivially traversable.
    ((1, []), 0),
    # No shared edges at all: every edge in a private chain is load-bearing.
    ((4, [[1, 1, 2], [2, 1, 2], [1, 2, 3], [2, 2, 3], [1, 3, 4], [2, 3, 4]]), 0),
    # The private edge appears before the shared edge that replaces it.
    ((3, [[1, 1, 2], [2, 1, 2], [3, 1, 2], [3, 2, 3]]), 2),
]


def solve(n: int, edges: list[list[int]]) -> int:
    return max_num_edges_to_remove(n, edges)
