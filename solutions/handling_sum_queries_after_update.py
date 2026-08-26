"""Handling Sum Queries After Update — LeetCode 2569."""

from __future__ import annotations

META = {
    "pattern": "segment-tree",
    "insight": "nums2 never needs to exist: a type-2 query adds p × (number of ones in nums1) to the running total, so the only live state is a flip-lazy count of ones.",
    "time": "O(n + q log n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Two arrays: `nums1` is binary, `nums2` is arbitrary. Three query types:

- `[1, l, r]` — flip every bit of `nums1` in `[l, r]`;
- `[2, p, 0]` — set `nums2[i] += nums1[i] * p` for **every** `i`;
- `[3, 0, 0]` — report `sum(nums2)`.

`n` and `q` both reach 10⁵. A type-2 query touching all `n` entries is 10¹⁰
element writes across the query stream, so the naive simulation is dead on the
type that looks cheapest to implement.

Confirm the ranges are inclusive and that type 2 applies to the *whole* array,
not a range — that global scope is exactly what makes the problem collapse.
""",
        ),
        (
            "The insight",
            """
Only type 3 ever observes `nums2`, and only in aggregate. So track the scalar
`total = sum(nums2)` and ask what each query does to it:

- type 2 with multiplier `p` adds `p · Σ nums1[i]` — and since `nums1` is
  binary, `Σ nums1[i]` is just **the number of ones**;
- type 1 changes that count;
- type 3 prints the scalar.

`nums2` is therefore never stored past its initial sum, and the entire problem
reduces to *maintain the number of ones in a binary array under range flips*.

That is a segment tree where each node holds `ones` for its span and carries a
boolean lazy tag meaning "this span is flipped". Applying a flip to a node is

```
ones = span_length - ones
```

which is why the node has to know its own length — a flip is not a value you can
push down, it is an involution on the stored count. O(log n) per flip, O(1) per
type 2 and type 3.

A Fenwick tree cannot do this: range update with range query needs either lazy
tags or the two-BIT difference trick, and the flip is not additive, so the
segment tree is genuinely the right structure here rather than the heavier one.
""",
        ),
        (
            "The pitfalls: the tag is XOR, and p can be zero",
            """
**Lazy flips compose by XOR, not assignment.** `flip[node] ^= True`. Two flips
of the same span cancel; writing `flip[node] = True` on the second one leaves a
spurious pending flip and the count drifts. The test is a query list containing
the *same* `[1, l, r]` twice — the state must be identical to before, and the
subsequent type-3 answer unchanged.

**Push down before recursing, and only then.** Flip tags on a node that is fully
covered stop there; on a partially covered node the pending tag must reach the
children before their counts are read, or the recursion reads stale values. The
symptom is an answer that is correct on ranges aligned to the tree and wrong on
ragged ones.

Two more:

- `p` can be **0**, in which case type 2 is a no-op. A guard that "optimises" by
  skipping when the ones count is zero is fine; one that assumes `p > 0` and
  short-circuits differently is not.
- Only **type 3** contributes to the output, so the result list is shorter than
  the query list — and it can be empty. Sizing the output to `len(queries)` and
  filling by index is the usual off-by-everything here.
- `total` reaches ~10⁵ · 10⁹ + 10⁵ · 10⁶ · 10⁵ ≈ 10¹⁶. Fine in Python, but in
  Java or C++ it is `long`, and every intermediate `p * ones` too.
""",
        ),
    ],
}


class FlipCountTree:
    """Number of ones in a binary array, under range flips."""

    def __init__(self, bits: list[int]) -> None:
        self.size = max(len(bits), 1)
        self.ones = [0] * (4 * self.size)
        self.flip = [False] * (4 * self.size)
        if bits:
            self._build(bits, 1, 0, self.size - 1)

    def _build(self, bits: list[int], node: int, lo: int, hi: int) -> None:
        if lo == hi:
            self.ones[node] = bits[lo]
            return
        mid = (lo + hi) // 2
        self._build(bits, 2 * node, lo, mid)
        self._build(bits, 2 * node + 1, mid + 1, hi)
        self.ones[node] = self.ones[2 * node] + self.ones[2 * node + 1]

    def _apply(self, node: int, lo: int, hi: int) -> None:
        self.ones[node] = (hi - lo + 1) - self.ones[node]  # an involution
        self.flip[node] ^= True  # XOR: two flips cancel

    def _push(self, node: int, lo: int, mid: int, hi: int) -> None:
        if self.flip[node]:
            self._apply(2 * node, lo, mid)
            self._apply(2 * node + 1, mid + 1, hi)
            self.flip[node] = False

    def flip_range(self, left: int, right: int,
                   node: int = 1, lo: int = 0, hi: int | None = None) -> None:
        hi = self.size - 1 if hi is None else hi
        if right < lo or hi < left:
            return
        if left <= lo and hi <= right:
            self._apply(node, lo, hi)
            return
        mid = (lo + hi) // 2
        self._push(node, lo, mid, hi)  # before recursing, always
        self.flip_range(left, right, 2 * node, lo, mid)
        self.flip_range(left, right, 2 * node + 1, mid + 1, hi)
        self.ones[node] = self.ones[2 * node] + self.ones[2 * node + 1]

    @property
    def count(self) -> int:
        return self.ones[1]


def handle_query(
    nums1: list[int], nums2: list[int], queries: list[list[int]]
) -> list[int]:
    tree = FlipCountTree(nums1)
    total = sum(nums2)  # nums2 is never needed again, only its sum

    answers: list[int] = []
    for kind, a, b in queries:
        if kind == 1:
            tree.flip_range(a, b)
        elif kind == 2:
            total += a * tree.count  # a is p; ones count == sum(nums1)
        else:
            answers.append(total)
    return answers  # only type 3 contributes


CASES = [
    (([1, 0, 1], [0, 0, 0], [[1, 1, 1], [2, 1, 0], [3, 0, 0]]), [3]),
    (([1], [5], [[2, 0, 0], [3, 0, 0]]), [5]),
    # Two identical flips must cancel: XOR tag, not assignment.
    (([0, 1], [1, 2], [[1, 0, 1], [1, 0, 1], [2, 10, 0], [3, 0, 0]]), [13]),
    # Multiple reports, and a report before anything has happened.
    (([0, 0], [1, 1], [[3, 0, 0], [1, 0, 1], [2, 2, 0], [3, 0, 0]]), [2, 6]),
    # Ragged ranges over a full array, exercising push-down on partial nodes.
    (
        (
            [1, 1, 1, 1],
            [0, 0, 0, 0],
            [[1, 1, 2], [2, 5, 0], [3, 0, 0], [1, 0, 3], [2, 3, 0], [3, 0, 0]],
        ),
        [10, 16],
    ),
    # No type-3 query: the answer list is empty, not len(queries) long.
    (([1, 1], [4, 4], [[1, 0, 0], [2, 7, 0]]), []),
    (([1], [1], []), []),
    # Negative values in nums2 are allowed by nothing but arithmetic; sum still works.
    (([0, 1, 0], [-5, 3, -1], [[3, 0, 0], [1, 0, 2], [2, 4, 0], [3, 0, 0]]), [-3, 5]),
]


def solve(
    nums1: list[int], nums2: list[int], queries: list[list[int]]
) -> list[int]:
    return handle_query(
        list(nums1), list(nums2), [list(query) for query in queries]
    )
