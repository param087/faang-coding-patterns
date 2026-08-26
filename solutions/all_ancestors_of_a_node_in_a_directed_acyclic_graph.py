"""All Ancestors of a Node in a Directed Acyclic Graph — LeetCode 2192."""

from __future__ import annotations

from collections import deque

META = {
    "pattern": "topological-sort",
    "insight": "In topological order every node's ancestors are already final, so a child just unions its parents' sets plus the parents themselves.",
    "time": "O(V·E / word size) in practice — O(V + E·V) with hash sets",
    "space": "O(V²) worst case for the ancestor sets",
    "sections": [
        (
            "What it asks",
            """
`n` nodes labelled `0 .. n-1` and a list of directed edges forming a DAG. For
every node, return the sorted list of all nodes that can reach it.

"Ancestor" is transitive: `0 → 1 → 2` makes 0 an ancestor of 2, not just 1. The
answer for node `i` must be sorted ascending and free of duplicates, which
nudges you towards a set per node and one sort at the end.

Constraints are small on purpose: `n ≤ 1000`, `edges ≤ min(2000, n(n-1)/2)`. So
an O(n · (n + e)) answer — roughly 3·10⁶ — is fully acceptable, and saying that
out loud is better than reaching for bitsets nobody asked for.
""",
        ),
        (
            "The insight",
            """
Two shapes both pass, and it is worth naming both:

1. **Reverse DFS/BFS from every node.** Flip the edges, flood from `i`, collect
   what you reach. n floods × O(n + e) each. Dead simple, no ordering needed,
   and the one to write if you are short on time.

2. **One topological pass with set propagation** — the version below. Process
   nodes in Kahn order. When you pop `node`, its own ancestor set is already
   complete, because every predecessor was popped before it. So for each child:

   ```
   ancestors[child] |= ancestors[node]
   ancestors[child].add(node)
   ```

   Each edge does exactly one union. The topological order is what guarantees
   `ancestors[node]` is final at the moment you use it — that is the entire
   reason to sort rather than to recurse blindly.

The DAG guarantee is load-bearing. With a cycle, "ancestors are final when you
pop" is false and Kahn would not drain anyway.

If `n` were 10⁵ you would swap the sets for Python ints used as bitmasks:
`mask[child] |= mask[node] | (1 << node)`, which turns each union into one
machine-word-parallel operation and cuts the constant by ~64×. Mention it, do
not write it unless asked — extracting the set bits back out costs you the
readability you just bought.
""",
        ),
        (
            "Edge cases",
            """
- **Isolated nodes.** A node with no incoming edges gets `[]`, and it must still
  appear in the output at its index. Building `ancestors` as a length-`n` list
  up front rather than a dict keyed by nodes-seen is what guarantees that.
- **Duplicate edges.** `[[0,1],[0,1]]` raises `indegree[1]` to 2 and puts 1 in
  `adjacency[0]` twice; both decrements fire and the set union is idempotent, so
  the answer is unchanged. Nothing to special-case.
- **Diamonds** — `0→1, 0→2, 1→3, 2→3` — are the reason for a set and not a list.
  Node 0 arrives at node 3 along two paths and must be counted once.
- **Memory.** A dense DAG gives every late node an ancestor set of size ~n, so
  the sets total O(n²) = 10⁶ ints at the limit. Fine here, and the number to
  quote if asked why bitsets would help.
- **`n = 0` or no edges at all** — the queue seeds with everything, no unions
  happen, and every answer is `[]`.
""",
        ),
    ],
}


def get_ancestors(n: int, edges: list[list[int]]) -> list[list[int]]:
    adjacency: list[list[int]] = [[] for _ in range(n)]
    indegree = [0] * n

    for parent, child in edges:
        adjacency[parent].append(child)
        indegree[child] += 1

    ancestors: list[set[int]] = [set() for _ in range(n)]
    queue = deque(node for node in range(n) if indegree[node] == 0)

    while queue:
        node = queue.popleft()  # ancestors[node] is final now
        for child in adjacency[node]:
            ancestors[child] |= ancestors[node]
            ancestors[child].add(node)
            indegree[child] -= 1
            if indegree[child] == 0:
                queue.append(child)

    return [sorted(group) for group in ancestors]


CASES = [
    (
        (8, [[0, 3], [0, 4], [1, 3], [2, 4], [2, 7], [3, 5], [3, 6], [3, 7], [4, 6]]),
        [[], [], [], [0, 1], [0, 2], [0, 1, 3], [0, 1, 2, 3, 4], [0, 1, 2, 3]],
    ),
    (
        (
            5,
            [[0, 1], [0, 2], [0, 3], [0, 4], [1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]],
        ),
        [[], [0], [0, 1], [0, 1, 2], [0, 1, 2, 3]],
    ),
    ((1, []), [[]]),
    ((3, []), [[], [], []]),
    ((4, [[0, 1], [1, 2], [2, 3]]), [[], [0], [0, 1], [0, 1, 2]]),
    ((3, [[0, 1], [0, 1], [1, 2]]), [[], [0], [0, 1]]),
    ((4, [[0, 2], [1, 2], [2, 3]]), [[], [], [0, 1], [0, 1, 2]]),
    ((4, [[0, 1], [0, 2], [1, 3], [2, 3]]), [[], [0], [0], [0, 1, 2]]),
]


def solve(n: int, edges: list[list[int]]) -> list[list[int]]:
    return get_ancestors(n, [list(edge) for edge in edges])
