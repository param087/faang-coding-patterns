"""Divide Chocolate — LeetCode 1231."""

from __future__ import annotations

META = {
    "pattern": "binary-search-answer",
    "insight": "Maximise-the-minimum is monotone: if every piece can clear sweetness x it can clear x-1, so binary search x and cut greedily.",
    "time": "O(n log(sum))",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
This one is **premium**, so the statement is not public — described here in my
own words. A chocolate bar is an array of chunk sweetness values. You cut it
into `k + 1` **contiguous** pieces (one for each of `k` friends, one for you),
where a piece's sweetness is the sum of its chunks. Your friends hand you the
*least* sweet piece. Maximise it.

Ask two things before writing anything. First: contiguous, or any subset? The
whole problem changes if you may reorder — with reordering it becomes a bin
packing variant and there is no clean answer. Second: is every chunk positive?
Yes on this problem, and that is load-bearing — a negative chunk destroys the
monotonicity the greedy cut relies on.
""",
        ),
        (
            "The insight",
            """
"Maximise the minimum" is the tell. Do not try to *construct* the optimal set
of cuts; **guess the answer and test it**.

Define `feasible(x)` = "can the bar be cut into at least `k + 1` pieces each of
sweetness `>= x`?" That predicate is monotone downwards: if you can achieve a
floor of `x`, the same cuts achieve a floor of `x - 1`. So the feasible values
form a *prefix* of the range and you binary search for the last one.

The check itself is a single greedy sweep: accumulate chunks and close a piece
the instant the running sum reaches `x`. Greedy is optimal here because closing
a piece as early as possible leaves the largest possible remainder for the
pieces still to come, and never reduces the count. Note `>= k + 1`, not `== k + 1`
— if the sweep produces *more* than `k + 1` qualifying pieces you simply glue
the extras onto neighbours, which only raises sums.
""",
        ),
        (
            "The bounds, and the mid that bites",
            """
Low is `min(sweetness)` — some piece is at most one chunk, so the floor can
never exceed the smallest chunk when the cuts are maximal. High is
`sum(sweetness) // (k + 1)` — with `k + 1` pieces the smallest cannot beat the
average. Sloppy bounds like `[0, 10**9]` still work but you will be asked to
justify them and there is nothing to say.

The real trap is the loop shape. This searches for the **largest** feasible
value, so `mid` must round **up**:

```python
mid = (low + high + 1) // 2
if feasible(mid):
    low = mid
else:
    high = mid - 1
```

With plain `(low + high) // 2` and `low = mid`, the pair `(low, high) = (5, 6)`
gives `mid = 5`, feasible, `low = 5` — an infinite loop. This is the single
most common way this family of problems is failed in an interview, and it will
not show up until you run it.
""",
        ),
    ],
}


def maximize_sweetness(sweetness: list[int], k: int) -> int:
    def feasible(target: int) -> bool:
        pieces = 0
        current = 0
        for chunk in sweetness:
            current += chunk
            if current >= target:  # close greedily: earliest cut is optimal
                pieces += 1
                current = 0
        return pieces >= k + 1

    low, high = min(sweetness), sum(sweetness) // (k + 1)
    while low < high:
        mid = (low + high + 1) // 2  # round UP: searching for the largest feasible
        if feasible(mid):
            low = mid
        else:
            high = mid - 1

    return low


CASES = [
    (([1, 2, 3, 4, 5, 6, 7, 8, 9], 5), 6),
    (([5, 6, 7, 8, 9, 1, 2, 3, 4], 8), 1),
    (([1, 2, 2, 1, 2, 2, 1, 2, 2], 2), 5),
    (([10, 1, 1, 1, 10], 1), 11),
    (([6, 6, 6, 6], 1), 12),
    (([9, 7, 3], 0), 19),
    (([1, 1, 1, 1], 3), 1),
    (([1], 0), 1),
]


def solve(sweetness: list[int], k: int) -> int:
    return maximize_sweetness(sweetness, k)
