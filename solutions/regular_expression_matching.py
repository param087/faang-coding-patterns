"""Regular Expression Matching — LeetCode 10."""

from __future__ import annotations

META = {
    "pattern": "dp-strings",
    "insight": "A star is not a character but a two-way branch: skip it and its atom together, or consume one character of s and stay on the same star.",
    "time": "O(m · n)",
    "space": "O(m · n), reducible to O(n)",
    "sections": [
        (
            "What it asks",
            """
Match `s` against a pattern supporting `.` (any single character) and `*`
(zero or more of the **preceding element**). The match must cover the
**entire** string, not a prefix — this is `fullmatch`, not `search`, and
assuming otherwise is the fastest way to a wrong answer.

Ask: is the pattern guaranteed well-formed? LeetCode promises every `*` has a
valid preceding element, so `"*a"` never appears. Say you are relying on that;
otherwise the `j - 2` index below is a bug.

Ask: is `.*` a single unit? Yes — `*` binds to the one element before it, so
`.*` means "any run of any characters", and `a*b*` is two independent units.
""",
        ),
        (
            "Brute force, and why it fails",
            """
Recurse: at each `*`, try consuming 0, 1, 2, … characters. The classic
exponential blow-up is `"aaaaaaaaaaaaaaaaaaaa"` against `"a*a*a*a*a*a*a*a*a*a*"`
— ten stars each free to absorb any split of twenty `a`s. That is on the order
of C(30, 10) ≈ **3 × 10⁷** distinct splits explored repeatedly, and naive
recursion times out on it. It is a real LeetCode test case, so it is not
hypothetical.

But the recursion only ever depends on `(i, j)` — how much of `s` is consumed
and how much of `p`. There are at most 20 × 30 = 600 such pairs. Same
argument as every other problem in this pattern: exponential branching over a
polynomial state space means memoise.
""",
        ),
        (
            "The insight",
            """
> `dp[i][j]` = does the first `i` characters of `s` match the first `j` of `p`?

The pattern is scanned in **units**, and the unit is decided by looking one
character *ahead* — or, going left to right in the table, by noticing that
`p[j-1]` is a `*` and therefore `p[j-2]` is its atom.

When `p[j-1]` is `*`:

- **zero copies** → `dp[i][j-2]`: throw away the atom and the star together.
  Note it is `j - 2`, not `j - 1`; the star and its atom are one unit.
- **one more copy** → if the atom matches `s[i-1]`, then `dp[i-1][j]`: consume
  one character of `s` and **stay on the same star**, because a star can match
  any number of characters.

Otherwise `p[j-1]` is a literal or `.`, and the cell is simply `dp[i-1][j-1]`
when it matches, `False` when it does not.

That "stay on the same `j`" in the second branch is the crux. Advancing `j`
there is the single most common bug and makes `*` mean "exactly one".
""",
        ),
        (
            "The base row is not all False",
            """
`dp[0][j]` asks whether the pattern matches the **empty** string, and patterns
like `"a*"`, `"a*b*c*"` and `".*"` do. So:

```
dp[0][j] = dp[0][j-2]  when p[j-1] == '*'
```

Leaving row 0 as all-`False` except `dp[0][0]` breaks `("", "a*")` and, worse,
breaks `("aab", "c*a*b")` — because the `c*` at the front has to vanish before
anything else can line up. That second case is the one to keep in your test
set; the first is easy to spot by inspection.

Column 0 is genuinely all-`False` below the corner: a non-empty string never
matches an empty pattern.
""",
        ),
        (
            "Dry run",
            """
`s = "aab"`, `p = "c*a*b"`.

Row 0: `dp[0][0] = True`. `p[1] = '*'` → `dp[0][2] = dp[0][0] = True` (`c*`
matched nothing). `p[3] = '*'` → `dp[0][4] = dp[0][2] = True` (`a*` matched
nothing too). `dp[0][5]` is `b` against empty → False.

Row `i = 1` (`s = "a"`): at `j = 4` the unit is `a*`. Zero copies gives
`dp[1][2]` = False. One more copy: the atom `a` matches `s[0]`, so
`dp[0][4] = True`. → **True**.

Row 2 (`"aa"`): at `j = 4`, one-more-copy reads `dp[1][4] = True`. → True.
The star absorbed both `a`s without `j` ever moving.

Row 3 (`"aab"`): `j = 5` is the literal `b`, matching `s[2]`, so it reads
`dp[2][4] = True`. → **True**.

Now the failure to watch: `"mississippi"` against `"mis*is*p*."` → **False**.
`p*` can only absorb `p`s, and after it the trailing `.` has two characters
left to cover. Anyone who let `*` advance `j` while also consuming will get
True here.
""",
        ),
        (
            "Follow-ups",
            """
- **Space** — each row reads only the row above and cells to its left, so two
  rows give O(n). Offer it, do not lead with it.
- **Wildcard Matching (44)** — `*` there is free-standing and matches any
  sequence, so the recurrence becomes `dp[i][j] = dp[i][j-1] or dp[i-1][j]`
  and there is no atom to look back at. It also admits a greedy two-pointer
  solution with backtracking in O(m + n) space O(1), which this problem does
  **not**. Knowing which of the two is greedy-able is a real differentiator.
- **`+`, `?`, character classes** — `+` is `atom` followed by `atom*`; you can
  desugar in a preprocessing pass rather than touching the recurrence.
- **"How would a real engine do it?"** — compile to an NFA and simulate it
  with a set of active states: Thompson's construction, O(m · n) with no
  backtracking. Mentioning this is what separates a candidate who memorised
  the table from one who knows what the table *is*.
""",
        ),
    ],
}


def is_match(s: str, p: str) -> bool:
    m, n = len(s), len(p)
    dp = [[False] * (n + 1) for _ in range(m + 1)]
    dp[0][0] = True

    # Row 0: a pattern like "a*b*" still matches the empty string.
    for j in range(2, n + 1):
        if p[j - 1] == "*":
            dp[0][j] = dp[0][j - 2]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            token = p[j - 1]
            if token == "*":
                atom = p[j - 2]  # guaranteed to exist for a valid pattern
                zero = dp[i][j - 2]  # drop the atom and the star together
                more = atom in (".", s[i - 1]) and dp[i - 1][j]  # stay on j
                dp[i][j] = zero or more
            elif token in (".", s[i - 1]):
                dp[i][j] = dp[i - 1][j - 1]

    return dp[m][n]


CASES = [
    (("aa", "a"), False),
    (("aa", "a*"), True),
    (("ab", ".*"), True),
    (("aab", "c*a*b"), True),
    (("mississippi", "mis*is*p*."), False),
    (("", "a*"), True),
    (("", ""), True),
    (("ab", ".*c"), False),
    (("aaa", "a*a"), True),
]


def solve(s: str, p: str) -> bool:
    return is_match(s, p)
