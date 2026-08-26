"""4Sum II — LeetCode 454."""

from __future__ import annotations

from collections import Counter

META = {
    "pattern": "arrays-hashing",
    "insight": "Split four arrays into two halves: tally every a+b, then look up -(c+d). Meet in the middle turns n⁴ into n².",
    "time": "O(n²)",
    "space": "O(n²)",
    "sections": [
        (
            "What it asks",
            """
Four separate arrays, all of length `n`. Count the **index quadruplets**
`(i, j, k, l)` with `nums1[i] + nums2[j] + nums3[k] + nums4[l] == 0`.

Two things to nail down, and the second one is what makes the problem easy:

1. The arrays are **separate**, so no "each element used once" bookkeeping — one
   index is drawn from each.
2. The answer counts **tuples of indices, not distinct value combinations**. If
   `nums1 = [0, 0]`, those two zeros are two different answers.

`n ≤ 200`, so the brute force is 200⁴ = **1.6 × 10⁹** additions. That number is
the whole justification for what follows.
""",
        ),
        (
            "The insight",
            """
Meet in the middle. Split the four arrays into two pairs and precompute one
side:

- Tally every `a + b` from `nums1 × nums2` into a `Counter`. O(n²) work, O(n²)
  entries.
- For every `c + d` from `nums3 × nums4`, the sum is zero exactly when
  `a + b == -(c + d)`. Look that up and add its multiplicity.

O(n²) time, O(n²) space — 4 × 10⁴ operations instead of 1.6 × 10⁹.

Add the multiplicity, not one. The counter value is *how many (i, j) pairs*
produce that sum, and each of them pairs with the current `(k, l)`. Writing
`if -(c + d) in pair_sums: total += 1` is the bug that passes the sample and
fails on anything with repeats.

The generalisation is worth stating: **k-sum over k independent arrays splits
into two halves at O(n^(k/2))**. With six arrays you would hash triples.
""",
        ),
        (
            "Why there is no de-duplication here",
            """
This is the trap for anyone arriving from 3Sum or 4Sum. Those problems ask for
*distinct value tuples*, which forces sorting and a fiddly skip-equal-neighbours
dance. This one asks for a **count of index tuples**, and duplicates are
supposed to be counted separately.

`nums1 = nums2 = nums3 = nums4 = [0, 0]` is the case that settles it: the answer
is 2⁴ = **16**, not 1. Any instinct to sort, dedupe, or use a set of sums is
wrong here — a `Counter` is exactly right, and the `Counter` is *why* it is
right.

Two more things an interviewer may push on:

- **Space.** O(n²) is 4 × 10⁴ entries at `n = 200`, which is nothing. If it were
  not, hash the smaller cross product, or stream one half.
- **"Now return the quadruplets, not the count."** The output can be Θ(n⁴), so
  no algorithm beats the brute force in the worst case. Store index lists in the
  map rather than counts and accept the output-sensitive bound.
""",
        ),
    ],
}


def four_sum_count(
    nums1: list[int],
    nums2: list[int],
    nums3: list[int],
    nums4: list[int],
) -> int:
    pair_sums = Counter(a + b for a in nums1 for b in nums2)
    # Add the multiplicity, not 1: every (i, j) with that sum is its own answer.
    return sum(pair_sums[-(c + d)] for c in nums3 for d in nums4)


CASES = [
    (([1, 2], [-2, -1], [-1, 2], [0, 2]), 2),
    (([0], [0], [0], [0]), 1),
    (([0, 0], [0, 0], [0, 0], [0, 0]), 16),  # 2⁴ index tuples, not 1 value tuple
    (([1], [1], [1], [1]), 0),
    (([-1, -1], [-1, 1], [-1, 1], [1, -1]), 6),
    (([1, 2, 3], [-1, -2, -3], [0, 0, 0], [0, 0, 0]), 27),
    (([-1, -2], [-3, -4], [5, 6], [1, 2]), 1),
    (([], [], [], []), 0),
]


def solve(nums1: list[int], nums2: list[int], nums3: list[int], nums4: list[int]) -> int:
    return four_sum_count(nums1, nums2, nums3, nums4)
