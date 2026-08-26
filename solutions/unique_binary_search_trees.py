"""Unique Binary Search Trees — LeetCode 96."""

from __future__ import annotations

META = {
    "pattern": "binary-search-trees",
    "symbol": "num_trees",
    "insight": "Fix the root and the count factorises into left size times right size — only the sizes matter, never the actual values.",
    "time": "O(n²)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Count the structurally distinct BSTs holding the values `1..n`. Structurally
distinct means the *shape* differs; since a BST is determined by its shape once
the value set is fixed, shape and tree are the same thing here.

`n ≤ 19` in the constraints. That bound is a message: the answer at n = 19 is
1,767,263,190, just under 2³¹, so the problem is sized to fit a 32-bit signed
int. In Python that is irrelevant; in Java or C++ it is the reason the limit
exists, and saying so is free credibility.

Clarify that you return a **count**, not the trees. Building them is LeetCode
95, and it is a different problem with a different complexity.
""",
        ),
        (
            "The insight",
            """
Pick which value is the root. If the root is `i`, then `1..i-1` must all sit in
the left subtree and `i+1..n` in the right — no choice about it, that is the
BST property. So:

```
count(n) = Σ over i in 1..n of  count(i - 1) * count(n - i)
```

The second observation is the one that turns this from exponential recursion
into a 10-line DP: **the count depends only on the number of values, not on
which values.** A subtree over `{4,5,6}` has exactly as many shapes as one over
`{1,2,3}`. So there are n+1 distinct subproblems, not 2ⁿ intervals, and a
single array indexed by size holds them all.

`count(0) = 1` — the empty tree is one arrangement, not zero. Getting that
base case wrong zeroes out every product and the whole answer collapses to 0.

Fill sizes upward; each size `s` costs `s` multiplications, so O(n²) total.
These are the Catalan numbers: 1, 1, 2, 5, 14, 42, 132.
""",
        ),
        (
            "Follow-ups",
            """
- **"Now return the trees" (LeetCode 95, Unique BSTs II)** — same split, but
  you build every left/right pair and take the cross product. The output size
  is Catalan(n) itself, so the complexity is Ω(4ⁿ / n^1.5); do not promise
  polynomial time. Memoise on `(lo, hi)` and share subtree objects between
  results if they let you.
- **"Closed form?"** — `C(2n, n) / (n + 1)`, O(n) with one pass of
  multiplications, or O(1) if you are allowed big-int binomials. Worth naming;
  the DP is still the safer thing to write under pressure because it survives
  the follow-up where the values are no longer `1..n`.
- **Where else this shape appears** — valid parenthesis strings of length 2n,
  triangulations of a convex polygon, and the number of distinct stack push/pop
  orders. If a counting problem splits into "left part × right part over every
  pivot", it is Catalan.
""",
        ),
    ],
}


def num_trees(n: int) -> int:
    # counts[s] = number of BST shapes over s values; the empty tree counts as one.
    counts = [0] * (n + 1)
    counts[0] = 1

    for size in range(1, n + 1):
        total = 0
        for left in range(size):  # left subtree holds `left` values
            total += counts[left] * counts[size - 1 - left]
        counts[size] = total

    return counts[n]


CASES = [
    ((0,), 1),  # the empty tree — the base case the whole DP rests on
    ((1,), 1),
    ((2,), 2),
    ((3,), 5),
    ((4,), 14),
    ((10,), 16796),
    ((19,), 1767263190),  # the constraint ceiling, just under 2^31
]


def solve(n: int) -> int:
    return num_trees(n)
