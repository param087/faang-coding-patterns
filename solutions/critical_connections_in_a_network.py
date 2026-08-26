"""Critical Connections in a Network — LeetCode 1192."""

from __future__ import annotations

META = {
    "pattern": "advanced-graphs",
    "insight": "An edge is a bridge exactly when the subtree below it can reach nothing above it, and one DFS timestamp per node proves that.",
    "time": "O(n + e)",
    "space": "O(n + e)",
    "sections": [
        (
            "What it asks",
            """
`n` servers and undirected connections. Return every connection whose removal
disconnects some pair of servers. These are **bridges**; the standard answer is
Tarjan's bridge-finding algorithm.

Two questions to ask before writing anything:

- **Is the graph connected?** LeetCode says yes, but the code should not care —
  loop the DFS over every unvisited root and it handles a forest for free.
- **Can the same pair appear twice?** LeetCode says no. It matters more than it
  sounds: a duplicated edge is a 2-cycle, so *neither* copy is a bridge, and the
  usual "skip the parent node" trick reports both. See below.

Order of the output does not matter, and neither does the order within a pair.
""",
        ),
        (
            "Brute force, and why it fails",
            """
Remove one edge, run a DFS or a union-find over the rest, see whether the graph
is still connected, put the edge back. That is O(e · (n + e)).

With `n = 10⁵` and `e = 10⁵` that is about **2 × 10¹⁰ operations**. It is also
genuinely the right first thing to say out loud, because it defines "bridge"
operationally and buys you thirty seconds to reach for low-link.
""",
        ),
        (
            "The insight",
            """
Root a DFS anywhere. In an **undirected** graph, DFS produces only tree edges
and back edges — there are no cross edges, because a cross edge would have been
walked as a tree edge from the other end first. So every non-tree edge points
from a node up to one of its own ancestors.

Give each node two numbers:

- `disc[u]` — when the DFS first reached it.
- `low[u]` — the smallest `disc` reachable from `u`'s subtree using tree edges
  downward plus **at most one** back edge.

Then for a tree edge `(u, child)`:

```
low[child] > disc[u]   ⟺   (u, child) is a bridge
```

Read it as a sentence: nothing in the child's subtree can reach `u` or anything
above `u` other than by walking back through this very edge. Cut it, and that
subtree is stranded. Every bridge is a tree edge, and back edges are never
bridges — they always close a cycle.
""",
        ),
        (
            "Strictly greater, and disc not low",
            """
Two details decide whether this compiles into a correct answer:

**`>` not `>=`.** `low[child] == disc[u]` means the subtree has a back edge
landing exactly on `u`, so there is a cycle through the edge and it survives
removal. Using `>=` reports every edge of every cycle. (`>=` with a root
special case is the *articulation point* rule — a different question, and
conflating the two is the classic slip.)

**On a back edge take `disc[v]`, not `low[v]`.** For undirected bridges you can
usually get away with `low[v]`, but it is not the definition, and the same
reflex is outright wrong in Tarjan's SCC where a cross edge into an already
finished component must never lower your link value. Write `disc[v]` and you
never have to remember which algorithm you are in.
""",
        ),
        (
            "Parent edge, not parent node — and the stack",
            """
The DFS must ignore the edge it arrived on, and the wrong way to do that is
`if v == parent: continue`. With connections `[[0,1],[0,1]]` — two cables
between the same pair — that skips *both* copies, `low[1]` never sees `disc[0]`,
and the code reports two bridges where there are none. Skip by **edge index**
instead, and multi-edges are handled with no extra thought.

The second production detail: `n` goes to `10⁵`, so a recursive DFS blows
CPython's default 1000-frame limit, and raising `setrecursionlimit` to `10⁵`
trades a clean exception for a segfault. The loop below carries an explicit
stack of `(node, arriving edge, neighbour iterator)`. Keeping the *iterator* on
the stack is what makes it O(n + e) rather than re-scanning a node's neighbours
every time it resurfaces.
""",
        ),
        (
            "Dry run",
            """
`n = 4`, connections `[[0,1],[1,2],[2,0],[1,3]]`.

- `disc[0]=0` → `disc[1]=1` → `disc[2]=2`.
- From 2 the edge to 0 is a back edge: `low[2] = min(2, disc[0]) = 0`.
- 2 pops. `low[1] = min(1, 0) = 0`. Is `low[2]=0 > disc[1]=1`? No — 1–2 is on
  the triangle, not a bridge.
- 1 explores 3. `disc[3] = low[3] = 3`, nothing else to see.
- 3 pops. Is `low[3]=3 > disc[1]=1`? **Yes** → `[1,3]` is a bridge.
- 1 pops: `low[1]=0 > disc[0]=0`? No. Triangle intact.

Result `[[1,3]]`. Note how the triangle's three edges all fail the test for the
same reason and the single pendant edge passes.
""",
        ),
        (
            "Follow-ups",
            """
- **Articulation points** (vertices, not edges): same DFS, test
  `low[child] >= disc[u]`, and special-case the root — it is a cut vertex iff
  it has **two or more** DFS children.
- **"Which edges are safe to cut?"** — the complement: contract every
  2-edge-connected component into a node and the graph becomes the *bridge
  tree*, whose edges are exactly the bridges. Queries like "how many bridges
  lie on the path between u and v" become tree path queries.
- **Directed version** is not bridges at all — it is strongly connected
  components, Tarjan or Kosaraju, and the low-link comparison changes to
  `low[u] == disc[u]` at the root of a component.
- **Online updates** ("edges arrive over time") is dynamic connectivity — say
  link-cut trees or offline divide-and-conquer, and move on.
""",
        ),
    ],
}


