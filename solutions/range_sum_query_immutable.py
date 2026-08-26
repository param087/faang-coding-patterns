"""Range Sum Query - Immutable — LeetCode 303."""

from __future__ import annotations

META = {
    "pattern": "prefix-sums",
    "symbol": "NumArray",
    "insight": "Pay O(n) once at construction so every range answers as the difference of two prefix sums in O(1).",
    "time": "O(n) to build, O(1) per query",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Build a structure over a fixed array that answers `sumRange(left, right)` —
inclusive on both ends — for many queries. The array never changes.

Ask: **how many queries relative to n?** That is the whole design question. At
one query, summing the slice is optimal and the prefix array is wasted work; at
10⁴ queries over n = 10⁴, the naive version is 10⁸ additions and the prefix
array is 10⁴ plus 10⁴. State the crossover instead of reciting the answer.

Also confirm the range is inclusive, and that `update` is genuinely not
required — if it is, this is LeetCode 307 and you want a Fenwick tree.
""",
        ),
        (
            "The insight",
            """
`sum(left..right) = prefix[right + 1] - prefix[left]`, where `prefix` is the
**exclusive** cumulative array of length `n + 1`:

```
prefix[0] = 0
prefix[i] = nums[0] + ... + nums[i - 1]
```

Each query is one subtraction. Construction is one pass. Nothing else happens.

The reason this is asked at all is that it is the smallest possible instance of
"precompute a reversible aggregate". Sums are invertible, so a range reduces to
a difference. Min and max are not, which is exactly why the min/max version
needs a sparse table or a segment tree instead — worth saying in one line,
because it shows you know the boundary of the trick.
""",
        ),
        (
            "The leading zero is the entire trick",
            """
Store the **inclusive** running sum instead and `sumRange(0, r)` becomes a
special case: `prefix[r] - prefix[-1]` has no meaning, so you write
`left == 0 ? prefix[right] : prefix[right] - prefix[left - 1]`.

That branch is where the bug lives. The `n + 1`-length array with a leading `0`
makes it disappear: `left = 0` reads `prefix[0] = 0`, the empty sum, which is
correct by construction rather than by a guard.

Same reasoning gives the `{0: -1}` seed in the hash-map prefix-sum problems and
the padded row-and-column in the 2-D version. One extra slot, no boundary
cases — carry that habit into all of them.
""",
        ),
    ],
}


class NumArray:
    def __init__(self, nums: list[int]) -> None:
        # Length n + 1 with a leading zero: prefix[i] is the sum of nums[:i].
        self.prefix = [0] * (len(nums) + 1)
        for i, value in enumerate(nums):
            self.prefix[i + 1] = self.prefix[i] + value

    def sum_range(self, left: int, right: int) -> int:
        # Inclusive on both ends, and no branch for left == 0.
        return self.prefix[right + 1] - self.prefix[left]


CASES: list[tuple[tuple, object]] = []


def check() -> None:
    array = NumArray([-2, 0, 3, -5, 2, -1])
    assert array.sum_range(0, 2) == 1
    assert array.sum_range(2, 5) == -1
    assert array.sum_range(0, 5) == -3
    assert array.sum_range(0, 0) == -2  # left == 0 needs no special case
    assert array.sum_range(5, 5) == -1  # last index
    assert array.sum_range(3, 3) == -5  # a single negative element

    single = NumArray([7])
    assert single.sum_range(0, 0) == 7

    zeros = NumArray([0, 0, 0, 0])
    assert zeros.sum_range(0, 3) == 0
    assert zeros.sum_range(1, 2) == 0

    # Repeated queries must be idempotent — the structure is read-only.
    repeated = NumArray([1, 2, 3])
    for _ in range(3):
        assert repeated.sum_range(0, 2) == 6

    # An empty array must still build; there is simply nothing to query.
    empty = NumArray([])
    assert empty.prefix == [0]

    # Cross-check every range against a brute-force slice sum.
    raw = [4, -1, 9, 0, 3, 7, -5, 2]
    checked = NumArray(raw)
    for left in range(len(raw)):
        for right in range(left, len(raw)):
            assert checked.sum_range(left, right) == sum(raw[left : right + 1])
