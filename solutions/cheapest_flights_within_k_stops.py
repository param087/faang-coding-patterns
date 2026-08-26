"""Cheapest Flights Within K Stops — LeetCode 787."""

from __future__ import annotations

META = {
    "pattern": "shortest-paths",
    "insight": "A hop budget makes cost alone the wrong ordering — relax edges in rounds instead, where round i means 'at most i edges'.",
    "time": "O(k · E)",
    "space": "O(V)",
    "sections": [
        (
            "What it asks",
            """
Directed flights with prices. Find the cheapest route from `src` to `dst`
using **at most `k` stops** — that is, at most `k + 1` flights. −1 if no such
route exists.

Ask two things. First, "stops" or "flights"? Off-by-one here is the single
most common way this is failed: `k` stops means `k + 1` edges. Second, are
prices non-negative (yes, LeetCode says 0–10⁴) — that keeps Dijkstra on the
table as a follow-up even though it is not the clean answer.
""",
        ),
        (
            "Brute force, and why it fails",
            """
DFS every route with at most `k + 1` edges. With `n = 100` cities and up to
5700 flights, out-degree can reach 99, and `k` can be 100 — so the search tree
is 99^101 in the worst case. Even the modest shape 99^11 is roughly 9 × 10²¹
paths. Not a candidate.

Memoising on `(city, flights_used)` fixes it, and that memo is exactly the DP
table the round-based solution fills iteratively.
""",
        ),
        (
            "Why plain Dijkstra is the wrong first answer",
            """
Reach for Dijkstra and you will write something that fails, because Dijkstra's
correctness rests on "once a node is settled at its cheapest cost, that cost is
final". Under a hop budget that is false: **the cheapest way to reach a city
may use too many flights to be useful.**

Concrete counterexample. Edges `0→1 (1)`, `1→2 (1)`, `2→3 (1)`, `0→2 (5)`,
with `src = 0`, `dst = 3`, `k = 1` (so at most 2 flights):

- Dijkstra settles city 2 at cost 2 via `0→1→2` — but that already spent both
  flights, so `2→3` is unreachable from that state.
- The only legal answer is `0→2→3` at cost **6**.

A cost-only priority queue never considers the more expensive arrival at city 2
and reports 3. The fix is to make hop count part of the state, which is the
follow-up below — but the round-based version is shorter and states the
constraint directly.
""",
        ),
        (
            "The insight",
            """
This is **Bellman–Ford truncated to `k + 1` rounds**.

After round `i`, `dist[v]` holds the cheapest cost to reach `v` using **at most
`i` edges**. Bellman–Ford's usual `V − 1` rounds exist to guarantee
convergence; here the round count is not a convergence bound at all — it *is*
the constraint. Stopping early is the whole algorithm.

Each round is one sweep over the edge list, so O(k · E) = 100 × 5700 = 5.7 × 10⁵
edge relaxations. Nothing about that is tight.
""",
        ),
        (
            "The one line that decides it",
            """
```python
snapshot = dist[:]
```

Relax **from the previous round's distances**, not from the array you are
writing into. Without the copy, an edge relaxed earlier in the same sweep feeds
a later edge in the same sweep, and a single round chains two or three flights
together. You silently allow more hops than the budget and return a price that
is too low.

The failure is order-dependent, which makes it worse: shuffle the flight list
and the same buggy code starts passing. Copy the array, or track
`dist[i][v]` as a genuine 2-D table.

The `if not updated: break` is a real early exit, not decoration — once a round
changes nothing, no later round will either.
""",
        ),
        (
            "Dry run",
            """
`n = 4`, flights `[[0,1,100],[1,2,100],[2,0,100],[1,3,600],[2,3,200]]`,
`src = 0`, `dst = 3`, `k = 1` → 2 rounds.

- **Round 1** (≤ 1 flight): only `0→1` fires. `dist = [0, 100, ∞, ∞]`.
- **Round 2** (≤ 2 flights), reading the snapshot `[0, 100, ∞, ∞]`:
  `1→2` gives 200, `1→3` gives **700**. `2→3` reads `snapshot[2] = ∞` and does
  nothing.

Answer **700** — the route `0→1→3`.

Now drop the snapshot. `1→2` writes `dist[2] = 200`, and a few edges later
`2→3` reads that fresh 200 and produces 400 via `0→1→2→3` — three flights, two
stops, over budget. 400 is the answer you get for forgetting one line.
""",
        ),
        (
            "Follow-ups",
            """
- **"Do it with a heap."** Push `(cost, city, flights_used)` and keep a
  `best[city][flights_used]` table, or simply prune when `flights_used > k`.
  Cost-ordered popping still returns `dst` at its true minimum on first arrival,
  because arriving at `dst` needs no further hops. Complexity O(E · k log(E · k))
  — worse than the rounds, and the reason to prefer Bellman–Ford here.
- **"Negative prices?"** Rounds still work; the DP is unaffected because you
  never claim convergence. The heap version breaks outright.
- **Exactly `k` stops** rather than at most: keep the full 2-D table and read
  `dist[k + 1][dst]`, since the collapsed 1-D array cannot distinguish "cheaper
  with fewer hops".
""",
        ),
    ],
}


def find_cheapest_price(
    n: int, flights: list[list[int]], src: int, dst: int, k: int
) -> int:
    infinity = float("inf")
    dist = [infinity] * n
    dist[src] = 0.0

    for _ in range(k + 1):  # k stops == k + 1 flights == k + 1 rounds
        snapshot = dist[:]  # relax from the previous round, never from itself
        updated = False
        for u, v, price in flights:
            if snapshot[u] + price < dist[v]:
                dist[v] = snapshot[u] + price
                updated = True
        if not updated:
            break

    return -1 if dist[dst] == infinity else int(dist[dst])


CASES = [
    ((4, [[0, 1, 100], [1, 2, 100], [2, 0, 100], [1, 3, 600], [2, 3, 200]], 0, 3, 1), 700),
    ((3, [[0, 1, 100], [1, 2, 100], [0, 2, 500]], 0, 2, 1), 200),
    ((3, [[0, 1, 100], [1, 2, 100], [0, 2, 500]], 0, 2, 0), 500),
    # Cheapest route to city 2 uses both hops — Dijkstra-by-cost returns 3 here.
    ((4, [[0, 1, 1], [1, 2, 1], [2, 3, 1], [0, 2, 5]], 0, 3, 1), 6),
    ((4, [[0, 1, 1], [1, 2, 1], [2, 3, 1], [0, 2, 5]], 0, 3, 2), 3),
    # Edge order chains three hops in one round without the snapshot copy.
    ((5, [[0, 3, 2], [3, 1, 2], [1, 2, 5], [0, 1, 5]], 0, 2, 1), 10),
    ((2, [[0, 1, 5]], 1, 0, 5), -1),
    ((1, [], 0, 0, 0), 0),
]


def solve(n: int, flights: list[list[int]], src: int, dst: int, k: int) -> int:
    return find_cheapest_price(n, flights, src, dst, k)
