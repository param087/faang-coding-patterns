"""4Sum — LeetCode 18."""

from __future__ import annotations

META = {
    "pattern": "two-pointers",
    "insight": "Sort, pin two indices, and let the converging pair solve the remaining 2Sum — the dedup rules are the whole difficulty.",
    "time": "O(n³)",
    "space": "O(1) beyond the sort and the output",
    "sections": [
        (
            "What it asks",
            """
Every **distinct** quadruplet summing to `target`. Distinct by *value*, not by
index: `[2,2,2,2,2]` with target 8 has exactly one answer, `[2,2,2,2]`, even
though five index choices produce it.

Two things to confirm out loud. First, order within a quadruplet and between
quadruplets does not matter — which frees you to sort. Second, `target` and the
values can both be large; in Java or C++ four `int`s summing past 2³¹ overflow
and you must widen to `long`. Python does not care, but saying it is what
separates a 4Sum answer from a memorised 3Sum answer.
""",
        ),
        (
            "The insight",
            """
Sort first. That does three jobs at once: equal values become adjacent so
dedup is a neighbour check, the pointer convergence becomes valid, and the
output comes out in a canonical order for free.

Then pin `i` and `j` with two loops and reduce to the sorted-2Sum you already
know: `lo`/`hi` converge on `target - nums[i] - nums[j]`. That is O(n²) pairs
times O(n) for the scan = **O(n³)**. At the constraint n = 200 that is 8·10⁶ —
comfortable.

The generic `k`-sum recursion (peel one index, recurse, bottom out at 2Sum) is
the elegant answer and worth mentioning, but under a clock the explicit two
loops are faster to write correctly and easier to talk through.
""",
        ),
        (
            "Dedup and pruning — where this is actually lost",
            """
Four dedup sites, and missing any one produces duplicate quadruplets:

- `i`: skip when `nums[i] == nums[i-1]` **and `i > 0`**.
- `j`: skip when `nums[j] == nums[j-1]` and **`j > i + 1`** — not `j > 0`. Using
  `j > 0` wrongly skips the second element of a legitimate pair like
  `[-1, -1, 1, 1]`.
- After recording a hit, advance `lo` past its duplicates and `hi` past its
  duplicates. Advancing only one of the two is the classic half-fix that passes
  the sample and fails on `[2,2,2,2,2]`.

The alternative — collect into a `set` of tuples — works and is a reasonable
thing to fall back on, but the interviewer will ask you to remove it.

The two prunes matter more than they look. Inside each loop:

- if the four **smallest** available values already exceed `target`, `break` —
  nothing further can help;
- if the current value plus the three **largest** still falls short, `continue`
  — this `i` is hopeless but a bigger one may not be.

`break` versus `continue` there is not interchangeable, and getting it backwards
is a silent correctness bug rather than a slow solution.
""",
        ),
    ],
}


def four_sum(nums: list[int], target: int) -> list[list[int]]:
    nums = sorted(nums)
    n = len(nums)
    result: list[list[int]] = []

    for i in range(n - 3):
        if i > 0 and nums[i] == nums[i - 1]:
            continue
        if nums[i] + nums[i + 1] + nums[i + 2] + nums[i + 3] > target:
            break  # smallest possible quad from here already overshoots
        if nums[i] + nums[n - 3] + nums[n - 2] + nums[n - 1] < target:
            continue  # this i cannot reach target, a larger one might

        for j in range(i + 1, n - 2):
            if j > i + 1 and nums[j] == nums[j - 1]:
                continue
            if nums[i] + nums[j] + nums[j + 1] + nums[j + 2] > target:
                break
            if nums[i] + nums[j] + nums[n - 2] + nums[n - 1] < target:
                continue

            lo, hi = j + 1, n - 1
            need = target - nums[i] - nums[j]
            while lo < hi:
                pair = nums[lo] + nums[hi]
                if pair < need:
                    lo += 1
                elif pair > need:
                    hi -= 1
                else:
                    result.append([nums[i], nums[j], nums[lo], nums[hi]])
                    lo += 1
                    hi -= 1
                    while lo < hi and nums[lo] == nums[lo - 1]:
                        lo += 1
                    while lo < hi and nums[hi] == nums[hi + 1]:
                        hi -= 1

    return result


CASES = [
    (([1, 0, -1, 0, -2, 2], 0), [[-2, -1, 1, 2], [-2, 0, 0, 2], [-1, 0, 0, 1]]),
    (([2, 2, 2, 2, 2], 8), [[2, 2, 2, 2]]),  # one answer from five index choices
    (([-2, -1, -1, 1, 1, 2, 2], 0), [[-2, -1, 1, 2], [-1, -1, 1, 1]]),  # both dedup sites
    (([0, 0, 0, 0], 0), [[0, 0, 0, 0]]),
    (([-3, -1, 0, 2, 4, 5], 2), [[-3, -1, 2, 4]]),
    (([1000000000, 1000000000, 1000000000, 1000000000], 0), []),  # overflows a 32-bit int
    (([1, 2, 3], 6), []),  # fewer than four values
    (([], 0), []),
]


def solve(nums: list[int], target: int) -> list[list[int]]:
    return four_sum(nums, target)
