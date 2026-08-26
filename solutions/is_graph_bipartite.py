"""Is Graph Bipartite? — LeetCode 785."""

from __future__ import annotations

from collections import deque

META = {
    "pattern": "graph-traversal",
    "insight": "Bipartite means two-colourable; walk the graph colouring neighbours the opposite colour and fail on the first clash.",
    "time": "O(V + E)",
    "space": "O(V)",
    "sections": [
        (
            "What it asks",
            """
Given an undirected graph as an adjacency list, decide whether the nodes split
into two sets such that **every edge crosses between them**. Equivalently:
can you two-colour it?

Ask whether the graph is connected. The statement says it need not be, and
that single word is what most wrong answers ignore.
""",
        ),
        (
            "The insight",
            """
Bipartite ⟺ two-colourable ⟺ **no odd-length cycle**. You do not need to hunt
for cycles: colour as you traverse. Give the start colour 0, every neighbour
the opposite, and the moment you meet an already-coloured neighbour wearing
*your* colour, you have closed an odd cycle and the answer is False.

BFS or DFS, it makes no difference — every edge is examined twice, so O(V + E)
either way. BFS reads slightly better because "the opposite of my colour" is a
single expression per level, and it avoids a recursion depth of 10⁵ on a path
graph, which is a real stack overflow in Python.

`colours` doubles as the visited set. A separate `visited` set is redundant
state you will then have to keep in sync.
""",
        ),
        (
            "The disconnected-graph pitfall",
            """
The failure that costs the offer: colouring from node 0 only. If the graph has
several components, a triangle sitting in component two is never touched and
you return True.

The outer `for start in range(n)` loop with a `if colours[start] is not None:
continue` guard is the whole fix, and it costs nothing — the guard makes the
total work still O(V + E), not O(V·(V + E)).

Other cases to name: zero nodes and an isolated node are both **True**
(vacuously two-colourable); two components that are individually fine are
fine; and LeetCode guarantees no self-loops, which is worth confirming,
because a self-loop makes any graph non-bipartite immediately.
""",
        ),
    ],
}


def is_bipartite(graph: list[list[int]]) -> bool:
    colours: list[int | None] = [None] * len(graph)

    for start in range(len(graph)):
        if colours[start] is not None:
            continue  # already handled with its component

        colours[start] = 0
        queue: deque[int] = deque([start])

        while queue:
            node = queue.popleft()
            for neighbour in graph[node]:
                if colours[neighbour] is None:
                    colours[neighbour] = 1 - colours[node]
                    queue.append(neighbour)
                elif colours[neighbour] == colours[node]:
                    return False  # an odd cycle just closed

    return True


CASES = [
    (([[1, 2, 3], [0, 2], [0, 1, 3], [0, 2]],), False),
    (([[1, 3], [0, 2], [1, 3], [0, 2]],), True),
    (([[1, 2], [0, 2], [0, 1]],), False),  # triangle
    # Bipartite component first, odd cycle second — breaks a single-source scan.
    (([[1], [0], [3, 4], [2, 4], [2, 3]],), False),
    (([[1], [0], [3], [2]],), True),  # two clean components
    (([[], []],), True),  # isolated nodes
    (([[]],), True),
    (([],), True),
]


def solve(graph: list[list[int]]) -> bool:
    return is_bipartite(graph)
