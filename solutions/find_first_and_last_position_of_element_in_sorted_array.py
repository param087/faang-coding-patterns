"""Find First and Last Position of Element in Sorted Array — LeetCode 34."""

from __future__ import annotations

META = {
    "pattern": "binary-search",
    "insight": "Two calls to the same loop, one character apart: lower_bound gives the first index, upper_bound minus one gives the last.",
    "time": "O(log n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
A sorted array with **duplicates**. Return `[first, last]` — the range of
indices holding `target` — or `[-1, -1]`. O(log n) is stated in the problem,
which rules out finding one occurrence and expanding.

This is the reference implementation of the whole pattern. If you can write
`lower_bound` and `upper_bound` from memory and say which one you just wrote,
half the binary-search questions asked at this level collapse into two calls.
""",
        ),
        (
            "The wrong first answer",
            """
Find any occurrence with a plain binary search, then walk left and right to
the ends of the run. It gives the right answer and it is what most people
reach for.

It is also **O(n)**. `[8] * 100000` with target 8: the search lands in the
middle and the two walks cover 10⁵ elements between them — a hundred thousand
steps to answer a question the problem says must take **17**. Duplicates are
not a rare corner here; they are the input the question is built around.

Any per-element scan after a binary search deserves the same suspicion.
""",
        ),
        (
            "The insight",
            """
Do not search for the target. Search for the two **boundaries** of its run,
each of which is an ordinary monotone predicate:

- `lower_bound(target)` — first index with `nums[i] >= target`. The predicate
  `nums[i] >= target` is false then true; the flip is the start of the run.
- `upper_bound(target)` — first index with `nums[i] > target`. Same flip, one
  position past the end of the run.

Same six lines both times. The only difference is `<` versus `<=`:

```
if nums[mid] <  target: low = mid + 1   # lower_bound
if nums[mid] <= target: low = mid + 1   # upper_bound
```

Then `[first, last] = [lower, upper - 1]`. Writing one bespoke loop that
tracks the target with flags and a `best` variable is how a five-minute
question becomes fifteen.
""",
        ),
        (
            "The detail that decides it",
            """
Neither loop can tell you whether the target is present — they return a
boundary regardless. Exactly one check does:

```
first = lower_bound(nums, target)
if first == len(nums) or nums[first] != target:
    return [-1, -1]
```

Both halves are needed. `first == len(nums)` catches a target larger than
everything (`high` starts at `n`, so `first` can legitimately be out of
bounds). `nums[first] != target` catches a target that falls in a gap, like 6
in `[5, 7, 7, 8]` — `lower_bound` returns 1, which points at a 7.

Get that guard right and `upper_bound - 1` needs no check at all: the target
is known present, so the run is non-empty and the last index is real.
""",
        ),
        (
            "Dry run",
            """
`[5, 7, 7, 8, 8, 10]`, target 8.

`lower_bound`, on `[0, 6)`:

- `mid = 3`, `nums[3] = 8`, not `< 8` → `high = 3`.
- `mid = 1`, `nums[1] = 7 < 8` → `low = 2`.
- `mid = 2`, `nums[2] = 7 < 8` → `low = 3`. `low == high == 3`. **First = 3.**

`upper_bound`, on `[0, 6)`:

- `mid = 3`, `nums[3] = 8 <= 8` → `low = 4`.
- `mid = 5`, `nums[5] = 10`, not `<= 8` → `high = 5`.
- `mid = 4`, `nums[4] = 8 <= 8` → `low = 5`. `low == high == 5`.
  **Last = 4.**

Answer `[3, 4]`. Note that `upper_bound` returned 5 — a valid index holding a
different value — and the `- 1` is what makes it the end of the run.
""",
        ),
        (
            "Follow-ups",
            """
- **Count the occurrences** of a value: `upper - lower`, no branching, and it
  is naturally 0 when absent. That is the version that shows up in interviews
  disguised as "how many times does x appear".
- **`bisect` in the standard library**: `bisect_left` and `bisect_right` are
  these two functions, with a `key=` parameter since 3.10. Name them, then
  write the loop — the point of the question is the loop.
- **Rotated array with duplicates** — the boundaries stop being monotone and
  the guarantee degrades to O(n) (LeetCode 81).
- **First and last in a stream or a huge sorted file** where random access is
  a disk seek: identical logic, and now the ~34 total probes instead of a
  linear scan is a real cost saving rather than a complexity class.
""",
        ),
    ],
}


def lower_bound(nums: list[int], target: int) -> int:
    """First index with nums[i] >= target; len(nums) if none."""
    low, high = 0, len(nums)

    while low < high:
        mid = (low + high) // 2
        if nums[mid] < target:
            low = mid + 1
        else:
            high = mid

    return low


def upper_bound(nums: list[int], target: int) -> int:
    """First index with nums[i] > target. One character apart from the above."""
    low, high = 0, len(nums)

    while low < high:
        mid = (low + high) // 2
        if nums[mid] <= target:
            low = mid + 1
        else:
            high = mid

    return low


def search_range(nums: list[int], target: int) -> list[int]:
    first = lower_bound(nums, target)
    if first == len(nums) or nums[first] != target:
        return [-1, -1]  # past the end, or landed in a gap
    return [first, upper_bound(nums, target) - 1]


CASES = [
    (([5, 7, 7, 8, 8, 10], 8), [3, 4]),
    (([5, 7, 7, 8, 8, 10], 6), [-1, -1]),
    (([5, 7, 7, 8, 8, 10], 11), [-1, -1]),
    (([5, 7, 7, 8, 8, 10], 5), [0, 0]),
    (([2, 2, 2, 2], 2), [0, 3]),
    (([-3, -1, -1, 0], -1), [1, 2]),
    (([1], 1), [0, 0]),
    (([], 0), [-1, -1]),
]


def solve(nums: list[int], target: int) -> list[int]:
    return search_range(nums, target)
