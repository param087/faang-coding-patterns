"""Satisfiability of Equality Equations — LeetCode 990."""

from __future__ import annotations

META = {
    "pattern": "union-find",
    "insight": "Equality is an equivalence relation, so process every '==' first to build the classes, then let every '!=' try to falsify them.",
    "time": "O(m · α(26))",
    "space": "O(1) — 26 variables",
    "sections": [
        (
            "What it asks",
            """
You get a list of strings, each exactly four characters, of the form `"a==b"`
or `"a!=b"` over single lowercase letters. Return whether some assignment of
integers to the letters satisfies all of them at once.

Worth asking: are variables always single lowercase letters (yes — that is why
the DSU is a fixed 26 slots and the space is O(1)), and is the relation over an
infinite domain (yes, integers, which is why there is never a pigeonhole
constraint forcing two distinct classes to collide).
""",
        ),
        (
            "The insight",
            """
`==` is an equivalence relation: reflexive, symmetric, **transitive**. That is
the definition of what a disjoint-set structure maintains, so the mapping is
not a trick — it is the same object.

The ordering is everything: **two passes, equalities first**.

```
for eq in equations:
    if eq[1] == '=': union(eq[0], eq[3])
for eq in equations:
    if eq[1] == '!' and find(eq[0]) == find(eq[3]): return False
return True
```

Interleaving the two kinds in one pass is the wrong first answer, and it fails
on `["a!=b", "a==b"]`: at the moment you check `a != b`, nothing has been
unioned yet, so `find('a') != find('b')` and you wrongly say satisfiable. The
inequalities are *constraints on the finished partition*, so they can only be
evaluated once the partition is finished.

Once the classes are built, satisfiability is trivial: give each class a
distinct integer. Every `==` holds by construction, and every `!=` holds iff its
two letters landed in different classes — which is exactly the second pass.
""",
        ),
        (
            "Edge cases",
            """
- **`["a!=a"]`** → `False`. Reflexivity makes any self-inequality immediately
  unsatisfiable, and the DSU handles it without a special case because
  `find('a') == find('a')` trivially.
- **`["a==a"]`** → `True`, and the union is a no-op.
- **Empty input** → `True`. Nothing to violate.
- **Transitive chains**: `["a==b","b==c","a!=c"]` → `False`. This is the case
  that catches a hash-map-of-pairs solution which never propagates equality
  through `b`.
- **Independent classes**: `["a==b","c==d","a!=c"]` → `True`. Two separate
  classes, so the inequality is satisfiable — a check that returns `False` for
  any `!=` at all fails here.
- Note the parse: with fixed-width strings, `eq[1]` distinguishes `=` from `!`
  and the operands are `eq[0]` and `eq[3]`. Do not reach for `split`.
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
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True


def equations_possible(equations: list[str]) -> bool:
    dsu = UnionFind(26)

    def index(letter: str) -> int:
        return ord(letter) - ord("a")

    for equation in equations:  # pass 1: build the equivalence classes
        if equation[1] == "=":
            dsu.union(index(equation[0]), index(equation[3]))

    for equation in equations:  # pass 2: try to falsify them
        if equation[1] == "!" and dsu.find(index(equation[0])) == dsu.find(index(equation[3])):
            return False

    return True


CASES = [
    ((["a==b", "b!=a"],), False),
    ((["a!=b", "a==b"],), False),  # order-dependent naive version says True
    ((["a==b", "b==a"],), True),
    ((["a==b", "b==c", "a==c"],), True),
    ((["a==b", "b==c", "a!=c"],), False),
    ((["c==c", "b==d", "x!=z"],), True),
    ((["a==b", "c==d", "a!=c"],), True),
    ((["a!=a"],), False),
    (([],), True),
]


def solve(equations: list[str]) -> bool:
    return equations_possible(equations)
