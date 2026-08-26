"""Maximum Swap — LeetCode 670."""

from __future__ import annotations

META = {
    "pattern": "greedy",
    "insight": "Fix the leftmost digit that has anything bigger to its right, and swap it with the last occurrence of the biggest such digit.",
    "time": "O(d) over the digits",
    "space": "O(1) — a 10-slot table",
    "sections": [
        (
            "What it asks",
            """
Given a non-negative integer, swap **at most one** pair of digits to make it as
large as possible. Return the resulting number.

At most **one** swap, so this is not "sort the digits descending": `1993` sorts
to `9931`, while the true answer is `9913`. It is also not "swap the largest
digit to the front" — `9973` is already maximal and must come back unchanged.
""",
        ),
        (
            "The insight",
            """
Digit position dominates digit value: improving an earlier position by 1 beats
improving every later position combined. So scan left to right and stop at the
**first** position that can be improved at all — that is the swap, and no other
choice competes with it.

Two sub-decisions follow, and both have a wrong answer that looks right:

- **Which digit to bring in?** The largest that appears anywhere to the right.
  Bringing in merely-larger loses.
- **Which copy of it?** The **last** one. Both copies raise the leading
  position identically, but the digit you send back lands further right when
  you take the later copy, which costs less. This is the whole problem:
  `1993` → take the second 9 → `9913`; taking the first gives `9193`.

A single pass recording the last index of each of the ten digits, then a second
pass trying `9, 8, ..., d+1` at each position, gives O(10·d).
""",
        ),
        (
            "Edge cases",
            """
- **Already maximal** (`9973`, `0`, `11`) — no swap improves it, so return the
  input unchanged. The inner loop must fall through, not force a swap.
- **All digits equal** — same thing; a "swap the min and max" formulation
  wrongly swaps two identical digits, which is harmless here but wrong in
  spirit and breaks the moment you must report *whether* you swapped.
- **Ties for the largest right-hand digit** are exactly the `1993` trap above;
  a `dict` of last indices handles it for free, a dict of *first* indices
  fails it.
- Leading zeros never arise, since a swap that moved a 0 to the front would
  make the number smaller and hence would never be chosen.
- Comparing digits as characters is safe — `'0'..'9'` are contiguous in ASCII
  and order the same as their values.
""",
        ),
    ],
}


def maximum_swap(num: int) -> int:
    digits = list(str(num))
    last = {digit: i for i, digit in enumerate(digits)}  # last occurrence wins

    for i, digit in enumerate(digits):
        for candidate in "987654321":
            if candidate <= digit:
                break  # nothing bigger available for this position
            j = last.get(candidate, -1)
            if j > i:
                digits[i], digits[j] = digits[j], digits[i]
                return int("".join(digits))

    return num  # already maximal


CASES = [
    ((2736,), 7236),
    ((9973,), 9973),  # already maximal, no swap
    ((1993,), 9913),  # must take the LAST 9, not the first
    ((98368,), 98863),
    ((10909,), 90901),
    ((1234,), 4231),
    ((0,), 0),
    ((11,), 11),
]


def solve(num: int) -> int:
    return maximum_swap(num)
