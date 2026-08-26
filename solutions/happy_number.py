"""Happy Number — LeetCode 202."""

from __future__ import annotations

META = {
    "pattern": "math-geometry",
    "insight": "The digit-square map is a function, so repeating it walks a rho-shaped path — this is cycle detection, not number theory.",
    "time": "O(log n) to shrink into [1, 243], then O(1) — the tail below 1000 is bounded",
    "space": "O(1) with Floyd, O(log n) with a seen-set",
    "sections": [
        (
            "What it asks",
            """
Repeatedly replace `n` by the sum of the squares of its digits. `n` is *happy*
if this reaches 1, unhappy if it loops forever.

The clarifying question that matters: **how do I know "forever" is
detectable?** If the sequence could run off to infinity there would be no
algorithm at all. It cannot, and the argument for why is the interesting half
of this problem — see the last section.
""",
        ),
        (
            "The insight",
            """
`n → sum of squared digits` is a **function**: every value has exactly one
successor. Iterating a function on a finite set always produces a path that
runs into a cycle — the "rho" shape. So the question "does it loop?" is
literally the linked-list cycle question, and the same two tools apply:

- **A `seen` set** — obvious, O(1) per step, and uses memory proportional to
  the tail length. Perfectly acceptable; write this first if you are short of
  time.
- **Floyd's tortoise and hare** — advance one pointer by one step and the
  other by two. They meet inside the cycle. **O(1) space**, and offering it
  unprompted is what separates this from a five-line warm-up.

The termination condition is `fast == 1`, not `slow == fast`, because `1` is
itself a fixed point (`1 → 1`), so a happy number's "cycle" has length 1 and
both tests would fire. Check for 1 first.
""",
        ),
        (
            "Why it must terminate",
            """
This is the part interviewers actually probe.

For a `d`-digit number the successor is at most `81d` — every digit is at most
9, and `9² = 81`. So:

| digits | largest input | largest successor |
|---|---|---|
| 4 | 9999 | 324 |
| 3 | 999 | 243 |

Any number with 4 or more digits **strictly shrinks**, because `81d < 10^(d-1)`
for `d ≥ 4`. So within a handful of steps every input drops below 1000, and
from there the successor never exceeds 243. The whole sequence is trapped in
`[1, 243]` — a finite set of 243 states — so it must repeat.

Better still, the trap has exactly **one** non-trivial cycle:

```
4 → 16 → 37 → 58 → 89 → 145 → 42 → 20 → 4
```

Which means a legitimate O(1)-space, O(1)-extra-state solution is
`while n != 1 and n != 4: n = next(n)`. It is correct, it is fast, and it is
a bad interview answer on its own — it is a memorised fact, not a method.
Mention it *after* Floyd, as a "if I knew the domain" aside.
""",
        ),
    ],
}


def square_digit_sum(n: int) -> int:
    total = 0
    while n:
        n, digit = divmod(n, 10)
        total += digit * digit
    return total


def is_happy(n: int) -> bool:
    slow, fast = n, square_digit_sum(n)

    # Test for 1 first: 1 is a fixed point, so slow == fast fires there too.
    while fast != 1 and slow != fast:
        slow = square_digit_sum(slow)
        fast = square_digit_sum(square_digit_sum(fast))

    return fast == 1


CASES = [
    ((19,), True),
    ((2,), False),
    ((1,), True),
    ((7,), True),
    ((4,), False),
    ((100,), True),
    ((1111111,), True),
    ((116,), False),
]


def solve(n: int) -> bool:
    return is_happy(n)
