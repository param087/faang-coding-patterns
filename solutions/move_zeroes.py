"""Move Zeroes — LeetCode 283."""

from __future__ import annotations

META = {
    "pattern": "two-pointers",
    "insight": "Compact the non-zeros forwards with a write pointer, then blank the tail — order is preserved for free.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Push every zero to the end **in place**, keeping the non-zero values in their
original relative order.

That last clause is the problem. Without it, this is the Dutch-flag partition
in three lines. With it, you need a **stable** compaction, and the obvious
end-to-end swap is disqualified.
""",
        ),
        (
            "The insight",
            """
Forget "moving zeroes". Compact the **non-zeros** to the front with a write
pointer, then fill everything from `write` onwards with 0.

```
[0, 1, 0, 3, 12]  ->  compact: [1, 3, 12, ...]  ->  pad: [1, 3, 12, 0, 0]
```

`write` never overtakes `read`, so each slot is read before it is written.
Stability is automatic: the non-zeros are copied in the order they are met.

Total writes: at most n in the compaction plus the number of zeros in the pad.
""",
        ),
        (
            "The pitfall: swap vs overwrite",
            """
The popular one-pass variant swaps rather than overwriting:

```python
if nums[read]:
    nums[write], nums[read] = nums[read], nums[write]
    write += 1
```

It is correct and also stable — but it performs a **swap on every non-zero**,
including when `write == read`, which is the common case. On an array with no
zeros at all that is n pointless three-way exchanges where the two-pass version
does zero writes.

If the interviewer says "minimise writes to memory" — a real constraint when
the array is flash-backed — the two-pass version wins, and guarding the swap
with `if write != read` is the middle ground. Know which one you are defending.

The genuinely wrong answer is swapping from the ends (`[0, 1]` handled by
trading the front zero with the back element): fast, O(1), and it destroys the
relative order the problem demands.
""",
        ),
    ],
}


def move_zeroes(nums: list[int]) -> list[int]:
    write = 0

    for read in range(len(nums)):
        if nums[read] != 0:
            nums[write] = nums[read]  # write <= read, so nothing unread is clobbered
            write += 1

    for i in range(write, len(nums)):
        nums[i] = 0

    return nums


CASES = [
    (([0, 1, 0, 3, 12],), [1, 3, 12, 0, 0]),
    (([0],), [0]),
    (([1, 2, 3],), [1, 2, 3]),  # no zeros: the pad loop must not run
    (([0, 0, 0],), [0, 0, 0]),
    (([],), []),
    (([0, 0, 1],), [1, 0, 0]),
    (([1, 0, 2, 0, 3, 0],), [1, 2, 3, 0, 0, 0]),
    (([-1, 0, -2],), [-1, -2, 0]),  # negatives are not zeros
]


def solve(nums: list[int]) -> list[int]:
    return move_zeroes(list(nums))  # copy: the algorithm mutates in place