def critical_connections(n: int, connections: list[list[int]]) -> list[list[int]]:
    adjacency: list[list[tuple[int, int]]] = [[] for _ in range(n)]
    for edge_id, (u, v) in enumerate(connections):
        adjacency[u].append((v, edge_id))
        adjacency[v].append((u, edge_id))

    disc = [-1] * n
    low = [0] * n
    bridges: list[list[int]] = []
    timer = 0

    for root in range(n):
        if disc[root] != -1:
            continue

        disc[root] = low[root] = timer
        timer += 1
        # (node, edge we arrived on, iterator over its remaining neighbours)
        stack = [(root, -1, iter(adjacency[root]))]

        while stack:
            node, arriving_edge, neighbours = stack[-1]
            descended = False

            for neighbour, edge_id in neighbours:
                if edge_id == arriving_edge:
                    continue  # by edge, so parallel edges still count
                if disc[neighbour] == -1:
                    disc[neighbour] = low[neighbour] = timer
                    timer += 1
                    stack.append((neighbour, edge_id, iter(adjacency[neighbour])))
                    descended = True
                    break
                low[node] = min(low[node], disc[neighbour])  # back edge: disc, not low

            if descended:
                continue

            stack.pop()
            if stack:
                parent = stack[-1][0]
                low[parent] = min(low[parent], low[node])
                if low[node] > disc[parent]:  # strictly greater
                    bridges.append([parent, node])

    return bridges


CASES = [
    ((4, [[0, 1], [1, 2], [2, 0], [1, 3]]), [[1, 3]]),
    ((2, [[0, 1]]), [[0, 1]]),
    # A triangle joined to a triangle by one cable.
    ((6, [[0, 1], [1, 2], [2, 0], [1, 3], [3, 4], [4, 5], [5, 3]]), [[1, 3]]),
    # Pure cycle: nothing is critical.
    ((4, [[0, 1], [1, 2], [2, 3], [3, 0]]), []),
    ((5, [[1, 0], [2, 0], [3, 2], [4, 2], [4, 3]]), [[0, 1], [0, 2]]),
    # A path: every edge is a bridge.
    ((3, [[0, 1], [1, 2]]), [[0, 1], [1, 2]]),
    # Disconnected input — both components must be walked.
    ((4, [[0, 1], [2, 3]]), [[0, 1], [2, 3]]),
    # Beyond LeetCode's constraints: two cables between the same pair are a
    # 2-cycle, so neither is critical. Fails if you skip by parent *node*.
    ((2, [[0, 1], [0, 1]]), []),
    ((1, []), []),
]


def solve(n: int, connections: list[list[int]]) -> list[list[int]]:
    # Any order is accepted; normalise so the cases can assert equality.
    return sorted(sorted(edge) for edge in critical_connections(n, connections))
