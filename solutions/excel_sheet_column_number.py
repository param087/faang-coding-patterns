"""Excel Sheet Column Number — LeetCode 171."""

from __future__ import annotations

META = {
    "pattern": "math-geometry",
    "insight": "It is base 26 with digits 1..26 instead of 0..25 — bijective base-26, which is why there is no letter for zero.",
    "time": "O(len(title))",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Convert an Excel column label to its 1-based index: `A → 1`, `Z → 26`,
`AA → 27`, `AB → 28`, `ZY → 701`.

The one-line version is a Horner loop and you should write it in thirty
seconds. What the question is really testing is whether you can *name* the
numbering system, because the naming is what makes the inverse problem
(LeetCode 168) fall out instead of turning into off-by-one roulette.
""",
        ),
        (
            "The insight",
            """
This is **bijective base-26**: positional notation whose digit set is
`1…26` rather than `0…25`. There is no symbol for zero, which is exactly why
`Z` is followed by `AA` and not by `A0` — and why every non-empty string of
letters maps to a distinct positive integer, with no gaps and no leading-zero
ambiguity.

Given that, the evaluation is ordinary Horner:

```
result = 0
for ch in title:
    result = result * 26 + (ord(ch) - ord('A') + 1)
```

Each step shifts the accumulated value one place left in base 26 and adds the
new digit. `AB` → `1`, then `1·26 + 2 = 28`.

The `+ 1` is the whole problem. `ord(ch) - ord('A')` gives `0…25`, which is
*ordinary* base 26 and produces `A → 0`, `AA → 0`, `AB → 1` — every string of
leading A's collapses to the same number. If your answer for `AA` is 0 or 26
rather than 27, this is the line.

No overflow question in Python, but note the range: LeetCode caps the title at
7 characters and `FXSHRXW` is exactly `2147483647`. That is not a coincidence
— the constraint was chosen so the answer fits in a signed 32-bit int.
""",
        ),
        (
            "The trap is the inverse",
            """
Going the other way — number to title, LeetCode 168 — is where the bijective
base actually bites, and it is the natural follow-up, so have it ready.

```
while n:
    n -= 1                       # <-- shift to 0-based BEFORE the divmod
    n, rem = divmod(n, 26)
    out.append(chr(ord('A') + rem))
return ''.join(reversed(out))
```

Without the `n -= 1`, `n = 26` gives `divmod(26, 26) = (1, 0)` → `AA`, when
the answer is `Z`. The decrement converts each bijective digit `1…26` into a
standard digit `0…25` just before extracting it, and simultaneously carries
the borrow into the higher places. Trace `n = 52` (`AZ`) by hand once and the
rule sticks:

- `52 - 1 = 51`, `divmod(51, 26) = (1, 25)` → `Z`, `n = 1`
- `1 - 1 = 0`, `divmod(0, 26) = (0, 0)` → `A`, `n = 0`
- reversed → `AZ`. Correct.

Other edges worth a sentence: labels are uppercase and non-empty by
constraint, so there is no case handling and no empty-string branch — but say
that you checked, and note that a defensive version would `.strip().upper()`
before the loop.
""",
        ),
    ],
}


def title_to_number(column_title: str) -> int:
    result = 0
    for ch in column_title:
        # digits run 1..26, not 0..25 — that is the whole problem
        result = result * 26 + (ord(ch) - ord("A") + 1)
    return result


CASES = [
    (("A",), 1),
    (("Z",), 26),
    (("AA",), 27),
    (("AB",), 28),
    (("AZ",), 52),
    (("BA",), 53),
    (("ZY",), 701),
    (("FXSHRXW",), 2147483647),
]


def solve(column_title: str) -> int:
    return title_to_number(column_title)
