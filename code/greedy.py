"""Greedy algorithms and the arguments that justify them.

A greedy solution is worthless without a reason it is optimal. The reason is
almost always an **exchange argument**: take any optimal solution, swap its
first choice for the greedy one, and show the result is no worse. If you
cannot construct that argument, the problem is probably dynamic programming.
"""

from __future__ import annotations

from collections import Counter


def can_jump(nums: list[int]) -> bool:
    """Jump Game: can you reach the last index?

    Track the furthest index reachable so far. If the loop ever stands beyond
    it, there is a gap nothing can cross. No DP needed — one variable.
    """
    reach = 0
    for i, jump in enumerate(nums):
        if i > reach:
            return False
        reach = max(reach, i + jump)
    return True


def min_jumps(nums: list[int]) -> int:
    """Jump Game II: fewest jumps to the end.

    This is a BFS by levels, written without a queue. `current_end` is the
    boundary of the current jump; reaching it means one more jump has been
    committed. `farthest` is the boundary of the next level.
    """
    jumps = 0
    current_end = 0
    farthest = 0

    for i in range(len(nums) - 1):
        farthest = max(farthest, i + nums[i])
        if i == current_end:  # must jump now
            jumps += 1
            current_end = farthest

    return jumps


def can_complete_circuit(gas: list[int], cost: list[int]) -> int:
    """Gas Station: the unique start index, or -1.

    Two independent facts. If total gas < total cost, no start works. And if
    you run dry partway from `start`, no station between `start` and here can
    work either — each would begin with even less — so the next candidate is
    the station after the failure. That is what makes it one pass.
    """
    if sum(gas) < sum(cost):
        return -1

    start = 0
    tank = 0
    for i in range(len(gas)):
        tank += gas[i] - cost[i]
        if tank < 0:
            start = i + 1  # skip every station up to and including i
            tank = 0

    return start


def candy(ratings: list[int]) -> int:
    """Each child gets ≥ 1 candy; a higher rating beats both neighbours.

    Two passes, because the constraint points in both directions and no single
    sweep can satisfy both. Left to right fixes the "greater than my left
    neighbour" rule; right to left fixes the mirror, taking a `max` so the
    first pass is not undone.
    """
    n = len(ratings)
    if n == 0:
        return 0

    candies = [1] * n
    for i in range(1, n):
        if ratings[i] > ratings[i - 1]:
            candies[i] = candies[i - 1] + 1

    for i in range(n - 2, -1, -1):
        if ratings[i] > ratings[i + 1]:
            candies[i] = max(candies[i], candies[i + 1] + 1)

    return sum(candies)


def task_scheduler(tasks: list[str], cooldown: int) -> int:
    """Least time to run all tasks with a cooldown between identical ones.

    Not a simulation — a formula. The most frequent task defines a skeleton of
    `(max_count - 1)` gaps of length `cooldown + 1`, plus the tasks tied for
    most frequent at the end. If there are enough distinct tasks to fill every
    idle slot, the answer is simply `len(tasks)`.
    """
    if not tasks:
        return 0

    counts = Counter(tasks)
    max_count = max(counts.values())
    max_count_tasks = sum(1 for count in counts.values() if count == max_count)

    skeleton = (max_count - 1) * (cooldown + 1) + max_count_tasks
    return max(len(tasks), skeleton)


CASES = [
    (([2, 3, 1, 1, 4],), True),
    (([3, 2, 1, 0, 4],), False),
    (([0],), True),
    (([2, 0, 0],), True),
]


def solve(nums: list[int]) -> bool:
    return can_jump(nums)


def check() -> None:
    for args, expected in CASES:
        assert can_jump(*args) == expected

    assert min_jumps([2, 3, 1, 1, 4]) == 2
    assert min_jumps([2, 3, 0, 1, 4]) == 2
    assert min_jumps([0]) == 0

    assert can_complete_circuit([1, 2, 3, 4, 5], [3, 4, 5, 1, 2]) == 3
    assert can_complete_circuit([2, 3, 4], [3, 4, 3]) == -1
    assert can_complete_circuit([5], [4]) == 0

    assert candy([1, 0, 2]) == 5
    assert candy([1, 2, 2]) == 4
    assert candy([1, 3, 2, 2, 1]) == 7  # needs the max() in the second pass
    assert candy([]) == 0

    assert task_scheduler(["A", "A", "A", "B", "B", "B"], 2) == 8
    assert task_scheduler(["A", "A", "A", "B", "B", "B"], 0) == 6
    assert task_scheduler(["A", "A", "A", "B", "C", "D", "E", "F", "G"], 2) == 9
    assert task_scheduler([], 2) == 0
