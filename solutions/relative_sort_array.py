"""Relative Sort Array — LeetCode 1122."""

from __future__ import annotations

META = {
    "pattern": "sorting",
    "insight": "The whole problem is the key: rank inside arr2 first, value second, with everything unranked pushed past the end.",
    "time": "O(n log n + m)",
    "space": "O(n + m)",
    "sections": [
        (
            "What it asks",
            """
Sort `arr1` so that elements also present in `arr2` come first, in the order
`arr2` lists them; every remaining element goes at the end in ascending order.
`arr2` has distinct values, all of which occur in `arr1`.

Ask whether `arr1` may contain duplicates of an `arr2` value — it may, and all
copies stay together at that rank.
""",
        ),
        (
            "The insight",
            """
Two ordering rules stacked on top of each other is one **tuple key**:

```
key(x) = (rank[x] if x in arr2 else len(arr2), x)
```

Unranked values get a sentinel rank of `len(arr2)`, which is strictly greater
than every real rank, so they land after everything — and the second component
sorts them ascending among themselves. For ranked values the second component
never fires, because equal ranks mean equal values.

This is the pattern in its purest form: the sort is one line, the thought is
entirely in the key. Reaching for a custom comparator or two separate sorts
plus a concatenation is more code and more places to be wrong.
""",
        ),
        (
            "Follow-ups",
            """
- **Do it in O(n + m).** The constraint is `0 <= arr1[i] <= 1000`, which is
  the standard hint for a counting sort: tally `arr1` into a 1001-slot array,
  emit `count[v]` copies for each `v` in `arr2` (zeroing as you go), then sweep
  the tally left to right for the rest. No comparisons, no log factor.
- **Unbounded values** — the counting sort dies, the tuple key does not. Say
  which one you would ship and why.
- **`arr2` contains values absent from `arr1`** — the key version already
  handles it; the counting version must skip zero counts rather than emit
  nothing-length runs.
- **Stability** — irrelevant here because equal keys mean equal integers, but
  the moment the elements become objects, `sorted` being stable is what keeps
  their input order inside a rank.
""",
        ),
    ],
}


def relative_sort_array(arr1: list[int], arr2: list[int]) -> list[int]:
    rank = {value: index for index, value in enumerate(arr2)}
    unranked = len(arr2)  # sorts after every real rank
    return sorted(arr1, key=lambda x: (rank.get(x, unranked), x))


CASES = [
    (([2, 3, 1, 3, 2, 4, 6, 7, 9, 2, 19], [2, 1, 4, 3, 9, 6]), [2, 2, 2, 1, 4, 3, 3, 9, 6, 7, 19]),
    (([28, 6, 22, 8, 44, 17], [22, 28, 8, 6]), [22, 28, 8, 6, 17, 44]),
    (([2, 1], [1, 2]), [1, 2]),
    (([1, 1, 1], [1]), [1, 1, 1]),
    (([9, 8, 7], [1, 2, 3]), [7, 8, 9]),
    (([5, 4, 3], []), [3, 4, 5]),
    (([], []), []),
]


def solve(arr1: list[int], arr2: list[int]) -> list[int]:
    return relative_sort_array(arr1, arr2)
