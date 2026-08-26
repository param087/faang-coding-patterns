"""Count Different Palindromic Subsequences — LeetCode 730."""

from __future__ import annotations

MOD = 10**9 + 7
ALPHABET = 26

META = {
    "pattern": "dp-strings",
    "insight": "When an interval's ends match, every inner palindrome doubles; subtract the span between the next and previous copy of that character.",
    "time": "O(n²)",
    "space": "O(n²)",
    "sections": [
        (
            "What it asks",
            """
Count **distinct** non-empty palindromic subsequences of `s`, modulo 1e9+7.
Distinct by *string value*, not by index set — `"aa"` picked from positions
(0,1) and (0,2) is one subsequence, not two. The alphabet is only `a`–`d`.

Ask this first, because it is the whole problem: **distinct strings or distinct
index sets?** Distinct index sets is a much easier DP (`dp[i][j] = dp[i+1][j] +
dp[i][j-1] - dp[i+1][j-1] + (s[i] == s[j]) * (dp[i+1][j-1] + 1)`, LC 647-style)
and if you write that one you have answered a different question. The
de-duplication is where all the difficulty lives.
""",
        ),
        (
            "The insight",
            """
> `dp[i][j]` = number of distinct palindromic subsequences inside `s[i..j]`.

**Ends differ** (`s[i] != s[j]`) — nothing can use both ends, so it is plain
inclusion–exclusion over the two shrunk intervals:

```
dp[i][j] = dp[i+1][j] + dp[i][j-1] - dp[i+1][j-1]
```

The subtraction is because the middle `s[i+1..j-1]` sits in both terms.

**Ends match** (`s[i] == s[j] == c`) — every palindrome `p` in the middle
yields a second one, `c + p + c`, and those are all new because they start and
end with `c` while `p` need not. So the middle count *doubles*. What is left is
to add the pure-`c` runs `"c"` and `"cc"` exactly once, and that depends on
whether `c` already appears strictly inside. Let `low` be the first `c` after
`i` and `high` the last `c` before `j`:

- **no `c` inside** (`low > high`) — `"c"` and `"cc"` are both new:
  `2·inner + 2`
- **exactly one `c` inside** (`low == high`) — `"c"` is already counted in
  `inner`, only `"cc"` is new: `2·inner + 1`
- **two or more** — the doubling now over-counts. Every palindrome that
  `s[low..high]` already wrapped in `c…c` gets produced twice, so subtract the
  interior between them: `2·inner - dp[low+1][high-1]`

Precomputing next/previous occurrence tables keeps each cell O(1), so the whole
thing is O(n²) rather than the O(n³) you get from scanning inwards per cell.
""",
        ),
        (
            "The two things that break it",
            """
**Negative intermediates.** Both the `- dp[i+1][j-1]` and the
`- dp[low+1][high-1]` terms can drive a cell negative once you reduce mod
1e9+7. Python's `%` returns a non-negative result so it self-heals here, but in
Java or C++ you must write `(x % MOD + MOD) % MOD` or the final answer comes
back negative on large inputs and looks like an overflow bug. Say this out loud
— it is the single most common failure in the room.

**Reducing too late.** Reduce every cell as you write it. `2 * inner` on an
unreduced table overflows a 64-bit accumulator long before `n = 1000`.

Third, quietly: the doubling argument only works because `p` and `c + p + c`
can never be the same string (the second is strictly longer). That is why
`"aaa"` gives 3 (`"a"`, `"aa"`, `"aaa"`) and not 4 — the `low == high` branch
declines to re-add `"a"`.
""",
        ),
    ],
}


def count_palindromic_subsequences(s: str) -> int:
    n = len(s)
    if n == 0:
        return 0

    # next_at[i][c] = smallest index >= i holding c, else n.
    next_at = [[n] * ALPHABET for _ in range(n + 1)]
    for i in range(n - 1, -1, -1):
        next_at[i] = next_at[i + 1][:]
        next_at[i][ord(s[i]) - 97] = i

    # prev_at[i][c] = largest index <= i holding c, else -1.
    prev_at = [[-1] * ALPHABET for _ in range(n)]
    prev_at[0][ord(s[0]) - 97] = 0
    for i in range(1, n):
        prev_at[i] = prev_at[i - 1][:]
        prev_at[i][ord(s[i]) - 97] = i

    dp = [[0] * n for _ in range(n)]
    for i in range(n):
        dp[i][i] = 1  # the single character itself

    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            inner = dp[i + 1][j - 1] if i + 1 <= j - 1 else 0

            if s[i] != s[j]:
                # inclusion-exclusion: the middle is counted by both halves
                dp[i][j] = dp[i + 1][j] + dp[i][j - 1] - inner
            else:
                c = ord(s[i]) - 97
                low = next_at[i + 1][c]  # first c strictly after i
                high = prev_at[j - 1][c]  # last c strictly before j
                if low > high:
                    dp[i][j] = 2 * inner + 2  # "c" and "cc" both new
                elif low == high:
                    dp[i][j] = 2 * inner + 1  # "c" already inside; only "cc" is new
                else:
                    # the span between the two inner copies was wrapped twice
                    dp[i][j] = 2 * inner - dp[low + 1][high - 1]

            dp[i][j] %= MOD  # reduce every cell; Python's % also fixes negatives

    return dp[0][n - 1]


CASES = [
    (("bccb",), 6),
    (("aaa",), 3),
    (("aba",), 4),
    (("abba",), 6),
    (("abcd",), 4),
    (("dcbabcbadcbba",), 81),
    (("a",), 1),
    (("",), 0),
]


def solve(s: str) -> int:
    return count_palindromic_subsequences(s)
