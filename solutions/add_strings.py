"""Add Strings — LeetCode 415."""

from __future__ import annotations

META = {
    "pattern": "string-manipulation",
    "insight": "Walk both strings from the right with one carry, and let the loop condition itself handle unequal lengths and a final carry.",
    "time": "O(max(m, n))",
    "space": "O(max(m, n)) for the output",
    "sections": [
        (
            "What it asks",
            """
Add two non-negative integers given as decimal strings and return the sum as a
string — **without** converting them to integers and without `BigInteger`.

The ban is the whole question: it is asking whether you can implement carry
propagation. Ask whether leading zeros can appear in the input (LeetCode says
no, except `"0"` itself) and whether negatives are in scope (they are not —
say so, because sign handling would double the code).
""",
        ),
        (
            "The insight",
            """
Grade-school addition, right to left, one `carry`. The part worth designing is
the **loop condition**:

```python
while i >= 0 or j >= 0 or carry:
```

Those three clauses replace three special cases people otherwise write out:
unequal lengths, a shorter operand running out mid-way, and a final carry that
grows the answer by a digit (`"999" + "1"` → `"1000"`). Treat an exhausted
string as contributing 0 and the whole thing is one branch-free block.

`divmod(total, 10)` gives carry and digit together. Build into a list and
reverse at the end — prepending to a string is `O(n)` per step and turns this
into `O(n²)`, which is a real and commonly-made mistake at n = 10⁴.

`ord(c) - ord('0')` rather than `int(c)` is worth a sentence: it is what the
equivalent C would do, and it is the same trick you need for
**Multiply Strings** and **Add Binary**.
""",
        ),
        (
            "Edge cases",
            """
- **`"0" + "0"` → `"0"`.** The loop must run at least once; it does, because
  `i >= 0` is true on the first iteration. A `while carry` written first would
  return `""`.
- **Very unequal lengths** (`"0" + "456"`), in both argument orders. The
  symmetric loop covers both; a version that assumes `num1` is longer does not.
- **Carry cascading through every digit**: `"99999999999999999999" + "1"`. This
  is the case that catches an off-by-one in the final-carry handling.
- **Follow-up: any base.** Replace the two `10`s with `base` and the same code
  is Add Binary (LeetCode 67). Interviewers ask this as the immediate extension.
""",
        ),
    ],
}


def add_strings(num1: str, num2: str) -> str:
    i, j = len(num1) - 1, len(num2) - 1
    carry = 0
    digits: list[str] = []

    # `or carry` is what grows the answer by a digit on "999" + "1".
    while i >= 0 or j >= 0 or carry:
        total = carry
        if i >= 0:
            total += ord(num1[i]) - ord("0")
            i -= 1
        if j >= 0:
            total += ord(num2[j]) - ord("0")
            j -= 1

        carry, digit = divmod(total, 10)
        digits.append(str(digit))

    return "".join(reversed(digits))  # reverse once, never prepend


CASES = [
    (("11", "123"), "134"),
    (("456", "77"), "533"),
    (("0", "0"), "0"),
    (("9", "99"), "108"),
    (("999", "1"), "1000"),
    (("1", "999"), "1000"),
    (("0", "456"), "456"),
    (("99999999999999999999", "1"), "100000000000000000000"),
]


def solve(num1: str, num2: str) -> str:
    return add_strings(num1, num2)
