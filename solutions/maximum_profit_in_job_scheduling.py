"""Maximum Profit in Job Scheduling — LeetCode 1235."""

from __future__ import annotations

from bisect import bisect_right

META = {
    "pattern": "dp-advanced",
    "insight": "Sort by end time so the best answer is monotone in time, then binary search for the last job that fits before this one.",
    "time": "O(n log n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Each job has a start, an end and a profit. Pick a subset with no two jobs
overlapping in time, maximising total profit. A job ending at `t` and one
starting at `t` do **not** overlap — confirm that, because the whole
tie-breaking rule hangs on it.

This is weighted interval scheduling. The unweighted version (most jobs) is the
classic greedy "take the earliest finisher". State that, then say why it breaks
here: one fat job can outweigh three thin ones, so greedy on end time is wrong
the moment profits differ. `start = [1,2,3,3]`, `end = [3,4,5,6]`,
`profit = [50,10,40,70]` → greedy takes 50 + 40 = 90; the answer is
**120** (50 + 70).
""",
        ),
        (
            "The insight",
            """
**Sort by end time.** That single decision is the problem. Once jobs are
ordered by when they finish, define

```
dp[i] = best profit achievable using only the first i jobs
```

and `dp` is **non-decreasing**, because using fewer jobs is always an option.
For job `i` you either skip it (`dp[i-1]`) or take it, in which case every
compatible earlier job ends at or before `start[i]` — and since ends are sorted,
those are exactly a **prefix**, found by one binary search:

```
k = bisect_right(ends, start_i)
dp[i] = max(dp[i - 1], dp[k] + profit_i)
```

`bisect_right`, not `bisect_left`: a job ending exactly at `start_i` is
compatible and must be included in the prefix. Getting that backwards silently
loses profit on every back-to-back pair, and the sample above will not catch it.

Sorting by **start** time instead leads to a working but clumsier recurrence
(you search forward and recurse from the right). Sorting by start with a
forward `dp` and no search is the version that quietly produces wrong answers.
""",
        ),
        (
            "Edge cases",
            """
- **Empty input** → 0. **One job** → its profit (profits are positive here; if
  they could be negative, `max(dp[i-1], …)` still handles it — that is why the
  skip branch is written explicitly rather than assumed).
- **Identical intervals** with different profits: only one can be taken, and the
  `max` picks the better. Include a case like `start=[1,1,1]`, `end=[2,3,4]`,
  `profit=[5,6,4]` → 6.
- **Nested intervals** `[1,10]` versus `[2,3]` and `[4,5]`: the fat outer job
  must lose if the two inner ones beat it. A solution that binary-searches
  against *start* times gets this wrong.
- **The heap variant.** Instead of `dp` + `bisect`, sweep jobs by start time
  with a min-heap keyed on end time, popping finished jobs into a running best.
  Same O(n log n); worth knowing because it generalises to "at most k machines"
  where the array DP does not.
""",
        ),
    ],
}


def job_scheduling(start_time: list[int], end_time: list[int], profit: list[int]) -> int:
    jobs = sorted(zip(end_time, start_time, profit, strict=True))

    ends = [0]  # ends[i] = finish time of the i-th job in sorted order
    best = [0]  # best[i] = max profit using the first i jobs

    for end, start, gain in jobs:
        # Last job that finishes at or before this one starts.
        k = bisect_right(ends, start) - 1
        ends.append(end)
        best.append(max(best[-1], best[k] + gain))

    return best[-1]


CASES = [
    (([1, 2, 3, 3], [3, 4, 5, 6], [50, 10, 40, 70]), 120),
    (([1, 2, 3, 4, 6], [3, 5, 10, 6, 9], [20, 20, 100, 70, 60]), 150),
    (([1, 1, 1], [2, 3, 4], [5, 6, 4]), 6),
    (([], [], []), 0),
    (([1], [2], [7]), 7),
    (([1, 2, 4], [10, 3, 5], [9, 5, 5]), 10),
    (([1, 2, 4], [10, 3, 5], [20, 5, 5]), 20),
    (([1, 3, 5, 7], [3, 5, 7, 9], [1, 1, 1, 1]), 4),
]


def solve(start_time: list[int], end_time: list[int], profit: list[int]) -> int:
    return job_scheduling(list(start_time), list(end_time), list(profit))
