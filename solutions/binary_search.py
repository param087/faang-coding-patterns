"""Binary Search — LeetCode 704."""

from __future__ import annotations

META = {
    "pattern": "binary-search",
    "insight": "Commit to one invariant — the answer lives in the half-open range [low, high) — and every bound becomes a variation of the same six lines.",
    "time": "O(log n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
A sorted array of **distinct** integers. Return the index of `target`, or −1.
O(log n) is required, so `nums.index(target)` is not an answer.

Nothing here is hard. It is asked as a warm-up, or as the five minutes before
the real question, and the only way to fail it is to write a loop you have not
memorised and then debug it live.

Worth confirming: sorted **ascending** (yes), distinct (yes — with duplicates
"the index" is ambiguous and you want LeetCode 34 instead).
""",
        ),
        (
            "The insight",
            """
Every iteration, `nums[mid]` tells you which side of `mid` the target can be
on, so half the remaining range disappears. 10⁵ elements → 17 comparisons.

Pick **one** invariant and never deviate:

> The answer, if it exists, is in `[low, high)` — low inclusive, high
> exclusive.

That fixes all three decisions at once. `high` starts at `len(nums)`, the loop
runs `while low < high`, and the two updates are `low = mid + 1` (mid ruled
out) and `high = mid` (mid ruled out, and it is already excluded by the
bound). When the range is empty the loop ends on its own.

The closed `[low, high]` variant with `while low <= high` and `high = mid - 1`
is equally correct. What is not correct is mixing them, which is exactly what
happens when you re-derive it under pressure.
""",
        ),
        (
            "The three places it breaks",
            """
1. **Loop condition against the update.** `while low <= high` with
   `high = mid` spins forever the moment `low == high == mid`. Pair the
   condition with the bound, always.
2. **Overflow.** `(low + high) // 2` is safe in Python because ints are
   arbitrary precision. In Java or C++ it overflows at 2³¹, which is the bug
   that sat in the JDK's own `binarySearch` for nine years. Write
   `low + (high - low) // 2` if you are on a whiteboard in another language,
   and say why.
3. **The empty array.** `len(nums) == 0` gives `low == high == 0`, the loop
   body never runs, and you return −1. That falls out of the invariant — if
   you needed an `if not nums` guard, your bounds are wrong.
""",
        ),
    ],
}


def search(nums: list[int], target: int) -> int:
    low, high = 0, len(nums)  # half-open: the answer, if any, is in [low, high)

    while low < high:
        mid = (low + high) // 2
        if nums[mid] < target:
            low = mid + 1  # mid ruled out, everything left of it too
        elif nums[mid] > target:
            high = mid  # mid ruled out, and high is exclusive
        else:
            return mid

    return -1


CASES = [
    (([-1, 0, 3, 5, 9, 12], 9), 4),
    (([-1, 0, 3, 5, 9, 12], 2), -1),
    (([-1, 0, 3, 5, 9, 12], -1), 0),
    (([-1, 0, 3, 5, 9, 12], 12), 5),
    (([5], 5), 0),
    (([5], -5), -1),
    (([1, 2], 2), 1),
    (([], 3), -1),
]


def solve(nums: list[int], target: int) -> int:
    return search(nums, target)
