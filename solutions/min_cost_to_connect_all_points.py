"""Min Cost to Connect All Points — LeetCode 1584."""

from __future__ import annotations

META = {
    "pattern": "minimum-spanning-tree",
    "insight": "The graph is complete, so never materialise the edges — dense Prim keeps one cheapest-link-to-the-tree number per point.",
    "time": "O(n²)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Given `n` points on the plane, connect all of them so any point is reachable
from any other, at minimum total cost, where the cost of joining two points is
their **Manhattan** distance `|x1-x2| + |y1-y2|`.

Two things are worth saying out loud before you write anything:

- The graph is **complete** — every pair is a legal edge. Nothing in the input
  restricts which points may connect, so this is a minimum spanning tree on an
  implicit dense graph, not a shortest-path problem.
- `n ≤ 1000`. That bound is the whole design brief: it says O(n²) is fine and
  that you should not be paying to build and sort ~500 000 edge tuples.
""",
        ),
        (
            "Brute force, and why it fails",
            """
"Try every spanning tree" is not a real option: Cayley's formula gives
`n^(n-2)` labelled spanning trees, so at n = 1000 that is 1000⁹⁹⁸.

The more interesting wrong answer is the greedy one people reach for first:
**connect each point to its nearest neighbour**. That gives a set of edges that
is neither a tree nor connected — on `[[0,0],[1,0],[5,0],[6,0]]` it links the
two left points and the two right points and stops, missing the bridge
entirely. Nearest-neighbour edges are a *subset* of the MST's candidates, not
the MST.

The honest brute force is Kruskal on the materialised edge list:
`n(n-1)/2 = 499 500` tuples at n = 1000, sorted — roughly 10⁷ comparisons and
tens of megabytes of Python tuples for an answer that a 10⁶-step array scan
gets for free.
""",
        ),
        (
            "The insight",
            """
Minimum spanning tree, and the cut property is the reason greedy works at all:
for any split of the points into "already in the tree" and "not yet", the
cheapest edge crossing that split is safe to take.

Prim's algorithm is exactly that statement turned into a loop. Maintain, for
every point still outside the tree, a single number — **the cost of its
cheapest edge into the tree so far**. Each round:

1. pick the outside point with the smallest such number, add it (that is the
   cheapest crossing edge);
2. now that the tree has grown by one point, relax every outside point against
   that one new point only.

Each round is two O(n) scans, n rounds, so O(n²) ≈ 10⁶ at the constraint — and
the only storage is two length-n arrays.
""",
        ),
        (
            "Dense Prim, not Kruskal — and why here",
            """
Kruskal is O(E log E) and Prim-with-a-heap is O(E log V). Both are better than
O(V²) on **sparse** graphs. This graph is not sparse: `E = Θ(n²)`, so those
become O(n² log n) and, worse, they force you to allocate all n²/2 edges.

Dense Prim drops the heap entirely. The "extract min" becomes a linear scan of
the `best` array, which is O(n) rather than O(log n) — but you were already
doing O(n) work per round in the relaxation step, so the scan is free. Same
asymptotics, no priority queue, no edge list, O(n) memory.

Rule of thumb worth stating in the interview: **heap Prim for sparse, array
Prim for dense, Kruskal when the edges are handed to you already**. This
problem hands you points, not edges, which is the tell.

One detail in the code: the running total adds `best[u]` at the moment `u` is
absorbed. Point 0 starts with `best[0] = 0`, so the first round contributes
nothing — that is the free choice of a root, not an off-by-one.
""",
        ),
        (
            "Dry run",
            """
`[[0,0],[2,2],[3,10],[5,2],[7,0]]`

Start with P0 absorbed, `best = [0, 4, 13, 7, 7]`.

- Cheapest outside is P1 at **4**. Total 4. Relax against P1:
  `best[2] = min(13, 9) = 9`, `best[3] = min(7, 3) = 3`, `best[4]` stays 7.
- Cheapest is P3 at **3**. Total 7. Relax: `best[4] = min(7, 4) = 4`,
  `best[2]` stays 9 (P3→P2 is 10).
- Cheapest is P4 at **4**. Total 11. Relax: P4→P2 is 14, no change.
- Last is P2 at **9**. Total **20**.

Note that P2's link changed owner twice — from P0 (13) to P1 (9) — and was
*not* its nearest neighbour at the moment it was added. That is precisely what
the nearest-neighbour greedy gets wrong.
""",
        ),
        (
            "Follow-ups",
            """
- **"Euclidean instead of Manhattan?"** The algorithm is unchanged (compare
  squared distances if you want to stay in integers, but remember to sum the
  real square roots). The *structure* changes though: the Euclidean MST is a
  subgraph of the Delaunay triangulation, which is O(n) edges — that is how you
  get O(n log n) for large n.
- **"n = 10⁵?"** O(n²) is 10¹⁰ and dead. For Manhattan there is a classic
  result: for each point only the nearest point in each of 8 angular octants can
  matter, giving O(n) candidate edges found by sweep line plus a BIT, then
  Kruskal — O(n log n). Knowing this exists is usually enough.
- **"One point must be a hub"** or "at most k edges per point" — the greedy
  breaks; degree-constrained MST is NP-hard in general.
- **Optimize Water Distribution** (1168) is the same MST with a virtual node,
  and **1135** is the same MST when the edges are given rather than implied.
""",
        ),
    ],
}


def min_cost_connect_points(points: list[list[int]]) -> int:
    n = len(points)
    if n <= 1:
        return 0

    in_tree = [False] * n
    # best[v] = cost of v's cheapest known edge into the tree. Coordinates are
    # bounded by 1e6, so any Manhattan distance is < 4e6 and this is a sentinel.
    best = [10**18] * n
    best[0] = 0  # arbitrary root, absorbed for free
    total = 0

    for _ in range(n):
        # Extract-min by linear scan: O(n), same cost as the relaxation below,
        # so a heap would buy nothing on a complete graph.
        u = -1
        for i in range(n):
            if not in_tree[i] and (u == -1 or best[i] < best[u]):
                u = i

        in_tree[u] = True
        total += best[u]

        # Only the newly absorbed point can improve anyone's cheapest link.
        ux, uy = points[u]
        for v in range(n):
            if not in_tree[v]:
                distance = abs(ux - points[v][0]) + abs(uy - points[v][1])
                if distance < best[v]:
                    best[v] = distance

    return total


CASES = [
    (([[0, 0], [2, 2], [3, 10], [5, 2], [7, 0]],), 20),
    (([[3, 12], [-2, 5], [-4, 1]],), 18),
    # Negative coordinates, and the cheapest pair is not adjacent in the input.
    (([[2, -3], [-17, -8], [13, 8], [-17, -15]],), 53),
    # Two clusters: nearest-neighbour greedy links each pair and never bridges.
    (([[0, 0], [1, 0], [5, 0], [6, 0]],), 6),
    (([[0, 0], [1, 1], [1, 0], [-1, 1]],), 4),
    # Duplicate points cost nothing to join.
    (([[0, 0], [0, 0], [3, 3]],), 6),
    (([[1, 1], [4, 5]],), 7),
    (([[0, 0]],), 0),
    (([],), 0),
]


def solve(points: list[list[int]]) -> int:
    return min_cost_connect_points(points)
