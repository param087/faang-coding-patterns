"""Decode Ways — LeetCode 91."""

from __future__ import annotations

META = {
    "pattern": "dp-1d",
    "insight": "Classify by the last letter: it consumed one digit or two, and zeros are what make each option illegal.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Digits map to letters as `A = 1 … Z = 26`. Given a digit string, count the
decodings. `"226"` is `BZ`, `VF`, `BBF` → **3**.

Ask the one question that matters: **can a code have a leading zero?** No —
`"06"` is not a valid encoding of `F`, only `"6"` is. Every hard case in this
problem is a zero, so establish that rule before writing anything.
""",
        ),
        (
            "The insight",
            """
Same "classify by the last move" shape as Climbing Stairs, with the moves
gated by validity:

> `dp[i]` = number of decodings of the first `i` characters.

```
dp[i] += dp[i-1]   if s[i-1] is '1'..'9'
dp[i] += dp[i-2]   if s[i-2:i] is between "10" and "26"
dp[0] = 1
```

Both guards are non-optional. Without them you have Fibonacci and you will
report 2 for `"27"` (only `BG`) and 1 for `"30"` (there are none).

Only two entries are read, so roll it into two variables: O(n) time, O(1)
space. Note that `dp[i] = 0` is a legitimate value and propagates correctly —
an unreachable prefix makes everything after it unreachable too, which is
exactly why `"100"` comes out as 0 without a special case.
""",
        ),
        (
            "Zeros are the whole problem",
            """
Run these before you say you are done — each one breaks a different sloppy
implementation:

| Input | Answer | What it catches |
| --- | --- | --- |
| `"0"` | 0 | no code is zero |
| `"06"` | 0 | leading zeros are not allowed |
| `"10"` | 1 | a zero that is only valid as part of a pair |
| `"100"` | 0 | `"10"` then a stranded `0`; needs the zero to propagate |
| `"2101"` | 1 | `"21"`+`"01"` must be rejected while `"2"`+`"10"`+`"1"` stands |
| `"27"` | 1 | the two-digit guard has an upper bound as well as a lower one |

The mental rule: a `0` **must** be swallowed by a preceding `1` or `2`, and it
can never start a code. Anything else is invalid input territory.

Convention on the empty string: LeetCode guarantees length ≥ 1, so pick one
and state it. Returning 0 (nothing to decode is not a decoding) is the safer
answer to give aloud, while the internal `dp[0] = 1` stays as the base case —
those are two different questions and mixing them up is a common wobble.
""",
        ),
    ],
}


def num_decodings(s: str) -> int:
    if not s or s[0] == "0":
        return 0

    two_back, one_back = 1, 1  # dp[i-2], dp[i-1], starting at i = 1

    for i in range(2, len(s) + 1):
        current = 0
        if s[i - 1] != "0":
            current += one_back  # this digit stands alone
        pair = int(s[i - 2] + s[i - 1])
        if 10 <= pair <= 26:  # lower bound rejects "01", upper bound rejects "27"
            current += two_back
        two_back, one_back = one_back, current

    return one_back


CASES = [
    (("12",), 2),
    (("226",), 3),
    (("11106",), 2),
    (("2101",), 1),
    (("100",), 0),
    (("10",), 1),
    (("27",), 1),
    (("06",), 0),
    (("",), 0),
]


def solve(s: str) -> int:
    return num_decodings(s)
