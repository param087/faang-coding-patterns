"""Next Greater Element II — LeetCode 503."""

from __future__ import annotations

META = {
    "pattern": "monotonic-stack",
    "insight": "Circularity costs one line: run the same stack over 2n steps with i % n, and push only during the first lap.",
    "time": "O(n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
For every element of a **circular** array, return the first strictly greater
element found by walking right and wrapping around; `-1` if the search comes
back to where it started.

Ask whether the wrap is a single lap (it is — you never need to pass an element
twice, because if nothing in a full circle beats it, nothing ever will).
""",
        ),
        (
            "The insight",
            """
Take the linear template unchanged and feed it the array twice. Iterating
`i` over `range(2 * n)` and reading `nums[i % n]` is exactly "walk one more
lap", and one extra lap is provably enough: an element's next greater value, if
it exists, is within `n - 1` steps.

Concatenating `nums + nums` into a real list works too, and is 2n extra memory
for nothing. `i % n` costs a modulo.
""",
        ),
        (
            "The push guard",
            """
The line that decides this problem is:

```python
if i < n:
    stack.append(i)
```

Second-lap indices must be allowed to **pop** but never to be **pushed**. Push
them and duplicates enter the stack, an element becomes its own answer through
the wrap, and the stack no longer drains — you get wrong answers on
`[5, 4, 3, 2, 1]`, where the correct output is `[-1, 5, 5, 5, 5]`.

Two more details:

- The pop test is strict (`<`). `[1, 1, 1]` must return `[-1, -1, -1]`: equal is
  not greater, and a non-strict test would have each 1 answer the others.
- Store **indices**, not values. `result[stack.pop()] = value` needs a slot to
  write into, and after `% n` a value alone no longer tells you where it came
  from.
""",
        ),
    ],
}


def next_greater_elements(nums: list[int]) -> list[int]:
    n = len(nums)
    result = [-1] * n
    stack: list[int] = []  # indices, values decreasing bottom -> top

    for i in range(2 * n):
        value = nums[i % n]
        while stack and nums[stack[-1]] < value:  # strict: equal is not greater
            result[stack.pop()] = value
        if i < n:  # second lap may pop, never push
            stack.append(i)

    return result


CASES = [
    (([1, 2, 1],), [2, -1, 2]),
    (([1, 2, 3, 4, 3],), [2, 3, 4, -1, 4]),
    # The wrap carries the answer all the way back: only the maximum returns -1.
    (([5, 4, 3, 2, 1],), [-1, 5, 5, 5, 5]),
    # Equal is not greater.
    (([1, 1, 1],), [-1, -1, -1]),
    # Negatives, and a tail that can only be answered by wrapping.
    (
        ([100, 1, 11, 1, 120, 111, 123, 1, -1, -100],),
        [120, 11, 120, 120, 123, 123, -1, 100, 100, 100],
    ),
    (([1],), [-1]),
    (([],), []),
]


def solve(nums: list[int]) -> list[int]:
    return next_greater_elements(nums)
