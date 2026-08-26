"""Maximum Product Subarray — LeetCode 152."""

from __future__ import annotations

META = {
    "pattern": "dp-1d",
    "insight": "A negative number flips the ranking, so carry the running minimum too — today's worst product is tomorrow's best.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
The largest product of any **contiguous** subarray. Contiguous, not
subsequence — and non-empty, so an all-negative array cannot answer 1.

Ask: can the array contain zeros (yes) and negatives (yes)? Are the values
bounded such that the product fits in 32 bits? LeetCode guarantees every
*prefix* product fits, which is a real constraint in Java and irrelevant in
Python — mention it, because the interviewer put it there.

The wrong first answer is Kadane with `max` swapped in for `sum`:
`best_here = max(x, best_here * x)`. On `[-2, 3, -4]` it reports 3 and the
answer is **24**. Multiplication is not monotone the way addition is: the
largest product so far is worthless the moment a negative arrives, and the
*smallest* one becomes the asset.
""",
        ),
        (
            "The insight",
            """
Track **two** running quantities ending at the current index: the maximum
product `high` and the minimum product `low`. A negative `x` swaps their roles,
because `low * x` is then the largest thing available.

At each step the best subarray ending here is one of exactly three things:

```
candidates = (x, high * x, low * x)
high, low  = max(candidates), min(candidates)
```

The bare `x` is not decoration — it is the restart. It is what lets the
subarray begin at the current index, which is precisely what you need after a
zero has wiped both running products out. No special-casing of zeros is
required; `x` alone dominates `0 * x`.

Keep a separate global `best`, updated from `high` after each step, and seed
everything from `nums[0]` so the "non-empty" requirement holds automatically.
""",
        ),
        (
            "The pitfalls worth naming",
            """
**Computing `high` before `low`, in place.** Write `high = max(x, high * x, low * x)`
and then `low = min(x, high * x, low * x)` and the second line uses the *new*
`high`. Assign both from the same snapshot.

**Seeding `best` with 0 or 1.** The subarray must be non-empty. `best = 0`
returns 0 on `[-3]` and `best = 1` returns 1 — both are the product of the empty
subarray wearing a disguise. Seed `best`, `high` and `low` all from `nums[0]`
and iterate from index 1.

**Returning `high` instead of `best`.** On `[2, 3, -2, 4]` the run ends with
`high = 4`, because the trailing `-2` destroyed the good prefix and the subarray
restarted at `4`. The answer is **6**, recorded two steps earlier. `high` is
local to the current index; `best` is the global maximum and they are not the
same variable.

**The counting argument as a sanity check.** An even count of negatives between
zeros means the whole stretch multiplies to a positive; an odd count means you
must drop everything up to and including the first negative, or from the last
negative onward. That is the O(n) two-pass "scan forwards, scan backwards"
solution, and it is a fine alternative answer — but the min/max pair handles
zeros without the bookkeeping.

Dry run `[2, -5, -2, -4, 3]`: after `-5`, `(high, low) = (-5, -10)`. After `-2`,
`low * x = 20` becomes the new `high` — the minimum did the work. After `-4`,
`high = 8` (again from `low * x`) and `low = -80`. After `3`, `high = 24`.
Answer **24**, from `-2 · -4 · 3`.
""",
        ),
    ],
}


def max_product(nums: list[int]) -> int:
    if not nums:
        return 0

    best = high = low = nums[0]

    for value in nums[1:]:
        # `value` alone is the restart - it is what recovers from a zero.
        candidates = (value, high * value, low * value)
        high, low = max(candidates), min(candidates)  # one snapshot, both writes
        best = max(best, high)

    return best


CASES = [
    (([2, 3, -2, 4],), 6),
    (([-2, 3, -4],), 24),
    (([-2, 0, -1],), 0),
    (([2, -5, -2, -4, 3],), 24),
    (([-1, -2, -9, -6],), 108),
    (([0, 2],), 2),
    (([-3],), -3),
    (([],), 0),
]


def solve(nums: list[int]) -> int:
    return max_product(nums)
