"""Sum of Two Integers — LeetCode 371."""

from __future__ import annotations

META = {
    "pattern": "bit-manipulation",
    "insight": "a ^ b is the sum with every carry dropped and (a & b) << 1 is those carries, so re-add the two until no carry is left.",
    "time": "O(1) — at most 32 rounds",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Return `a + b` without using `+` or `-`.

It is a hardware question in disguise: reimplement a ripple-carry adder. The
constraints on LeetCode are small (|a|, |b| ≤ 1000), which is a red herring —
**the difficulty is entirely in the negatives**, and in Python it is in the
language.

Two questions worth asking, in this order:

1. **What integer width am I emulating?** 32-bit signed. Without a width the
   problem has no well-defined answer for negatives.
2. **Which language?** In Java, C++ or Go this is five lines and the wrap-
   around is free. In Python it is genuinely different, and saying so up front
   is a strong signal rather than an excuse.
""",
        ),
        (
            "The insight",
            """
Split addition into the two things a full adder does:

- **Sum without carry**: `a ^ b`. Column by column, `1 + 1` gives 0 and `1 + 0`
  gives 1 — XOR is addition mod 2 per column.
- **The carries**: `a & b` marks every column where both bits were 1, and a
  carry belongs one column to the **left**, hence `(a & b) << 1`.

Then add those two together — with the same routine, recursively:

```python
while b:
    a, b = a ^ b, (a & b) << 1
```

It terminates because each round shifts the carry at least one position left,
so after at most 32 rounds the carry has fallen off the end of the word. Not
"usually fast" — bounded at 32.

Subtraction comes free once you have this: `a - b == a + (~b + 1)`.
""",
        ),
        (
            "Why the naive Python loop hangs",
            """
Write that loop with `a = -1, b = 1` in Python and it does not return a wrong
answer, and it is not slow: **it never terminates.**

```
a = -1, b = 1   →  a ^ b = -2,  carry = (-1 &  1) << 1 = 2
a = -2, b = 2   →  a ^ b = -4,  carry = (-2 &  2) << 1 = 4
a = -4, b = 4   →  a ^ b = -8,  carry = (-4 &  4) << 1 = 8
...
```

Python integers are unbounded and behave as if two's complement extends
infinitely leftwards, so a negative operand supplies an endless run of 1 bits
for the carry to keep propagating into. The carry doubles every round and
never reaches zero. In Java the same loop finishes because the carry shifts
out of bit 31 and is discarded — **the overflow you are taught to fear is what
makes the algorithm halt.**

If you have ever wondered why this Easy-adjacent problem has a poor acceptance
rate in Python, that is why.
""",
        ),
        (
            "The mask, and getting the sign back",
            """
Emulate the missing width by hand. Two lines of ceremony:

```python
MASK = 0xFFFFFFFF        # keep exactly 32 bits
MAX_INT = 0x7FFFFFFF     # largest positive 32-bit signed value
```

- **Mask after every step.** `a &= MASK`, and mask the carry too, so anything
  above bit 31 is thrown away exactly as hardware would.
- **Reinterpret at the end.** After the loop `a` is an *unsigned* 32-bit
  pattern. If it exceeds `MAX_INT`, bit 31 is set and the intended value is
  negative, so convert:

```python
return a if a <= MAX_INT else ~(a ^ MASK)
```

`a ^ MASK` flips all 32 bits and `~` of that is the two's-complement negative
— the same value as `a - 2**32`, but written **without a minus sign**, which
matters because the problem bans `-`. That detail is the difference between a
solution that survives the interviewer reading it and one that does not.

Do not mask the *return* value: masking is for the loop's arithmetic, sign
extension is for the result.
""",
        ),
        (
            "Dry run",
            """
**`1 + 3`** — the carry chains twice:

| a | b | a ^ b | (a & b) << 1 |
| --- | --- | --- | --- |
| 001 | 011 | 010 | 010 |
| 010 | 010 | 000 | 100 |
| 100 | 000 | — | — |

Answer `100` = **4**. Note the second round: the carry created a *new* carry.
That is exactly the ripple, and it is why one pass is not enough.

**`-1 + 1`** with the mask: `a = 0xFFFFFFFF`, `b = 1`. The carry walks up the
word one bit per round — 32 rounds — and on the last one `(a & b) << 1`
overflows bit 31, the mask discards it, `b` becomes 0 and `a` is 0. Answer
**0**. That single case is the whole reason for the mask, and it is the case
to test first.
""",
        ),
        (
            "Follow-ups",
            """
- **Subtract without `-`**: `a - b = get_sum(a, get_sum(~b, 1))`. `~b + 1` is
  two's-complement negation, and you already own `+`.
- **Multiply without `*`**: shift-and-add — for each set bit `i` of `b`, add
  `a << i`. That is Russian peasant multiplication, and it is the same adder
  underneath.
- **Divide without `/`** ([Divide Two Integers](../divide-two-integers/)):
  repeated doubling of the divisor, plus the `INT_MIN / -1` overflow special
  case. Same family, and a much more common interview question.
- **"Why does the carry loop always terminate?"** Each iteration moves the
  lowest possible carry position strictly left, and there are only 32
  positions. Worth being able to state as a bound, not a hope.
""",
        ),
    ],
}

MASK = 0xFFFFFFFF
MAX_INT = 0x7FFFFFFF


def get_sum(a: int, b: int) -> int:
    a &= MASK
    b &= MASK

    while b:  # b holds the pending carries
        carry = ((a & b) << 1) & MASK  # masking is what makes this terminate
        a = (a ^ b) & MASK  # sum with carries dropped
        b = carry

    # a is now an unsigned 32-bit pattern; reinterpret it as signed.
    return a if a <= MAX_INT else ~(a ^ MASK)


def subtract(a: int, b: int) -> int:
    """a - b, still without + or -: negate b in two's complement, then add."""
    return get_sum(a, get_sum(~b & MASK, 1))


CASES = [
    ((1, 2), 3),
    ((2, 3), 5),  # the carry ripples twice
    ((0, 0), 0),
    ((-2, 3), 1),
    ((-1, 1), 0),  # the case the unmasked Python loop hangs on
    ((-5, -7), -12),
    ((1000, -1000), 0),
    ((-2147483648, 1), -2147483647),  # INT_MIN, sign bit set throughout
    ((2147483647, -1), 2147483646),  # INT_MAX
]


def solve(a: int, b: int) -> int:
    return get_sum(a, b)


def check() -> None:
    for args, expected in CASES:
        assert get_sum(*args) == expected

    # Exhaustive-ish agreement with real addition across signs and magnitudes.
    values = [0, 1, 2, 7, 1000, 65535, 1 << 20, MAX_INT, -1, -2, -1000, -(1 << 20), -MAX_INT - 1]
    for a in values:
        for b in values:
            if -(1 << 31) <= a + b <= MAX_INT:  # stay inside the 32-bit word
                assert get_sum(a, b) == a + b, (a, b)
            if -(1 << 31) <= a - b <= MAX_INT:
                assert subtract(a, b) == a - b, (a, b)
