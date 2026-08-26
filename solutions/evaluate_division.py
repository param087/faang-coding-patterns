"""Evaluate Division — LeetCode 399."""

from __future__ import annotations

META = {
    "pattern": "union-find",
    "insight": "Store, alongside each parent pointer, the ratio of the child to that parent — then a query is one division of two root-relative weights.",
    "time": "O((e + q) · α(n))",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Given equations like `a / b = 2.0` and a list of queries `x / y`, return each
query's value, or `-1.0` when it cannot be determined from the given facts.

Worth asking: are all values strictly positive (yes — which kills the division-
by-zero worry and lets you use multiplicative weights freely), and are the
equations guaranteed consistent (yes, so you never have to *detect* a
contradiction, though the follow-up below is exactly that). Also confirm the
tolerance: LeetCode accepts anything within 1e-5, so accumulating a few float
multiplications is fine.
""",
        ),
        (
            "The insight",
            """
The obvious answer is a graph: an edge `a → b` with weight 2.0 and `b → a` with
weight 0.5, then DFS/BFS per query multiplying along the path. That is correct
and O(q · (V + E)); with `q = 20` and `V ≤ 40` on LeetCode it is a perfectly
acceptable answer, and many interviewers will accept it.

The DSU answer is better when queries are many, and it is what puts this problem
in this chapter: keep a **weighted** union-find, where each node stores
`weight[x] = value(x) / value(parent[x])`. Path compression then collapses each
node to point straight at its root while multiplying the weights along the way,
so after `find(x)` you have `value(x) / value(root)` in O(1).

A query is then one division:

```
find(a); find(b)
if root(a) != root(b): return -1.0
return weight[a] / weight[b]     # (a/root) / (b/root) = a/b
```

The root cancels — that is the whole trick, and it is why the ratios can be
stored relative to an arbitrary, changing representative.

The union is the part to derive carefully rather than memorise. Given
`a / b = v`, with `ra = find(a)` and `rb = find(b)`, hang `ra` under `rb`:

```
value(ra)/value(rb) = (value(a)/weight[a]) / (value(b)/weight[b])
                    = v · weight[b] / weight[a]
```

Say that derivation out loud; it is the only place a sign or an inversion can
go wrong, and an interviewer watching you flounder there learns more than from
the rest of the problem.
""",
        ),
        (
            "The pitfalls",
            """
- **Unknown variables.** `["x","x"]` where `x` never appeared is `-1.0`, not
  `1.0`. The self-division shortcut only applies to variables the equations
  mention. Check membership before anything else.
- **Compression order.** In `find`, you must multiply the child's weight by the
  parent's root-relative weight **before** repointing the parent link. Reassign
  first and you have silently lost a factor. Doing the two-pass iterative
  version (walk to the root accumulating, then walk again rewriting) avoids
  recursion depth issues on a 10⁵-long chain — the recursive version is shorter
  but blows the default 1000-frame limit on adversarial input.
- **Union-by-rank fights the weights.** If you swap which root goes under which,
  you must invert the weight you were about to store. It is legal, but it is one
  more place to be wrong; skipping rank here costs you nothing asymptotically
  because path compression alone is already O(log n) amortised.
- **Float equality.** Never compare results with `==` in a test harness — the
  cases below round to 5 decimal places, matching the problem's stated
  tolerance.
- **Consistency follow-up.** If the equations were *not* guaranteed consistent,
  a union whose endpoints already share a root becomes a check rather than a
  no-op: verify `weight[a] / weight[b] ≈ v` and report a contradiction if not.
  That is a natural extension question, and this structure answers it in one
  extra line — the DFS solution does not.
""",
        ),
    ],
}


class WeightedUnionFind:
    """parent[x] plus weight[x] = value(x) / value(parent[x])."""

    def __init__(self) -> None:
        self.parent: dict[str, str] = {}
        self.weight: dict[str, float] = {}

    def add(self, x: str) -> None:
        if x not in self.parent:
            self.parent[x] = x
            self.weight[x] = 1.0

    def find(self, x: str) -> str:
        # Pass 1: walk to the root, accumulating value(x) / value(root).
        root, ratio = x, 1.0
        while self.parent[root] != root:
            ratio *= self.weight[root]
            root = self.parent[root]

        # Pass 2: repoint everything on the path directly at the root.
        node, node_ratio = x, ratio
        while self.parent[node] != root:
            nxt = self.parent[node]
            nxt_ratio = node_ratio / self.weight[node]  # must read the old weight first
            self.parent[node] = root
            self.weight[node] = node_ratio
            node, node_ratio = nxt, nxt_ratio

        return root

    def union(self, a: str, b: str, value: float) -> None:
        """Record a / b = value."""
        self.add(a)
        self.add(b)
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return
        # value(ra)/value(rb) = (a / weight[a]) / (b / weight[b]) = value·weight[b]/weight[a]
        self.parent[ra] = rb
        self.weight[ra] = value * self.weight[b] / self.weight[a]

    def query(self, a: str, b: str) -> float:
        if a not in self.parent or b not in self.parent:
            return -1.0
        if self.find(a) != self.find(b):
            return -1.0
        return self.weight[a] / self.weight[b]  # the shared root cancels


def calc_equation(
    equations: list[list[str]],
    values: list[float],
    queries: list[list[str]],
) -> list[float]:
    dsu = WeightedUnionFind()
    for (a, b), value in zip(equations, values, strict=True):
        dsu.union(a, b, value)

    # Rounded to the tolerance the problem allows, so results compare exactly.
    return [round(dsu.query(a, b), 5) for a, b in queries]


CASES = [
    (
        (
            [["a", "b"], ["b", "c"]],
            [2.0, 3.0],
            [["a", "c"], ["b", "a"], ["a", "e"], ["a", "a"], ["x", "x"]],
        ),
        [6.0, 0.5, -1.0, 1.0, -1.0],
    ),
    (
        (
            [["a", "b"], ["b", "c"], ["bc", "cd"]],
            [1.5, 2.5, 5.0],
            [["a", "c"], ["c", "b"], ["bc", "cd"], ["cd", "bc"]],
        ),
        [3.75, 0.4, 5.0, 0.2],
    ),
    (
        ([["a", "b"]], [0.5], [["a", "b"], ["b", "a"], ["a", "c"], ["x", "y"]]),
        [0.5, 2.0, -1.0, -1.0],
    ),
    (
        (
            [["a", "b"], ["c", "d"], ["d", "e"]],
            [2.0, 4.0, 5.0],
            [["a", "e"], ["c", "e"], ["e", "c"]],
        ),
        [-1.0, 20.0, 0.05],
    ),
    (
        (
            [["a", "b"], ["b", "c"], ["c", "d"], ["d", "e"], ["e", "f"]],
            [2.0, 2.0, 2.0, 2.0, 2.0],
            [["a", "f"], ["f", "a"], ["c", "c"]],
        ),
        [32.0, 0.03125, 1.0],
    ),
    (([["x", "y"]], [3.0], []), []),
]


def solve(
    equations: list[list[str]],
    values: list[float],
    queries: list[list[str]],
) -> list[float]:
    return calc_equation(equations, values, queries)
