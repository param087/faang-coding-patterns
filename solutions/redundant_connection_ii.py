"""Redundant Connection II — LeetCode 685."""

from __future__ import annotations

META = {
    "pattern": "union-find",
    "insight": "It can break two ways at once — a second parent and a cycle — so find the double parent, then let the DSU pick which edge to blame.",
    "time": "O(n · α(n))",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
A rooted tree on `n` nodes (every node has exactly one parent except the root,
and every node is reachable from the root) had **one extra directed edge**
added. Return the edge to remove so it is a rooted tree again; if several work,
return the one appearing last in the input.

Worth asking: is the extra edge guaranteed to make the result fixable by
removing exactly one edge (yes), and are nodes `1`-indexed (yes — size the
parent arrays `n + 1`). The clarifying question that actually matters:
**directed**, not undirected. If you answer this like LeetCode 684 you will be
wrong on roughly half the cases, and the interviewer is asking it precisely
because 684 is the well-known one.
""",
        ),
        (
            "The insight",
            """
Adding one directed edge `u → v` to a rooted tree breaks it in exactly one of
three ways, and each demands a different answer:

1. **`v` already had a parent, and no cycle formed.** Two edges point at `v`.
   Removing either would fix the in-degree, so the tie-break rule decides:
   return the **later** of the two.
2. **No node gained a second parent, so `u → v` closed a cycle** (it points at
   the old root, or back up its own ancestry). Return the edge that closes the
   cycle — this is 684 exactly.
3. **Both at once**: `v` has two parents *and* the graph contains a cycle. Now
   only one of `v`'s two incoming edges lies on the cycle, and only removing
   *that* one kills both defects. The tie-break does not apply; correctness does.

The algorithm is therefore two passes:

```
pass 1: scan edges, find any node with two parents
        -> record cand1 (the earlier edge into it), cand2 (the later one)
pass 2: DSU over all edges, SKIPPING cand2
        if some union fails (a cycle survived without cand2):
            return cand1 if cand1 else that edge
        else:
            return cand2
```

Why skipping `cand2` is the right probe: if removing `cand2` leaves a graph with
no cycle, `cand2` was the culprit (case 1). If a cycle survives without
`cand2`, then `cand2` was innocent and the cycle must run through `cand1`
(case 3), because in a valid input the only way both a double parent and a
cycle exist is for the cycle to use one of the two competing edges.
""",
        ),
        (
            "The pitfalls",
            """
- **Returning `cand1` whenever it exists.** That is case 3's answer applied to
  case 1, and it fails on `[[1,2],[1,3],[2,3]]`: node 3 has parents 1 and 2, no
  cycle, so the answer is the later edge `[2,3]`, not `[1,2]`.
- **Running plain 684 and hoping.** On `[[2,1],[3,1],[4,2],[1,4]]` an undirected
  DSU reports the cycle-closing edge `[1,4]`, but removing it leaves node 1
  with two parents — still not a tree. The right answer is `[2,1]`.
- **Recording the wrong pair.** When you meet the second edge into `v` during
  pass 1, `cand1` is `[parent[v], v]` (already stored) and `cand2` is the edge
  you are looking at right now. Getting these the wrong way round inverts cases
  1 and 3 simultaneously, which is hard to see from a single failing test.
- **Detecting the cycle with the *directed* DSU.** The DSU here is undirected —
  it detects an undirected cycle. With `cand2` excluded, every node has at most
  one parent, and an undirected cycle in a functional graph is a directed one,
  so it is sound. Say that; it is the step an interviewer will poke.
- **Off-by-one.** Nodes are `1..n` where `n == len(edges)`, so allocate `n + 1`
  slots. Iterate `edges` in the given order — the "last valid answer" rule is
  satisfied for free by processing in input order and never re-sorting.
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
        """False means they already shared a root — this edge closes a cycle."""
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True


def find_redundant_directed_connection(edges: list[list[int]]) -> list[int]:
    n = len(edges)
    parent = [0] * (n + 1)  # nodes are 1-indexed
    first_edge: list[int] | None = None  # cand1: the earlier edge into a double-parent node
    second_index = -1  # cand2: the index of the later one, so duplicates cannot confuse us

    for i, (u, v) in enumerate(edges):  # pass 1: does any node have two parents?
        if parent[v] != 0:
            first_edge = [parent[v], v]
            second_index = i
        else:
            parent[v] = u

    dsu = UnionFind(n + 1)  # pass 2: is there still a cycle without cand2?
    for i, (u, v) in enumerate(edges):
        if i == second_index:
            continue
        if not dsu.union(u, v):
            # A cycle survived. Blame cand1 if there is one, else this edge.
            return first_edge if first_edge is not None else [u, v]

    # No cycle once cand2 is gone, so cand2 was the whole problem.
    return list(edges[second_index]) if second_index >= 0 else []


CASES = [
    (([[1, 2], [1, 3], [2, 3]],), [2, 3]),  # double parent, no cycle -> later edge
    (([[1, 2], [2, 3], [3, 4], [4, 1], [1, 5]],), [4, 1]),  # pure cycle
    (([[2, 1], [3, 1], [4, 2], [1, 4]],), [2, 1]),  # both defects -> cand1
    (([[1, 2], [2, 3], [3, 1]],), [3, 1]),  # cycle with no root at all
    (([[4, 2], [1, 5], [5, 2], [5, 3], [2, 4]],), [4, 2]),  # both defects, cand1 again
    (([[2, 1], [3, 1], [4, 2], [1, 3]],), [3, 1]),  # both defects -> cand2 this time
    (([[1, 2], [2, 1]],), [2, 1]),  # two-node cycle
]


def solve(edges: list[list[int]]) -> list[int]:
    # edges is not mutated, but copy the rows so callers can reuse CASES safely.
    return find_redundant_directed_connection([list(edge) for edge in edges])
