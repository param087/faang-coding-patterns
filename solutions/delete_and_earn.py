"""Delete and Earn — LeetCode 740."""

from __future__ import annotations

from collections import Counter

META = {
    "pattern": "dp-1d",
    "insight": "The decision is per distinct value, not per element: take a value and you take every copy, but lose v-1 and v+1 entirely.",
    "time": "O(n log n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Pick a number `v` from the array, earn `v`, and delete **every** copy of `v`
along with every copy of `v-1` and `v+1`. Repeat until the array is empty.
Maximise the total earned.

The clarification worth making: deleting `v` removes all copies of `v` at once,
and picking `v` again later is impossible. So the whole problem lives on the
*set of distinct values*, not on the elements.
""",
        ),
        (
            "The insight",
            """
Two observations turn this into a problem you already know.

**One.** If you ever take value `v`, you should take every copy of it. Taking
one copy already destroys `v-1` and `v+1`, so the remaining copies are free
money. Collapse the array to `points[v] = v · count(v)`.

**Two.** The constraint "cannot take both `v` and `v+1`" is *adjacency on the
number line*. So lay the distinct values out in sorted order, weight each by
`points[v]`, and you are looking at **House Robber** — maximum-weight set with
no two adjacent.

```
take[v]  = skip[v-1] + points[v]
skip[v]  = max(take[v-1], skip[v-1])
```

with one wrinkle: the values are sparse. When the next value is **not** `v+1`
there is no conflict at all, so the chain breaks and both states reset to the
best so far. Concretely, the array splits into runs of consecutive integers,
each run solved independently and the results added.

Recognising a familiar problem hiding behind a transformation is the actual
skill being tested; the DP itself is four lines.
""",
        ),
        (
            "Edge cases",
            """
- **Sparse vs bucketed.** LeetCode caps values at 10⁴, so a `points` array
  indexed 0…10⁴ and one linear sweep is O(n + maxValue) and simpler to write.
  Sorting the distinct values is O(n log n) but stays sane if the follow-up
  raises the cap to 10⁹ — say which you are choosing and why.
- **Duplicates are the whole point.** `[2, 2, 3, 3, 3, 4]` → points are
  `{2: 4, 3: 9, 4: 4}`, so the answer is **9**, taking all three 3s. Anyone who
  treats elements individually gets 8 by taking the 2s and the 4.
- **The gap reset.** `[1, 1, 1, 2, 4, 5, 5, 5, 6]` → points
  `{1: 3, 2: 2, 4: 4, 5: 15, 6: 6}`. Run `{1, 2}` contributes 3, run
  `{4, 5, 6}` contributes 15, total **18**. Forget to reset across the gap
  between 2 and 4 and you wrongly forbid taking 4 after 2.
- **Empty array** → 0. **Single element** → that element.
- Values are guaranteed positive, so "take nothing" is never optimal. If
  negatives were allowed you would clamp each run's answer at 0.
""",
        ),
    ],
}


def delete_and_earn(nums: list[int]) -> int:
    points = Counter(nums)
    take, skip = 0, 0  # best for the run so far, ending taken / not taken
    previous: int | None = None

    for value in sorted(points):
        if previous is not None and value != previous + 1:
            # gap: the runs are independent, so bank the finished one
            take = skip = max(take, skip)
        take, skip = skip + value * points[value], max(take, skip)
        previous = value

    return max(take, skip)


CASES = [
    (([3, 4, 2],), 6),
    (([2, 2, 3, 3, 3, 4],), 9),
    (([1, 1, 1, 2, 4, 5, 5, 5, 6],), 18),
    (([1, 2, 3, 4, 5, 6, 7, 8, 9, 10],), 30),
    (([1, 3, 5, 7],), 16),
    (([2, 2, 2],), 6),
    (([8],), 8),
    (([],), 0),
]


def solve(nums: list[int]) -> int:
    return delete_and_earn(nums)
