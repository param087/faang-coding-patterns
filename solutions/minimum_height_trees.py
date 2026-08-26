"""Minimum Height Trees — LeetCode 310."""

from __future__ import annotations

META = {
    "pattern": "topological-sort",
    "insight": "Peel the leaves layer by layer; whatever survives when 2 or fewer nodes remain is the centre of the tree.",
    "time": "O(n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
An undirected tree on `n` nodes given as `n - 1` edges. Root it at each node in
turn; the resulting rooted tree has some height. Return **every** root that
achieves the minimum height.

Two clarifying questions that change the code:

- *Is the input guaranteed to be a tree?* Yes — connected and `n - 1` edges. No
  cycle handling, no forest handling.
- *How many answers can there be?* You should be able to answer this yourself:
  **at most two**, and saying so before you write anything signals you know the
  structure rather than having memorised the loop.
""",
        ),
        (
            "Brute force, and why it fails",
            """
BFS from every node and keep the roots with the smallest eccentricity. Each BFS
is O(n), so the whole thing is O(n²).

At n = 2·10⁴ that is 4·10⁸ edge relaxations in Python — comfortably over a
minute, and the constraint is deliberately sized so that it fails.

There is also a genuinely correct O(n) alternative: find the tree's **diameter**
with two BFS passes, then return the one or two nodes at its midpoint. It is a
fine answer, but it needs parent tracking and careful midpoint arithmetic for
odd versus even diameters. The leaf-peel below is shorter and harder to get
wrong under pressure.
""",
        ),
        (
            "The insight",
            """
The best root is never a leaf. Rooting at a leaf costs you the full distance
across the tree; stepping one node inward can only shrink the eccentricity of
the deepest branch.

So: strip all current leaves simultaneously. That removes one from the
eccentricity of everything that remains, and the *relative* ranking of the
survivors is unchanged. Repeat.

This is Kahn's algorithm with `degree == 1` instead of `indegree == 0` as the
frontier condition — a topological peel on an undirected graph. Each round is a
BFS level, and the process converges on the **centre** of the tree, which is by
a classical result either one node (odd diameter path) or two adjacent nodes
(even diameter path).

Stop when `remaining <= 2`. Whatever is still standing is the answer.
""",
        ),
        (
            "The detail that decides it",
            """
Two things sink people here:

1. **Peel by whole layers, not one node at a time.** If you pop a single leaf,
   decrement, and push, you will strip one long branch to the bone before
   touching the others and land on the wrong node. The `for leaf in leaves`
   loop building `next_leaves` is what enforces the simultaneous round.

2. **Count `remaining` explicitly.** The termination condition is about how many
   nodes are *left*, not how many leaves are in the current layer. A path of 4
   has 2 leaves at every stage; keying off `len(leaves)` never terminates
   correctly.

And the guard: `n <= 2` must return `[0]` or `[0, 1]` immediately. With `n == 1`
there are no edges and no node has degree 1, so the loop below would never
start; with `n == 2` both nodes are leaves and peeling them removes everything.

Adjacency as `set` rather than `list` is deliberate — `adjacency[neighbour]
.discard(leaf)` has to be O(1), and a list would make the peel O(n²) on a star.
""",
        ),
        (
            "Dry run",
            """
`n = 6`, edges `[[3,0],[3,1],[3,2],[3,4],[5,4]]`.

Degrees: 0→1, 1→1, 2→1, 3→4, 4→2, 5→1.

- Round 1: leaves `[0, 1, 2, 5]`. `remaining` 6 → 2. Removing 0, 1, 2 drops node
  3 to degree 1; removing 5 drops node 4 to degree 1. `next_leaves = [3, 4]`.
- `remaining == 2`, stop. Answer **`[3, 4]`** — the two ends of the middle edge
  of the diameter `0–3–4–5`.

Contrast a path of 7, `0–1–2–3–4–5–6`: three rounds peel `{0,6}`, `{1,5}`,
`{2,4}`, leaving the single centre **`[3]`**. Odd diameter, one answer.
""",
        ),
        (
            "Follow-ups",
            """
- **"What is the minimum height?"** Count the rounds. Each round removes one
  level, so the height is `rounds` when one centre survives and `rounds` again
  when two do — safest is to track the depth as you peel rather than derive it.
- **"Return the diameter too."** The two-BFS method gives it directly; the peel
  gives it as `2·rounds` or `2·rounds + 1` depending on whether one or two nodes
  survive.
- **The graph is a forest, not a tree.** Run the peel per component and report
  the centre of each; the `remaining <= 2` counter must then be per component.
- **Weighted edges.** The leaf peel breaks entirely — "one layer" is no longer
  "one unit of height". Fall back to computing the weighted diameter with two
  DFS passes and locating the point on it, which may sit *inside* an edge.
""",
        ),
    ],
}


def find_min_height_trees(n: int, edges: list[list[int]]) -> list[int]:
    if n <= 2:
        return list(range(n))

    adjacency: list[set[int]] = [set() for _ in range(n)]
    for u, v in edges:
        adjacency[u].add(v)
        adjacency[v].add(u)

    leaves = [node for node in range(n) if len(adjacency[node]) == 1]
    remaining = n

    while remaining > 2:
        remaining -= len(leaves)
        next_leaves: list[int] = []
        for leaf in leaves:  # a whole layer at once, never one node at a time
            neighbour = adjacency[leaf].pop()
            adjacency[neighbour].discard(leaf)
            if len(adjacency[neighbour]) == 1:
                next_leaves.append(neighbour)
        leaves = next_leaves

    return sorted(leaves)


CASES = [
    ((4, [[1, 0], [1, 2], [1, 3]]), [1]),
    ((6, [[3, 0], [3, 1], [3, 2], [3, 4], [5, 4]]), [3, 4]),
    ((1, []), [0]),
    ((2, [[0, 1]]), [0, 1]),
    ((3, [[0, 1], [1, 2]]), [1]),
    ((6, [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5]]), [2, 3]),
    ((7, [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 6]]), [3]),
    ((7, [[0, 1], [0, 2], [1, 3], [1, 4], [2, 5], [2, 6]]), [0]),
]


def solve(n: int, edges: list[list[int]]) -> list[int]:
    return find_min_height_trees(n, [list(edge) for edge in edges])
