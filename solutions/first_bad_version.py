"""First Bad Version — LeetCode 278."""

from __future__ import annotations

from collections.abc import Callable

META = {
    "pattern": "binary-search",
    "insight": "The versions are a sorted array of booleans you never materialise — binary search the predicate, not the data.",
    "time": "O(log n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Versions `1..n` ship in order. Once one is bad every later one is bad. An API
`isBadVersion(v)` tells you about a single version, and you must find the
first bad one using as few calls as possible.

The API here is a stand-in for something expensive: a bisect over commits, a
canary deploy, a query against a service. That framing is the reason the
question exists — the cost model is **API calls**, not array accesses.
""",
        ),
        (
            "The insight",
            """
`isBadVersion` is **monotone**: `False ... False True ... True`. That is a
sorted boolean array, so it is binary-searchable even though it does not exist
in memory.

It is `lower_bound` on the predicate:

```
if is_bad(mid): high = mid    # mid might be the first bad one — keep it
else:           low = mid + 1 # mid is good, so is everything before it
```

`low` and `high` start at 1 and `n` (versions are 1-indexed, and the answer is
guaranteed to exist, so no exclusive upper bound is needed). The loop ends with
`low == high` on the answer, having made ⌈log₂ n⌉ calls — 31 of them at
n = 2³¹ − 1.

The generalisation is the point: any monotone yes/no question over an ordered
domain is a binary search, whether the domain is an array, a range of integers,
or a build history.
""",
        ),
        (
            "The two bugs graders look for",
            """
1. **`(low + high) // 2` overflows** in Java or C++. With `n = 2³¹ − 1` the
   very first `low + high` wraps negative and the search dies. Python's ints
   are unbounded so this file is safe, but say `low + (high - low) // 2` out
   loud — this problem is *the* canonical place that bug is tested.
2. **Calling the API after the loop.** `while low < high` exits with the
   answer already in `low`; a trailing `if is_bad(low)` is a wasted call, and
   on a bounded-call grader that is the difference between accept and reject.

Also: never write `high = mid - 1` here. `mid` being bad does not rule it out
— it is a *candidate*. That single character is the whole problem.
""",
        ),
    ],
}


def first_bad_version(n: int, is_bad_version: Callable[[int], bool]) -> int:
    low, high = 1, n

    while low < high:
        mid = low + (high - low) // 2  # overflow-safe by habit
        if is_bad_version(mid):
            high = mid  # mid is still a candidate
        else:
            low = mid + 1  # mid is good, discard it and everything before

    return low


CASES = [
    ((5, 4), 4),
    ((1, 1), 1),
    ((2, 1), 1),
    ((2, 2), 2),
    ((10, 1), 1),
    ((10, 10), 10),
    ((2126753390, 1702766719), 1702766719),
]


def solve(n: int, bad: int) -> int:
    """`bad` is the hidden first bad version; the search only sees the predicate."""
    return first_bad_version(n, lambda version: version >= bad)
