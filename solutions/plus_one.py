"""Plus One — LeetCode 66."""

from __future__ import annotations

META = {
    "pattern": "math-geometry",
    "insight": "A carry only travels through nines, so return at the first digit below nine — and the array only grows when every digit was nine.",
    "time": "O(n), and O(1) amortised on random input since the carry usually dies immediately",
    "space": "O(n) for the returned list, O(1) beyond it",
    "sections": [
        (
            "What it asks",
            """
A non-negative integer is given as an array of decimal digits, most
significant first, with no leading zeros. Add one and return the digit array.

The reason this exists as a question is that the number does **not** fit in a
machine integer — that is the whole point of the array representation. So the
answer that joins the digits, `int()`s them, adds one and splits again is a
non-answer for the intended input size, even though Python would happily run
it. Say why you are not doing that.
""",
        ),
        (
            "The insight",
            """
Adding one is the degenerate case of schoolbook addition, and its carry
behaviour is much simpler than general addition: **the carry is always exactly
1, and it dies at the first digit that is not 9**.

So walk from the right:

- digit `< 9` → increment it and return immediately, nothing to the left moves;
- digit `== 9` → it becomes `0` and the carry continues.

Falling out of the loop means every digit was a 9, so the value was
`10^n - 1` and the answer is `1` followed by `n` zeros. That is the only way
the array grows, and it grows by exactly one element — there is no need for a
general "resize by carry length" argument.
""",
        ),
        (
            "Edge cases",
            """
- **All nines** — `[9]` → `[1, 0]`, `[9, 9, 9]` → `[1, 0, 0, 0]`. This is the
  case a `for` loop with no post-loop handling silently gets wrong, returning
  `[0, 0, 0]`. Write the `return [1, *digits]` line before you write the loop.
- **`[0]`** — the one legal input with a leading zero, since the number zero
  has to be written somehow. Returns `[1]`; the general code handles it.
- **Carry stopping mid-array** — `[1, 9, 9]` → `[2, 0, 0]`. Worth stating that
  the loop is O(1) on almost all inputs: 90% of the time the last digit is not
  a 9 and you return on the first iteration.
- **Purity** — the in-place version mutates the caller's array. Fine on
  LeetCode, a bug in real code and a bug if a grader reuses the input. Copy
  first; it costs the O(n) you are already paying for the result.
- **The real follow-up** is *Add Strings* or *Add Two Numbers*, where the
  addend is arbitrary and the carry can be 0 or 1 at every position. The
  early-return trick disappears there — do not carry it over.
""",
        ),
    ],
}


def plus_one(digits: list[int]) -> list[int]:
    result = list(digits)  # never mutate the caller's array

    for i in range(len(result) - 1, -1, -1):
        if result[i] < 9:
            result[i] += 1
            return result  # carry dies here, everything left of i is untouched
        result[i] = 0

    return [1, *result]  # every digit was a 9: 10^n - 1 becomes 10^n


CASES = [
    (([1, 2, 3],), [1, 2, 4]),
    (([4, 3, 2, 1],), [4, 3, 2, 2]),
    (([9],), [1, 0]),
    (([9, 9, 9],), [1, 0, 0, 0]),
    (([0],), [1]),
    (([1, 9, 9],), [2, 0, 0]),
    (([2, 9],), [3, 0]),
    (([8, 9, 9, 9],), [9, 0, 0, 0]),
]


def solve(digits: list[int]) -> list[int]:
    return plus_one(digits)  # plus_one already copies, so CASES survive reruns
