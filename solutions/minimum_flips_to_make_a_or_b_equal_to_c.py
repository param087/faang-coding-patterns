"""Minimum Flips to Make a OR b Equal to c — LeetCode 1318."""

from __future__ import annotations

META = {
    "pattern": "bit-manipulation",
    "insight": "Bits are independent, so decide each column on its own: a 1 in c costs a flip only if both inputs are 0, a 0 costs one flip per set input.",
    "time": "O(32)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Flip individual bits of `a` and `b` — either direction, any positions — until
`a | b == c`. Return the fewest flips.

Confirm two things: flips go both ways (1→0 as well as 0→1), and `c` is fixed,
you never touch it. If flips were one-directional the problem would be a
different, much fiddlier one.
""",
        ),
        (
            "The insight",
            """
`OR` is computed **bitwise with no carries**, so column `k` of the result
depends only on column `k` of the inputs. There is no interaction between
positions, which means there is nothing to optimise globally — just take the
minimum cost in each column and add them up. Say this explicitly; it is the
whole reason a greedy answer is optimal rather than merely plausible.

Per column, with `x = a_k`, `y = b_k`, `z = c_k`:

| `z` | `x, y` | cost | why |
| --- | ------ | ---- | --- |
| 1 | at least one 1 | 0 | OR already gives 1 |
| 1 | 0, 0 | 1 | flip either one up — one flip suffices |
| 0 | 0, 0 | 0 | already 0 |
| 0 | one 1 | 1 | clear that bit |
| 0 | 1, 1 | 2 | **both** must be cleared |

The `z = 0, x = y = 1` row costing **2** is the only line anyone gets wrong. A
solution that counts differing bits of `(a | b)` against `c` charges 1 there and
comes out under the true answer.

Once you see the table, the loop writes itself, or you can collapse it to two
population counts:

```python
(((a | b) ^ c).bit_count()) + ((a & b & ~c).bit_count())
```

`(a | b) ^ c` charges one flip per mismatched column; `a & b & ~c` adds the
second flip for exactly the double-set-must-clear columns. Handy, but derive
the table first — the formula alone is not an explanation.
""",
        ),
        (
            "Edge cases",
            """
- **Any operand zero** — `a = b = 0, c = 7` needs 3 flips; `a = b = 7, c = 0`
  needs 6, because every column pays twice. Having both of those in your head
  is the fastest way to sanity-check the table.
- **Already satisfied** — `a | b == c` gives 0, and the loop returns 0 without a
  special case.
- **Unequal bit lengths** — `c` may be longer than `a | b` or shorter. Loop
  `while a or b or c` (or a fixed 32 rounds) so you never stop early on the
  shorter operand; iterating `range(a.bit_length())` silently drops the high
  bits of `c`.
- **`~c` in the one-liner** — in Python `~c` is negative and infinitely
  sign-extended, so `a & b & ~c` is still correct (the extra high 1-bits of `~c`
  meet zeros in `a & b`), but in a fixed-width language mask it first.
""",
        ),
    ],
}


def min_flips(a: int, b: int, c: int) -> int:
    flips = 0

    while a or b or c:  # run until every operand is exhausted
        bit_a, bit_b, bit_c = a & 1, b & 1, c & 1

        if bit_c:
            flips += 0 if bit_a or bit_b else 1
        else:
            flips += bit_a + bit_b  # both set means two flips

        a >>= 1
        b >>= 1
        c >>= 1

    return flips


CASES = [
    ((2, 6, 5), 3),
    ((4, 2, 7), 1),
    ((1, 2, 3), 0),
    ((0, 0, 0), 0),
    ((0, 0, 7), 3),
    ((7, 7, 0), 6),
    ((8, 3, 5), 3),
]


def solve(a: int, b: int, c: int) -> int:
    return min_flips(a, b, c)
