"""Palindrome Partitioning II — LeetCode 132."""

from __future__ import annotations

META = {
    "pattern": "dp-advanced",
    "insight": "Grow palindromes outward from each centre and update the cut count the moment a palindrome ends — no separate table.",
    "time": "O(n²)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Cut a string into pieces so every piece is a palindrome; return the **minimum
number of cuts**. Cuts, not pieces — the answer for `"aab"` is 1, not 2. Every
string is cuttable, since single characters are palindromes, so `n - 1` is
always an upper bound and there is no "impossible" case to handle.

Do not confuse it with Palindrome Partitioning I, which enumerates every
partition and is exponential by necessity. Here only a count is wanted, which
is what makes polynomial time possible.
""",
        ),
        (
            "The insight",
            """
The recurrence is easy: `cuts[i]` = fewest cuts for the prefix of length `i`,
and `cuts[i] = min(cuts[j] + 1)` over every `j` where `s[j:i]` is a palindrome.
The cost is entirely in answering *"is `s[j:i]` a palindrome?"* — done naively
that is O(n) per query and the whole thing is O(n³): at n = 2000 that is
8·10⁹ character comparisons.

The standard fix is a precomputed `n × n` palindrome table, O(n²) time and
O(n²) memory. Fine, and what most people write.

The better answer fuses the two passes. **Expand around each of the `2n - 1`
centres**, and every time the expansion confirms `s[l..r]` is a palindrome,
relax the DP immediately:

```
cuts[r + 1] = min(cuts[r + 1], cuts[l] + 1)
```

Every palindromic substring is discovered exactly once, so this is O(n²) time
with only **O(n) space** — no boolean table at all. Expansion also stops early
the moment the characters differ, which on real strings is far faster than the
table's unconditional n² fill.

Initialise `cuts[i] = i - 1`, i.e. `cuts = list(range(-1, n))`. The `-1` at
index 0 is deliberate: an empty prefix costs "minus one cut" so that closing the
first palindrome yields 0. Set `cuts[0] = 0` instead and every answer is one too
high — that is the single most common bug in this problem.
""",
        ),
        (
            "Pitfalls",
            """
- **Both centre families.** `2n - 1` centres: `n` odd (single character) and
  `n - 1` even (between two characters). Skip the even ones and `"aa"` reports
  1 cut instead of 0. `"abba"` reports 3 instead of 0.
- **`cuts[0] = -1`**, as above. Verify with `"aba"` → 0.
- **Already a palindrome** → 0 cuts. `"aaaa"` must not answer 3.
- **All distinct** `"abcde"` → 4, the upper bound. If you get 5, you are
  counting pieces.
- **Empty string / single character** → 0. `list(range(-1, 0))` is `[-1]`, and
  `cuts[0] = -1` would be returned for `n = 0`, so guard the empty case rather
  than trusting the indexing.
- **The real discriminator** is a string with overlapping palindromes of
  different lengths, like `"cabababcbc"` → 3. A greedy "take the longest
  palindrome you can from here" answers 4 on it, which is exactly why this is
  DP and not greedy.
""",
        ),
    ],
}


def min_cut(s: str) -> int:
    n = len(s)
    if n == 0:
        return 0

    # cuts[i] = fewest cuts for s[:i]; cuts[0] = -1 so closing a palindrome gives 0.
    cuts = list(range(-1, n))

    def expand(left: int, right: int) -> None:
        while left >= 0 and right < n and s[left] == s[right]:
            cuts[right + 1] = min(cuts[right + 1], cuts[left] + 1)
            left -= 1
            right += 1

    for centre in range(n):
        expand(centre, centre)  # odd-length palindromes
        expand(centre, centre + 1)  # even-length palindromes

    return cuts[n]


CASES = [
    (("aab",), 1),
    (("a",), 0),
    (("ab",), 1),
    (("",), 0),
    (("aaaa",), 0),
    (("abcde",), 4),
    (("cabababcbc",), 3),
    (("noonabbad",), 2),
    (("abbab",), 1),
]


def solve(s: str) -> int:
    return min_cut(s)
