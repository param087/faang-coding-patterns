"""Jump Game II — LeetCode 45."""

from __future__ import annotations

META = {
    "pattern": "greedy",
    "insight": "It is a breadth-first search written without a queue — current_end is the boundary of the current level.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
From index `i` you may jump up to `nums[i]` steps. Return the **fewest jumps**
to reach the last index.

Ask: is reaching the end guaranteed (yes in Jump Game II — otherwise it is
Jump Game I); can jumps be zero-length (yes); is the answer the count of jumps
rather than of indices visited (jumps).
""",
        ),
        (
            "The DP baseline",
            """
`dp[i]` = fewest jumps to reach `i`, filled by relaxing from every earlier
index that can reach it. O(n²).

Give it — it is correct and it establishes what the greedy is beating.
""",
        ),
        (
            "The insight",
            """
It is a **breadth-first search by levels**, written without a queue.

From everything reachable in `k` jumps, compute everything reachable in
`k + 1`. Two variables track the level boundaries:

- **`current_end`** — the far edge of the current jump. Reaching it means one
  more jump has been committed.
- **`farthest`** — the far edge of the *next* level, accumulated as you scan.

Seeing it as BFS is what makes it obviously correct, and it is a much better
explanation than "we jump when we have to".
""",
        ),
        (
            "The loop bound",
            """
The scan stops at `len(nums) - 1`, not `len(nums)`.

Arriving at the last index does not require another jump. Including it
increments the counter one final, spurious time.
""",
        ),
        (
            "Dry run",
            """
`[2, 3, 1, 1, 4]`

- Level 0 is index 0. From it you reach up to index 2 → that is level 1.
- From indices 1 and 2 you reach up to index 4 → level 2, which contains the
  target.

Answer **2**.

Point at where `i == current_end` fires — that single line is doing all the
work.
""",
        ),
        (
            "Follow-ups",
            """
- **Jump Game I** — can you reach the end at all? One variable: track the
  furthest reachable index, and fail if the loop ever stands beyond it.
- **Jump Game III / IV** — arbitrary jump targets, which really is a
  [BFS](../../patterns/graph-traversal/) with an explicit queue, because the
  reachable set is no longer a contiguous interval.
- **Minimum jumps with a cost per jump** — back to DP.
""",
        ),
    ],
}


def jump(nums: list[int]) -> int:
    jumps = 0
    current_end = 0  # far edge of the current BFS level
    farthest = 0  # far edge of the next level

    # Stop before the last index: arriving there needs no further jump.
    for i in range(len(nums) - 1):
        farthest = max(farthest, i + nums[i])
        if i == current_end:  # exhausted this level — commit a jump
            jumps += 1
            current_end = farthest

    return jumps


CASES = [
    (([2, 3, 1, 1, 4],), 2),
    (([2, 3, 0, 1, 4],), 2),
    (([0],), 0),
    (([1, 2],), 1),
    (([1, 1, 1, 1],), 3),
    (([5, 1, 1, 1, 1],), 1),
]


def solve(nums: list[int]) -> int:
    return jump(nums)
