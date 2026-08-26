"""Jump Game III — LeetCode 1306."""

from __future__ import annotations

from collections import deque

META = {
    "pattern": "graph-traversal",
    "insight": "Each index is a node with at most two out-edges, i +/- arr[i]; the question is plain reachability, not jumping strategy.",
    "time": "O(n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Start at index `start` in an array of non-negative integers. From index `i`
you may jump to `i + arr[i]` or `i - arr[i]`, never outside the array. Return
whether you can reach **any** index holding 0.

Ask whether values can be negative (they cannot — the constraint is
`0 <= arr[i] < n`, and it matters, because a negative value would make the two
jump directions overlap in a way that changes nothing here but confuses the
bounds check).
""",
        ),
        (
            "The insight",
            """
The name says "Jump Game", so people reach for the greedy from I and II or
start writing a DP over reachable ranges. Both are the wrong shape. Here the
jump length is **fixed by the cell you are standing on** — there is no choice
of distance, only of sign — so the array is a directed graph with `n` nodes
and at most `2n` edges, and the question is nothing but *is a zero-valued node
reachable from `start`*.

That is one traversal, BFS or DFS, in O(n + 2n) = O(n) time. Once you name it
as reachability the code writes itself, and you have said the thing the
interviewer is listening for.

Not needing shortest path is the giveaway: no distance is asked, so BFS and
DFS are interchangeable and you should say so.
""",
        ),
        (
            "The visited set is the entire problem",
            """
Skip it and the traversal does not merely get slow, it **hangs**. `[2, 2, 2, 2]`
from index 0 bounces 0 → 2 → 0 → 2 forever, and the correct answer is False.
Any value that jumps you back to where you came from does this, and a cycle
like that is the common case rather than the exotic one.

Two ways to mark visited:

- a `bool` array or a set — clean, O(n) extra space;
- or negate `arr[i]` in place for O(1) extra space, which is the follow-up
  they ask for. It works because values are guaranteed non-negative, so a
  negative entry is unambiguously "seen" — but it **mutates the caller's
  array**, so say that out loud and offer to restore it.

Also worth stating: `arr[start] == 0` is an immediate True, and a
single-element `[0]` is True while `[1]` alone is False.
""",
        ),
    ],
}


def can_reach(arr: list[int], start: int) -> bool:
    n = len(arr)
    if not 0 <= start < n:
        return False

    seen = [False] * n
    seen[start] = True
    queue: deque[int] = deque([start])

    while queue:
        i = queue.popleft()
        if arr[i] == 0:
            return True
        for j in (i + arr[i], i - arr[i]):
            if 0 <= j < n and not seen[j]:
                seen[j] = True  # mark on push: never queue an index twice
                queue.append(j)

    return False


CASES = [
    (([4, 2, 3, 0, 3, 1, 2], 5), True),
    (([4, 2, 3, 0, 3, 1, 2], 0), True),
    (([3, 0, 2, 1, 2], 2), False),
    (([2, 2, 2, 2], 0), False),  # cycles forever without the visited marks
    (([0], 0), True),
    (([1], 0), False),
    (([1, 1, 1, 1, 1], 0), False),  # reaches every index, none of them zero
    (([2, 1, 0], 0), True),
]


def solve(arr: list[int], start: int) -> bool:
    return can_reach(list(arr), start)
