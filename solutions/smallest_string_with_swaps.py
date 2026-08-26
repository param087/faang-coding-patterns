"""Smallest String With Swaps — LeetCode 1202."""

from __future__ import annotations

META = {
    "pattern": "union-find",
    "insight": "Swaps are transitive, so each component of indices permutes freely — sort its characters and write them back in index order.",
    "time": "O(n log n + p · α(n))",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Given a string `s` and a list of index pairs, you may swap the characters at
any listed pair **any number of times**. Return the lexicographically smallest
string reachable.

Worth asking: unlimited swaps (yes — this is the hinge), and can pairs repeat or
be given in either order (yes, both harmless). If swaps were limited to *one
use each* this becomes a genuinely hard permutation problem; the "any number of
times" clause is what collapses it.
""",
        ),
        (
            "The insight",
            """
"Any number of times" means the reachable rearrangements form a group, and
swapping is transitive: if you can swap `(0,3)` and `(3,5)`, you can move the
character at 0 to position 5 by composing them. So the index set partitions into
connected components, and **within a component every permutation is reachable**
— adjacent transpositions generate the full symmetric group on that component.

That reduces the problem to something with no search in it at all:

1. Union every pair.
2. Bucket indices by root.
3. For each bucket, sort the indices and sort the characters at those indices,
   then zip them back together.

Sorted indices paired with sorted characters puts the smallest available
character at the earliest position in that component, which is exactly the
greedy that lexicographic order demands. Positions in different components
never interact, so the greedy is safe locally and globally at once.

The wrong first answer is to run bubble-sort-like passes over the allowed pairs
until nothing improves. It converges to the same string, but it is O(n²) passes
in the worst case and you cannot bound it cleanly in an interview.
""",
        ),
        (
            "Edge cases",
            """
- **No pairs** → return `s` unchanged. Every index is its own component of size
  one, and sorting a singleton does nothing.
- **All indices in one component** → the answer is `sorted(s)`. Useful as a
  sanity check: `"dcab"` with pairs forming a chain gives `"abcd"`.
- **Duplicate characters** are fine — sorting is stable enough here because
  equal characters are interchangeable by definition.
- **Duplicate or self-referential pairs** (`[2,2]`) produce a `union` that
  returns `False` and change nothing.
- The bucketing pass is where an off-by-one hides: you need `find(i)` for
  *every* index `0..n-1`, not just the indices that appear in `pairs`, or the
  untouched positions get dropped from the output entirely.
- Complexity note worth saying: sorting each component separately totals
  O(n log n) across all of them, not O(k · n log n) — the components are
  disjoint.
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


def smallest_string_with_swaps(s: str, pairs: list[list[int]]) -> str:
    n = len(s)
    dsu = UnionFind(n)
    for a, b in pairs:
        dsu.union(a, b)

    components: dict[int, list[int]] = {}
    for i in range(n):  # every index, not just the ones named in pairs
        components.setdefault(dsu.find(i), []).append(i)

    result = list(s)
    for indices in components.values():
        # indices are already ascending; pair them with the sorted characters
        for index, char in zip(indices, sorted(result[i] for i in indices), strict=True):
            result[index] = char

    return "".join(result)


CASES = [
    (("dcab", [[0, 3], [1, 2]]), "bacd"),
    (("dcab", [[0, 3], [1, 2], [0, 2]]), "abcd"),
    (("cba", [[0, 1], [1, 2]]), "abc"),
    (("abc", []), "abc"),
    (("a", []), "a"),
    (("zdcbay", [[0, 5], [1, 4]]), "yacbdz"),
    (("dbca", [[0, 1], [1, 2], [2, 3], [0, 3]]), "abcd"),
    (("bbaa", [[0, 2], [1, 3]]), "aabb"),
]


def solve(s: str, pairs: list[list[int]]) -> str:
    return smallest_string_with_swaps(s, pairs)
