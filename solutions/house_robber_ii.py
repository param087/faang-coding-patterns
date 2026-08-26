"""House Robber II — LeetCode 213."""

from __future__ import annotations

META = {
    "pattern": "dp-1d",
    "insight": "The first and last houses cannot both be robbed, so run the linear solver twice — once without each — and take the max.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
House Robber, but the street is a **circle**: house `0` and house `n-1` are
now neighbours, so no two adjacent houses — including that wrap-around pair —
can both be robbed. Maximise the take.

Ask whether values can be zero or negative (LeetCode says non-negative, which
is why "rob nothing" never beats "rob something") and what `n = 1` means, since
in a one-house circle the house is adjacent to itself.
""",
        ),
        (
            "The insight",
            """
Do not try to patch the recurrence with a "did I take the first house" flag
carried down the array. It works, but it is fiddly and it is not what the
question is testing.

The circle imposes exactly one extra constraint: **houses 0 and n-1 are not
both taken**. So split on it:

- an optimal solution that skips house `0` is a linear problem on `nums[1:]`;
- an optimal solution that skips house `n-1` is a linear problem on `nums[:-1]`.

Every valid circular solution falls into at least one of those two cases, and
neither case can produce an invalid one. Take the larger.

```
rob_circular(nums) = max(rob_linear(nums[1:]), rob_linear(nums[:-1]))
```

Two O(n) passes is still O(n). This "split on the one thing that makes it hard,
solve the easy version twice" move shows up again in Best Time to Buy and Sell
Stock III and in most circular-array DP.
""",
        ),
        (
            "Edge cases",
            """
- **`n == 1`** — both slices are empty and you would return 0, which is wrong;
  the single house is robbable. Special-case it before splitting. This is the
  bug that actually fails the submission.
- **`n == 2`** — falls out correctly: the two slices are `[nums[1]]` and
  `[nums[0]]`, so you get `max(nums[0], nums[1])`. Worth checking out loud
  rather than adding a second special case for it.
- **Empty input** — return 0.
- **The tempting shortcut** "drop whichever of the first and last house is
  smaller, then run the linear solver once" is wrong. On `[1, 2, 1, 1]` the two
  ends tie at 1; drop the last and the linear answer on `[1, 2, 1]` is 2, but
  the true answer is **3** — rob indices 1 and 3, which are not adjacent on a
  4-circle. Deciding *which* end to drop is exactly the work the two-pass
  reduction refuses to do.
""",
        ),
    ],
}


def _rob_linear(nums: list[int], start: int, stop: int) -> int:
    take, skip = 0, 0  # best ending here having taken / skipped this house

    for i in range(start, stop):
        take, skip = skip + nums[i], max(skip, take)

    return max(take, skip)


def rob(nums: list[int]) -> int:
    n = len(nums)
    if n == 0:
        return 0
    if n == 1:
        return nums[0]  # a one-house circle: the slices would both be empty

    # Either house 0 is skipped, or house n-1 is. Slice by index, no copying.
    return max(_rob_linear(nums, 1, n), _rob_linear(nums, 0, n - 1))


CASES = [
    (([2, 3, 2],), 3),
    (([1, 2, 3, 1],), 4),
    (([1, 2, 3],), 3),
    (([200, 3, 140, 20, 10],), 340),
    (([1, 2],), 2),
    (([5],), 5),
    (([],), 0),
    (([0, 0, 0],), 0),
]


def solve(nums: list[int]) -> int:
    return rob(nums)
