"""Integer to Roman — LeetCode 12."""

from __future__ import annotations

META = {
    "pattern": "string-manipulation",
    "insight": "The four subtractive pairs are just four more symbols, so plain greedy over a 13-row table is correct.",
    "time": "O(1) — 13 rows, output capped at 15 characters",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Convert an integer in 1–3999 to its Roman numeral.

Worth stating out loud: the bound is 3999 because there is no symbol above M,
so the largest representable numeral is `MMMCMXCIX`. That bound is what lets
you call everything here O(1).
""",
        ),
        (
            "The insight",
            """
The wrong first answer is to write seven symbols and then special-case the
subtractive forms with `if num % 10 == 9` style branches. That is a dozen
branches and every one of them is a place to be wrong.

Instead treat `CM`, `CD`, `XC`, `XL`, `IX`, `IV` as **symbols in their own
right**. With 13 rows in descending value order, the entire algorithm is
"repeatedly take the largest value that fits":

```
count, num = divmod(num, value)
```

Greedy is provably optimal here, and the reason is worth knowing: the Roman
value set is *canonical* (each row's value exceeds the largest total the rows
below it can express before a carry). Greedy on an arbitrary value set — coin
change with `[1, 3, 4]` and target 6 — is not optimal. Naming that distinction
is what separates a memorised table from an understood one.
""",
        ),
        (
            "Edge cases",
            """
- **Order matters.** The table must be strictly descending. Put `IX` after `V`
  and 9 comes out as `VIIII`.
- **`divmod`, not a `while` loop.** Only `I`, `X`, `C`, `M` can repeat, and at
  most three times, so `count` is 0–3 everywhere except `M` where it is 0–3
  as well. A `while num >= value` loop is equivalent but reads worse.
- **1 and 3999** are the two you should test: the smallest single symbol, and
  the one that exercises `MMM`, `CM`, `XC` and `IX` all at once.
- If the interviewer lifts the 3999 bound, ask what symbol represents 5000 —
  the usual answer is an overbar (vinculum), which no longer fits in ASCII.
""",
        ),
    ],
}

# Descending, with the four subtractive pairs interleaved as first-class rows.
VALUES: list[tuple[int, str]] = [
    (1000, "M"),
    (900, "CM"),
    (500, "D"),
    (400, "CD"),
    (100, "C"),
    (90, "XC"),
    (50, "L"),
    (40, "XL"),
    (10, "X"),
    (9, "IX"),
    (5, "V"),
    (4, "IV"),
    (1, "I"),
]


def int_to_roman(num: int) -> str:
    parts: list[str] = []
    for value, symbol in VALUES:
        count, num = divmod(num, value)
        parts.append(symbol * count)  # count is 0 whenever the row does not fit
    return "".join(parts)


CASES = [
    ((1,), "I"),
    ((3,), "III"),
    ((4,), "IV"),
    ((9,), "IX"),
    ((58,), "LVIII"),
    ((1994,), "MCMXCIV"),
    ((3749,), "MMMDCCXLIX"),
    ((3999,), "MMMCMXCIX"),
]


def solve(num: int) -> str:
    return int_to_roman(num)
