"""Minimum Number of K Consecutive Bit Flips — LeetCode 995."""

from __future__ import annotations

META = {
    "pattern": "sliding-window",
    "insight": "The leftmost remaining 0 can only be fixed by a flip starting exactly there, so carry the flip parity in a window rather than flipping.",
    "time": "O(n)",
    "space": "O(n) — O(1) if you mark inside the input",
    "sections": [
        (
            "What it asks",
            """
A binary array and a fixed width `k`. One move flips every bit in some
contiguous subarray of length exactly `k`. Return the fewest moves to make the
array all `1`s, or `-1` if it cannot be done.

Ask: is `k` fixed for every move (yes — that is the whole constraint), and may
the chosen subarrays overlap (yes, and they must). Note that flips commute and
flipping the same window twice is a no-op, so the answer depends only on the
**set of start indices**, each used at most once.
""",
        ),
        (
            "The insight",
            """
Scan left to right. When you stand at index `i`, every index before it is
already `1` and no future flip can reach backwards past `i` — a flip starting
at `j > i` covers `[j, j + k)`. So if position `i` is currently `0`, the only
move that can ever fix it is the flip starting exactly at `i`. No choice, no
search: the greedy is **forced**, which is also the proof of optimality.

The naive implementation of that greedy actually writes `k` bits per flip:
O(n·k), and at n = 10⁵ with k = 10⁵ that is 10¹⁰ writes.

The fix is to never flip anything. Only the **parity** of flips covering `i`
matters, and the flips covering `i` are exactly those started in the window
`(i - k, i]`. Keep a running counter `active` of flips whose range still covers
the cursor, and a small array recording where each flip expires: at index `i`,
subtract the flips that end there, then test `(nums[i] + active) % 2`. Odd
means the position already reads `1`.

Impossibility is a one-line check: if you need a flip at `i` but `i + k > n`,
there is no window left, so return `-1`. Nothing later can rescue it, because
of the same "no flip reaches backwards" argument.
""",
        ),
        (
            "The trap: mutating the array to track flips",
            """
The popular O(1)-space variant marks a flip by writing a sentinel (say `2`)
into `nums[i]`, then reads it back `k` steps later to decrement `active`. It is
correct and it is what an interviewer means by "can you do it in constant extra
space", but it has two costs worth naming out loud:

- It **destroys the input**. If the caller reuses `nums`, or your test harness
  runs the same case twice, the second run is wrong. That is why `solve` here
  never mutates and the expiry array is separate — a silently stateful solution
  is a far worse bug than an O(n) array.
- The sentinel only works because the alphabet is `{0, 1}`; the moment the
  problem becomes "flip a range of arbitrary integers", the trick evaporates
  while the difference-array version survives unchanged.

Two smaller ways to get this wrong: testing `nums[i] == 0` instead of the
parity `(nums[i] + active) % 2 == 0`, which ignores every flip in effect; and
expiring flips **after** the parity test instead of before, which keeps a flip
alive for one index too many and produces an answer one or two too high on
inputs where flips abut exactly.
""",
        ),
    ],
}


def min_k_bit_flips(nums: list[int], k: int) -> int:
    n = len(nums)
    expiring = [0] * (n + 1)  # expiring[i] = flips whose coverage ends at i
    active = 0  # flips currently covering the cursor
    moves = 0

    for i, bit in enumerate(nums):
        active -= expiring[i]  # retire first, then read

        if (bit + active) % 2 == 0:  # this position still reads 0
            if i + k > n:
                return -1  # no window of width k starts here
            moves += 1
            active += 1
            expiring[i + k] += 1

    return moves


CASES = [
    (([0, 1, 0], 1), 2),
    (([1, 1, 0], 2), -1),  # the trailing 0 has no room
    (([0, 0, 0, 1, 0, 1, 1, 0], 3), 3),  # overlapping flips, parity matters
    (([0, 0, 1, 0, 0, 0, 0, 0], 3), 3),
    (([1, 1, 1], 3), 0),
    (([0, 1], 2), -1),  # one flip is possible but makes it worse
    (([0, 0], 2), 1),
    (([1], 1), 0),
    (([], 1), 0),
]


def solve(nums: list[int], k: int) -> int:
    return min_k_bit_flips(list(nums), k)
