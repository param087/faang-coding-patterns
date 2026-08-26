"""Multiply Strings — LeetCode 43."""

from __future__ import annotations

META = {
    "pattern": "string-manipulation",
    "insight": "Digit i times digit j always lands in slots i+j and i+j+1 of an (m+n)-length buffer, so there is no shifting and no intermediate addition.",
    "time": "O(m·n)",
    "space": "O(m + n)",
    "sections": [
        (
            "What it asks",
            """
Multiply two non-negative integers given as decimal strings and return the
product as a string, without converting to `int` and without a big-integer
library.

Ask: can either input have leading zeros (no, apart from `"0"` itself)? Are
they ever negative (no)? How long can they be (LeetCode says 200 digits, so
the answer can have 400 — enough that the buffer layout matters).
""",
        ),
        (
            "The insight",
            """
The obvious method is long multiplication: build `m` shifted partial products
and add them up with the Add Strings routine. That works and is still `O(m·n)`,
but you write two loops, a shift, and a string adder, and each is a place to
put a bug.

The clean version drops the intermediates entirely. Index from the **right**
and note that

```
num1[i] * num2[j]  ->  product[i + j + 1] (units), product[i + j] (tens)
```

in a buffer of length `m + n`. That is not a trick; it is just place value
written down. Every pair of digits knows exactly where it goes, so you can
accumulate all `m·n` partial products into one array in any order and carry as
you go:

```python
total = int(num1[i]) * int(num2[j]) + product[i + j + 1]
product[i + j + 1] = total % 10
product[i + j] += total // 10
```

`product[i + j]` may temporarily exceed 9. That is fine — it is normalised when
the loop reaches it as somebody else's `i + j + 1`, and the leading cell can
never overflow because an `m`-digit number times an `n`-digit number is always
under `10**(m + n)`.
""",
        ),
        (
            "The two things that go wrong",
            """
**The zero case.** `"0" * "52"` produces a buffer of all zeros; stripping
leading zeros then yields `""`. Guard it up front (`if num1 == "0" or num2 ==
"0"`) or fall back with `digits or "0"` — do one or the other, and say which,
because returning `""` is the single most common failure here.

**Buffer length.** `m + n` is right; `m + n - 1` truncates `"99" * "99"` and
`m + n + 1` leaves a stray leading zero that the strip then has to remove. The
product of an `m`-digit and an `n`-digit number has either `m + n - 1` or
`m + n` digits, so size for the maximum and strip.

Follow-up worth knowing the name of: **Karatsuba** brings `O(n²)` down to
`O(n^1.585)` by splitting each operand in half and doing three multiplications
instead of four. Nobody expects you to code it at 200 digits, but knowing it
exists — and that it only pays off in the thousands of digits — is the right
answer to "can you do better?".
""",
        ),
    ],
}


def multiply(num1: str, num2: str) -> str:
    if num1 == "0" or num2 == "0":
        return "0"  # otherwise the strip below returns ""

    m, n = len(num1), len(num2)
    product = [0] * (m + n)  # m + n slots: the product never needs more

    for i in range(m - 1, -1, -1):
        for j in range(n - 1, -1, -1):
            # place value: units at i + j + 1, tens at i + j
            total = int(num1[i]) * int(num2[j]) + product[i + j + 1]
            product[i + j + 1] = total % 10
            product[i + j] += total // 10

    digits = "".join(map(str, product)).lstrip("0")
    return digits or "0"


CASES = [
    (("2", "3"), "6"),
    (("123", "456"), "56088"),
    (("0", "52"), "0"),
    (("52", "0"), "0"),
    (("9", "9"), "81"),
    (("999", "999"), "998001"),
    (("100", "100"), "10000"),
    (("123456789", "987654321"), "121932631112635269"),
]


def solve(num1: str, num2: str) -> str:
    return multiply(num1, num2)
