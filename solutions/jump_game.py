"""Jump Game — LeetCode 55."""

from __future__ import annotations

META = {
    "pattern": "greedy",
    "insight": "Track only the furthest index reachable so far; the first time the scan outruns it, the array is cut in two.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
`nums[i]` is the **maximum** jump length from index `i`. Starting at index 0,
can you reach the last index?

"Maximum, not exact" is the whole problem. If jumps were exact lengths this
would be a reachability search with no greedy structure at all — worth saying
out loud, because it shows you read the constraint rather than the title.
""",
        ),
        (
            "The insight",
            """
You never need to know *which* jumps you took, only **how far you can get**.
Keep one number, `reach = max(reach, i + nums[i])`, and sweep left to right.

Two facts make that sufficient:

- Reachability is a prefix property. If index `i` is reachable at all, every
  index in `[0, i]` is too, because from a smaller `j` with `j + nums[j] >= i`
  you can land on anything in between (jumps are "at most").
- So the reachable set is always a contiguous prefix `[0, reach]`, and a single
  scalar describes it exactly.

The scan fails the moment `i > reach`: nothing at or beyond `i` is reachable,
so the array is severed there and no later element can rescue it. Return early.
""",
        ),
        (
            "Edge cases",
            """
- **A single element** — you are already at the last index, so `True` even if
  `nums == [0]`. A loop that requires a jump to happen gets this wrong.
- **A zero at the last index** is harmless; a zero anywhere else is only fatal
  if nothing earlier jumps over it. `[3, 0, 0, 0]` is `True`.
- **`i > reach` versus `reach >= n - 1`** — the early exits are not symmetric.
  You must break on failure (else `reach` keeps absorbing unreachable elements
  and you return `True` for `[0, 1, 5]`); the success exit is only an
  optimisation.
- The DP that marks each index reachable by scanning back over all predecessors
  is O(n²) — at n = 10⁴ that is 10⁸ operations, and it is the answer people
  write first.
""",
        ),
    ],
}


def can_jump(nums: list[int]) -> bool:
    reach = 0

    for i, jump in enumerate(nums):
        if i > reach:  # severed: nothing from here on is reachable
            return False
        reach = max(reach, i + jump)

    return True


CASES = [
    (([2, 3, 1, 1, 4],), True),
    (([3, 2, 1, 0, 4],), False),  # the 0 at index 3 cannot be jumped over
    (([0],), True),  # already at the last index
    (([0, 1],), False),
    (([3, 0, 0, 0],), True),  # zeros are fine if something clears them
    (([1, 0, 1, 0],), False),
    (([2, 0, 0],), True),  # lands exactly on the last index
    (([1, 1, 1, 1],), True),
]


def solve(nums: list[int]) -> bool:
    return can_jump(nums)
