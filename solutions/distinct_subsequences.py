"""Distinct Subsequences — LeetCode 115."""

from __future__ import annotations

META = {
    "pattern": "dp-strings",
    "insight": "Counting, not maximising: on a match the two branches add rather than max, because using and skipping it are different subsequences.",
    "time": "O(m · n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
How many distinct ways can `t` be picked out of `s` as a subsequence? Two ways
are different if they use different **positions**, even when the resulting
string is identical — `"rabbbit"` yields `"rabbit"` three times because there
are three `b`s to drop.

Ask whether the count can overflow. LeetCode guarantees it fits in 32 bits,
which is a hint that no modulus is coming; in Python it is moot, but in Java
or C++ you would say `int` is safe only because the problem promised it.
""",
        ),
        (
            "The insight",
            """
> `dp[i][j]` = the number of ways the first `i` characters of `s` produce the
> first `j` characters of `t`.

Split on whether `s[i-1]` is *used*:

```
dp[i][j] = dp[i-1][j]                              # skip s[i-1]
         + dp[i-1][j-1]  if s[i-1] == t[j-1]       # use it
```

The plus sign is the whole problem. Everything else in this pattern takes a
`max` or a `min`; here the two branches are disjoint sets of solutions, so
they **add**. Writing `max` gives you back Longest Common Subsequence, which
answers a completely different question and returns 1 on `"rabbbit"`.

Base cases: `dp[i][0] = 1` — the empty target is matched exactly one way, by
choosing nothing. `dp[0][j] = 0` for `j > 0`. That lone 1 in the corner is
what every count is ultimately built from; initialising it to 0 returns 0 for
everything and looks like a much deeper bug than it is.
""",
        ),
        (
            "Why the inner loop runs backwards",
            """
Rolling to one array, `dp[j] += dp[j-1]` needs `dp[j-1]` from the **previous**
row. Iterating `j` upwards overwrites `dp[j-1]` first, so you read the current
row and start counting subsequences that reuse the same character of `s`
twice — the count inflates, sometimes enormously.

So `for j in range(len(t), 0, -1)`. This is the identical trick to 0/1 knapsack
rolled to 1-D, and for the identical reason: each item of `s` may be used at
most once per subsequence. Iterating forwards turns it into the unbounded
knapsack.

Quick check on `("aaa", "aa")` → **3** (positions 01, 02, 12). A forwards loop
gives 4 or more. Keep this case; it is small enough to trace and it fails
loudly.
""",
        ),
    ],
}


def num_distinct(s: str, t: str) -> int:
    if len(t) > len(s):
        return 0

    n = len(t)
    dp = [0] * (n + 1)
    dp[0] = 1  # the empty target is matched exactly one way

    for ch in s:
        # Backwards: dp[j - 1] must still be the previous row's value.
        for j in range(n, 0, -1):
            if t[j - 1] == ch:
                dp[j] += dp[j - 1]

    return dp[n]


CASES = [
    (("rabbbit", "rabbit"), 3),
    (("babgbag", "bag"), 5),
    (("aaa", "aa"), 3),
    (("aaaaa", "a"), 5),
    (("abc", ""), 1),
    (("", ""), 1),
    (("", "a"), 0),
    (("abc", "abcd"), 0),
]


def solve(s: str, t: str) -> int:
    return num_distinct(s, t)
