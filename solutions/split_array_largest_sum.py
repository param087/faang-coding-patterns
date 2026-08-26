"""Split Array Largest Sum — LeetCode 410."""

from __future__ import annotations

META = {
    "pattern": "binary-search-answer",
    "insight": "Stop asking where the cuts go and ask whether a given largest-sum budget is affordable; that question has a greedy answer.",
    "time": "O(n log(sum − max))",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Cut `nums` into `k` contiguous non-empty subarrays so the **largest** subarray
sum is as small as possible. Return that largest sum.

Ask whether values can be zero or negative. LeetCode guarantees `nums[i] >= 0`,
and that is load-bearing: with negatives, prefix sums stop being monotone and
the greedy feasibility check below collapses. If the interviewer allows
negatives, the honest answer is "then it is DP, not binary search".
""",
        ),
        (
            "Brute force, and why it fails",
            """
Choose `k − 1` cut positions out of `n − 1`: C(n−1, k−1) splits. At n = 1000
and k = 50 that is about 10⁸⁵ — not a slow algorithm, an impossible one.

The standard rescue is DP: `dp[i][j]` = best cost splitting the first `i`
elements into `j` parts, filled by scanning every previous cut. That is
**O(n²k)** — at n = 1000, k = 50 that is 5·10⁷ states-times-transitions, which
passes but is the answer of someone who did not see the trick.
""",
        ),
        (
            "The insight",
            """
Invert the question. Instead of *"where do the cuts go?"* ask *"is a largest
sum of `limit` achievable with at most `k` parts?"*

That question has a greedy answer: sweep left to right, keep extending the
current part while it stays within `limit`, cut the moment it would exceed.
Because everything is non-negative, extending a part never helps a later part,
so this uses the **fewest possible** parts for that limit.

And feasibility is **monotone** — if `limit` works, `limit + 1` works. So the
feasible limits form a suffix of `[max(nums), sum(nums)]` and you binary search
for where it starts. O(n log(sum)) with 30-odd iterations, versus 5·10⁷.
""",
        ),
        (
            "Fewest parts, not exactly k",
            """
The check returns `parts_needed(limit) <= k`, not `== k`. This trips people up:
the problem demands *exactly* `k` subarrays.

It is fine, because a split into fewer parts can always be refined into more:
peel a single element off any part with at least two elements, and no part's
sum ever increases. As long as `n >= k` — which the constraints guarantee — a
feasible split into `p < k` parts implies a feasible split into exactly `k`.

Writing `== k` instead makes the predicate **non-monotone** and the binary
search returns nonsense. This is the detail that decides the problem.
""",
        ),
        (
            "The bounds",
            """
- **low = max(nums)** — some part contains the largest element, so no answer
  can be smaller. Starting at 0 or 1 is not just wasteful: the greedy loop
  then has to handle "a single element exceeds the limit", which is an
  infinite-loop bug waiting to happen if you write it as `while cur + x >
  limit: cut`.
- **high = sum(nums)** — `k = 1` puts everything in one part.

Both ends are achievable, so the answer is genuinely inside the range and the
lower-bound loop can land on either.
""",
        ),
        (
            "Dry run",
            """
`nums = [7,2,5,10,8], k = 2`. low = 10, high = 32.

- mid = 21 → parts: `7+2+5 = 14`, `+10 = 24 > 21` → cut; `10+8 = 18`. **2
  parts** ≤ 2, feasible → high = 21.
- mid = 15 → `7+2+5 = 14`, `+10 > 15` → cut; `10`, `+8 > 15` → cut; `8`. **3
  parts** > 2 → low = 16.
- mid = 18 → `14`, cut, `10+8 = 18` → **2 parts**, feasible → high = 18.
- mid = 17 → `14`, cut, `10`, `+8 = 18 > 17` → cut, `8`. **3 parts** → low = 18.

Answer **18**, the split `[7,2,5] | [10,8]`. Note 18 = 10 + 8 exactly: the
boundary case that the `<= limit` comparison has to include.
""",
        ),
        (
            "Follow-ups",
            """
- **"What if `nums` can be negative?"** Binary search dies — the greedy is no
  longer optimal, because a negative can make it worth extending a part past
  where you would otherwise cut. Fall back to the O(n²k) DP.
- **"Minimise the *maximum*, or maximise the *minimum*?"** Same skeleton,
  flipped comparison. Divide Chocolate (1231) and Magnetic Force Between Two
  Balls (1552) are the maximise-the-minimum twins.
- **"k up to n, n up to 10⁶?"** The binary search is untouched; it never had a
  `k` factor. That asymmetry is the strongest argument for it over DP.
""",
        ),
    ],
}


def split_array(nums: list[int], k: int) -> int:
    def parts_needed(limit: int) -> int:
        parts, current = 1, 0
        for num in nums:
            if current + num > limit:
                parts += 1
                current = 0
            current += num
        return parts

    low, high = max(nums), sum(nums)
    while low < high:
        mid = (low + high) // 2
        if parts_needed(mid) <= k:  # <= k, never == k: fewer parts can be refined
            high = mid
        else:
            low = mid + 1

    return low


CASES = [
    (([7, 2, 5, 10, 8], 2), 18),
    (([1, 2, 3, 4, 5], 2), 9),
    (([1, 2, 3, 4, 5], 1), 15),
    (([1, 2, 3, 4, 5], 5), 5),
    (([1, 4, 4], 3), 4),
    (([2, 3, 1, 2, 4, 3], 5), 4),
    (([0, 0, 0, 0], 2), 0),
    (([1], 1), 1),
]


def solve(nums: list[int], k: int) -> int:
    return split_array(nums, k)
