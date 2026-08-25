"""Two-pointer templates.

Three distinct shapes wear the same name. Knowing which one a problem wants is
most of the work: converging from both ends needs sorted input, same-direction
needs a monotone condition, and fast/slow is really about cycles.
"""

from __future__ import annotations


def three_sum(nums: list[int]) -> list[list[int]]:
    """All unique triples summing to zero.

    Sort, fix one element, then converge two pointers over the rest. The
    dedupe is the whole difficulty: skip repeats of the fixed element, and
    skip repeats of the left pointer *after* recording a hit.
    """
    nums = sorted(nums)
    result: list[list[int]] = []

    for i in range(len(nums) - 2):
        if nums[i] > 0:
            break  # sorted, so nothing further can sum to zero
        if i > 0 and nums[i] == nums[i - 1]:
            continue  # this fixed value was already handled

        left, right = i + 1, len(nums) - 1
        while left < right:
            total = nums[i] + nums[left] + nums[right]
            if total < 0:
                left += 1
            elif total > 0:
                right -= 1
            else:
                result.append([nums[i], nums[left], nums[right]])
                left += 1
                while left < right and nums[left] == nums[left - 1]:
                    left += 1

    return result


def max_area(heights: list[int]) -> int:
    """Container With Most Water — converge from the ends.

    Always move the *shorter* wall. Moving the taller one cannot help: width
    shrinks either way, and the area is capped by the shorter wall, so the
    only chance of improvement is replacing that one. This exchange argument
    is what the interviewer wants said out loud.
    """
    left, right = 0, len(heights) - 1
    best = 0

    while left < right:
        best = max(best, (right - left) * min(heights[left], heights[right]))
        if heights[left] < heights[right]:
            left += 1
        else:
            right -= 1

    return best


def sort_colors(nums: list[int]) -> list[int]:
    """Dutch national flag — partition into three regions in one pass.

    `low` is the boundary of the 0s, `high` of the 2s, `i` scans. The subtle
    part: after swapping with `high` do *not* advance `i`, because the value
    just pulled in from the right has not been examined yet.
    """
    low, i, high = 0, 0, len(nums) - 1

    while i <= high:
        if nums[i] == 0:
            nums[low], nums[i] = nums[i], nums[low]
            low += 1
            i += 1
        elif nums[i] == 2:
            nums[high], nums[i] = nums[i], nums[high]
            high -= 1  # i stays put — the new nums[i] is unexamined
        else:
            i += 1

    return nums


def has_cycle(next_index: list[int], start: int = 0) -> bool:
    """Floyd's tortoise and hare over an index-following sequence.

    The linked-list version is the famous one, but the idea is general: if a
    fast pointer moving two steps ever meets a slow one moving one step, the
    sequence loops. `-1` stands in for a null next.
    """
    slow = fast = start

    while True:
        if next_index[fast] == -1:
            return False
        fast = next_index[fast]
        if next_index[fast] == -1:
            return False
        fast = next_index[fast]
        slow = next_index[slow]
        if slow == fast:
            return True


CASES = [
    (([-1, 0, 1, 2, -1, -4],), [[-1, -1, 2], [-1, 0, 1]]),
    (([0, 0, 0, 0],), [[0, 0, 0]]),
    (([1, 2, 3],), []),
    (([],), []),
]


def solve(nums: list[int]) -> list[list[int]]:
    return three_sum(nums)


def check() -> None:
    for args, expected in CASES:
        assert three_sum(*args) == expected

    assert max_area([1, 8, 6, 2, 5, 4, 8, 3, 7]) == 49
    assert max_area([1, 1]) == 1

    assert sort_colors([2, 0, 2, 1, 1, 0]) == [0, 0, 1, 1, 2, 2]
    assert sort_colors([2, 0, 1]) == [0, 1, 2]
    assert sort_colors([]) == []

    assert has_cycle([1, 2, 3, 1]) is True
    assert has_cycle([1, 2, 3, -1]) is False
