"""Find the City With the Smallest Number of Neighbors at a Threshold Distance — LeetCode 1334."""

from __future__ import annotations

META = {
    "pattern": "shortest-paths",
    "insight": "You need every pair's distance, not one source's — n ≤ 100 makes Floyd–Warshall's n³ = 10⁶ the shortest thing to write.",
    "time": "O(n³)",
    "space": "O(n²)",
    "sections": [
        (
            "What it asks",
            """
Weighted undirected graph. For each city, count how many other cities lie
within `distanceThreshold` by shortest path; return the city with the smallest
count, breaking ties towards the **largest index**.

Ask about the tie-break — it is stated in the problem and it is the part people
skip. Ask whether weights are non-negative (yes) and whether the graph is
connected (no, it need not be, so unreachable pairs must stay at infinity).
""",
        ),
        (
            "The insight",
            """
This is all-pairs, not single-source. `n ≤ 100`, so **Floyd–Warshall** at
100³ = 10⁶ operations is instant and takes six lines.

The loop order is the entire algorithm and it is the thing to get right: `k`
**outermost**. The invariant is "after iteration `k`, `dist[i][j]` is the best
path from `i` to `j` using only `0..k` as intermediates". Put `k` innermost and
you get a plausible-looking triple loop that computes something else entirely
and passes small tests.

The alternative is Dijkstra from every node: O(n · E log n), which is genuinely
faster on a sparse graph — `E` can be as low as `n − 1` here, giving about
100 × 100 × 7 ≈ 7 × 10⁴. Say that. Then write Floyd–Warshall anyway, because at
this `n` the constant factor is irrelevant and the code has no heap, no
adjacency list and no stale-entry guard to get wrong.

The tie-break falls out of `<=` in the final scan: iterate cities in increasing
order and accept a count that merely *ties* the best, so the last (largest)
index wins.
""",
        ),
        (
            "Edge cases",
            """
- **Do not count the city itself.** `dist[i][i] = 0 ≤ threshold` always, so the
  count is off by one everywhere if you forget `j != i`. It shifts every city
  equally, so the answer still often comes out right — which is exactly what
  makes it survive a casual test.
- **Unreachable pairs** must stay at infinity. Initialise off-diagonal entries
  to infinity, not to 0 and not to some large integer you might later add to
  another large integer.
- **No edges at all** → every count is 0, so the answer is `n - 1` by the
  tie-break.
- **Parallel edges**: keep `min` when seeding the matrix. LeetCode's constraints
  forbid duplicates, but the `min` costs nothing and the interviewer may not.
- **The threshold can exceed every path**, in which case counts are just
  component sizes minus one.
""",
        ),
    ],
}


def find_the_city(n: int, edges: list[list[int]], distance_threshold: int) -> int:
    infinity = float("inf")
    dist = [[infinity] * n for _ in range(n)]
    for i in range(n):
        dist[i][i] = 0
    for u, v, w in edges:
        if w < dist[u][v]:  # min guards against parallel edges
            dist[u][v] = dist[v][u] = w

    for k in range(n):  # k outermost: "paths using only 0..k as intermediates"
        through_k = dist[k]
        for i in range(n):
            i_to_k = dist[i][k]
            if i_to_k == infinity:
                continue
            row = dist[i]
            for j in range(n):
                if i_to_k + through_k[j] < row[j]:
                    row[j] = i_to_k + through_k[j]

    best_city, best_count = -1, n + 1
    for i in range(n):
        count = sum(1 for j in range(n) if j != i and dist[i][j] <= distance_threshold)
        if count <= best_count:  # <= so a tie promotes the larger index
            best_city, best_count = i, count
    return best_city


CASES = [
    ((4, [[0, 1, 3], [1, 2, 1], [1, 3, 4], [2, 3, 1]], 4), 3),
    # Answer is 0, so this catches "just return n - 1".
    ((5, [[0, 1, 2], [0, 4, 8], [1, 2, 3], [1, 4, 2], [2, 3, 1], [3, 4, 1]], 2), 0),
    ((2, [[0, 1, 5]], 4), 1),
    ((2, [[0, 1, 5]], 5), 1),
    ((1, [], 0), 0),
    # No edges: every count is 0.
    ((3, [], 10), 2),
    # The direct 0–2 edge costs 5 but the shortest path is 2.
    ((4, [[0, 1, 1], [1, 2, 1], [0, 2, 5], [2, 3, 4]], 2), 3),
    # Two components; the isolated pair is out of range of each other.
    ((5, [[0, 1, 1], [1, 2, 1], [2, 0, 1], [3, 4, 10]], 5), 4),
]


def solve(n: int, edges: list[list[int]], distance_threshold: int) -> int:
    return find_the_city(n, [edge[:] for edge in edges], distance_threshold)
