"""Monotonic stack and monotonic deque templates.

The stack holds indices whose answer is still unknown. When a new element
arrives that resolves them, they pop — and because each index is pushed once
and popped once, the whole scan is O(n) despite the inner while loop.
"""

from __future__ import annotations

from collections import deque


def next_greater(nums: list[int]) -> list[int]:
    """For each index, the next strictly greater value to its right, else -1.

    The template. `stack` holds indices in decreasing order of value; the
    moment `nums[i]` beats the top, that index's answer is `nums[i]`.
    """
    result = [-1] * len(nums)
    stack: list[int] = []  # indices, values decreasing bottom -> top

    for i, value in enumerate(nums):
        # Strict `<` finds the next *strictly* greater. Use `<=` to treat
        # equal neighbours as resolving each other.
        while stack and nums[stack[-1]] < value:
            result[stack.pop()] = value
        stack.append(i)

    return result


def previous_smaller(nums: list[int]) -> list[int]:
    """For each index, the index of the previous strictly smaller value, else -1.

    Same machinery, read from the other side: whatever survives the popping
    when `i` arrives *is* the previous smaller element. This is the half of
    the template people forget, and it is what histogram problems need.
    """
    result = [-1] * len(nums)
    stack: list[int] = []  # indices, values increasing bottom -> top

    for i, value in enumerate(nums):
        while stack and nums[stack[-1]] >= value:
            stack.pop()
        result[i] = stack[-1] if stack else -1
        stack.append(i)

    return result


def sliding_window_max(nums: list[int], k: int) -> list[int]:
    """Maximum of every window of size k, in O(n).

    A monotonic *deque* rather than a stack: the front must also leave once it
    falls out of the window, which a stack cannot express. Values decrease
    front -> back, so the front is always the current window's maximum.
    """
    if k <= 0 or not nums:
        return []

    window: deque[int] = deque()  # indices, values decreasing front -> back
    result: list[int] = []

    for i, value in enumerate(nums):
        # Anything smaller than the incoming value can never be a maximum
        # again — a later window containing it also contains `value`.
        while window and nums[window[-1]] <= value:
            window.pop()
        window.append(i)

        # Evict the front once it is outside [i - k + 1, i].
        if window[0] <= i - k:
            window.popleft()

        if i >= k - 1:
            result.append(nums[window[0]])

    return result


CASES = [
    (([2, 1, 2, 4, 3],), [4, 2, 4, -1, -1]),
    (([5, 4, 3, 2, 1],), [-1, -1, -1, -1, -1]),
    (([1, 2, 3],), [2, 3, -1]),
    (([],), []),
]


def solve(nums: list[int]) -> list[int]:
    return next_greater(nums)


def check() -> None:
    for args, expected in CASES:
        assert next_greater(*args) == expected

    assert previous_smaller([2, 1, 2, 4, 3]) == [-1, -1, 1, 2, 2]
    assert previous_smaller([1, 2, 3]) == [-1, 0, 1]
    assert previous_smaller([3, 2, 1]) == [-1, -1, -1]

    assert sliding_window_max([1, 3, -1, -3, 5, 3, 6, 7], 3) == [3, 3, 5, 5, 6, 7]
    assert sliding_window_max([1], 1) == [1]
    assert sliding_window_max([9, 8, 7], 2) == [9, 8]
    assert sliding_window_max([], 3) == []
