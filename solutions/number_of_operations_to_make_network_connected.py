"""Number of Operations to Make Network Connected — LeetCode 1319."""

from __future__ import annotations

META = {
    "pattern": "union-find",
    "insight": "If you own at least n-1 cables you always have enough spares, so the answer is just components - 1.",
    "time": "O(n + e · α(n))",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
`n` computers are wired by a list of `connections`. In one operation you may
unplug **any** existing cable and plug it in between any two computers. Return
the fewest operations that make every computer reachable from every other, or
`-1` if it is impossible.

Worth asking up front: **can you buy new cables?** No — that is the entire
problem. If you could, the answer would trivially be `components - 1` with no
feasibility question at all. The whole difficulty is the fixed cable budget.

Second question: can `connections` contain duplicates or self-loops? LeetCode
says no, but if it did they would still be counted as cables you own, which
keeps the argument below intact.
""",
        ),
        (
            "Brute force, and why it fails",
            """
The literal reading is a search: pick a cable to unplug, pick a pair of
computers to plug it into, recurse. At `n = 10⁵` there are about
`n²/2 = 5 × 10⁹` destination pairs for each of up to `10⁵` cables — roughly
**5 × 10¹⁴ candidate moves at the first level alone**, and the search is up to
`n - 1` levels deep.

Even the "smart" greedy version — repeatedly find a redundant cable, then find
two components to bridge — is O(n · e) if you re-scan connectivity after every
move: 10¹⁰ operations. The problem is not asking you to *perform* the moves. It
is asking you to **count** them.
""",
        ),
        (
            "The insight",
            """
Two separate facts, and the answer is the second one.

**Feasibility.** Connecting `n` computers needs at least `n - 1` cables, full
stop — that is the size of a spanning tree. So if `len(connections) < n - 1`,
return `-1` immediately, before touching the DSU.

**Cost.** With `c` connected components, you need exactly `c - 1` moves: each
move can merge at most two components (one cable joins two things), and a
sequence of `c - 1` well-chosen moves clearly achieves it. So:

```
if len(connections) < n - 1: return -1
build DSU; c = n - (successful unions)
return c - 1
```

The `-1` check and the component count are the two lines that matter. The DSU
is doing nothing exotic; it is just the cheapest way to get `c`.
""",
        ),
        (
            "The detail that decides it: you never run out of spare cables",
            """
The step almost everyone tries to add is a check that there are *enough
redundant cables* to perform `c - 1` moves. That check is unnecessary, and
being able to say why is the difference between a memorised solution and an
understood one.

Let `m = len(connections)` and let the components have sizes `k₁ … k_c`. A
component of `kᵢ` nodes uses **at least** `kᵢ - 1` cables to hold itself
together, so the cables that are genuinely load-bearing number at most
`Σ(kᵢ - 1) = n - c`. Therefore:

```
redundant cables  =  m - (n - c)
```

and once you have passed the `m ≥ n - 1` gate:

```
redundant  ≥  (n - 1) - (n - c)  =  c - 1
```

You always have at least as many spares as moves required. So the feasibility
test and the cost calculation are completely decoupled: **one comparison, then
one component count**. No second budget check, no min(), no case analysis.

The corollary is the sanity check for your `-1` branch: `m ≥ n - 1` is not a
heuristic, it is exactly the condition for solvability.
""",
        ),
        (
            "Dry run",
            """
`n = 6`, `connections = [[0,1],[0,2],[0,3],[1,2],[1,3]]`

- `m = 5`, `n - 1 = 5`. Feasible, by exactly zero margin.
- `union(0,1)` → True, `union(0,2)` → True, `union(0,3)` → True.
- `union(1,2)` → **False** (redundant). `union(1,3)` → **False** (redundant).
- 3 successful unions, so `c = 6 - 3 = 3`: `{0,1,2,3}`, `{4}`, `{5}`.
- Answer `c - 1` = **2**.

And note the arithmetic from the previous section lands on the nose: redundant
cables = `5 - (6 - 3)` = 2, exactly the two moves needed. Unplug `[1,2]` into
`[0,4]` and `[1,3]` into `[0,5]`.

Now delete one cable: `n = 6`, `connections = [[0,1],[0,2],[0,3],[1,2]]`. `m = 4
< 5` → **-1**, and no DSU work happens at all.
""",
        ),
        (
            "Follow-ups",
            """
- **"You may also buy cables, at cost 1 each."** Then `-1` never happens and the
  answer is `c - 1` unconditionally — which shows the `-1` branch really is the
  only place the cable budget appears.
- **"Which cables would you move, and where?"** Now you need the moves, not the
  count: collect the edges whose `union` returned `False`, collect one
  representative per root, and pair them up. Same pass, extra bookkeeping.
- **"Computers join and cables get added online; report the answer after every
  event."** Maintain `components` incrementally inside `union` and keep a
  running `m`; each query is O(1). This is where DSU beats a re-run of BFS by a
  factor of `n`.
- **"Cables have costs and you want the cheapest connected network."** That is
  Kruskal — same DSU, same `union`-returns-`False` skip rule, plus a sort. Min
  Cost to Connect All Points is the same question on a complete graph.
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
        """False means they already shared a root — that cable is a spare."""
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True


def make_connected(n: int, connections: list[list[int]]) -> int:
    if len(connections) < n - 1:  # fewer cables than a spanning tree needs
        return -1

    dsu = UnionFind(n)
    components = n
    for a, b in connections:
        if dsu.union(a, b):
            components -= 1

    # Spares are guaranteed by the check above, so cost is purely the merge count.
    return components - 1


CASES = [
    ((4, [[0, 1], [0, 2], [1, 2]]), 1),
    ((6, [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3]]), 2),
    ((6, [[0, 1], [0, 2], [0, 3], [1, 2]]), -1),
    ((5, [[0, 1], [0, 2], [3, 4], [2, 3]]), 0),
    ((1, []), 0),
    ((2, []), -1),
    ((3, [[0, 1], [0, 2], [1, 2]]), 0),
    ((5, [[0, 1], [0, 2], [1, 2], [3, 4]]), 1),
]


def solve(n: int, connections: list[list[int]]) -> int:
    return make_connected(n, connections)
