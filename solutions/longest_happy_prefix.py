"""Longest Happy Prefix — LeetCode 1392."""

from __future__ import annotations

META = {
    "pattern": "string-algorithms",
    "insight": "A happy prefix is exactly a border, so the answer is the last entry of the KMP prefix function — the problem is the table, not a use of it.",
    "time": "O(n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Return the longest **proper** prefix of `s` that is also a suffix of `s`.
Proper means shorter than `s` itself, so the whole string never counts. Return
the empty string when there is none.

Ask nothing about the statement — it is unambiguous. Ask about the size:
n ≤ 10⁵, which is what kills the obvious loop.

This is the rare problem where the answer *is* a named algorithm rather than an
application of one. The value asked for is the definition of a border, and the
KMP prefix function is the table of borders of every prefix. If you can write
that table you have written the solution, and if you cannot, no amount of
cleverness elsewhere will help.
""",
        ),
        (
            "Brute force, and why it fails",
            """
Try every length `k` from `n - 1` down to 1 and compare `s[:k]` with `s[n-k:]`.
Each comparison is O(k), so the total is O(n²) — and it is the *long* prefixes
that get tested first, so the constant is bad.

At n = 10⁵ that is about 5·10⁹ character comparisons. `"aaaa…a"` is not even
the worst input for it; the worst is a string of all `a` with a single `b`
planted near the front, which forces almost every comparison to run nearly to
completion before failing.

Python's slicing makes this look like three lines, which is why it is the
answer most people write. It times out.
""",
        ),
        (
            "The insight",
            """
Define `failure[i]` = length of the longest proper border of `s[:i + 1]`. The
answer is `s[:failure[n - 1]]`.

The table builds on itself. Suppose you know `failure[i - 1] = k`, so
`s[:k] == s[i-k:i]`. To extend the border to position `i` you need one more
character to agree:

- if `s[i] == s[k]`, the border grows to `k + 1`;
- otherwise the length-`k` border is dead, but a **shorter** one may survive —
  and the only candidates are the borders of `s[:k]`, which is `failure[k - 1]`,
  then `failure[failure[k - 1] - 1]`, and so on down to 0.

That chain is why the retreat is `k = failure[k - 1]` inside a `while`, not a
plain `k = 0`.

```
while k and s[i] != s[k]:
    k = failure[k - 1]
```

Why the borders of `s[:k]` are the only candidates is the part worth saying out
loud: any shorter border of `s[:i]` is itself both a prefix and a suffix of
`s[:k]`, because `s[:k]` is where it must live at both ends.
""",
        ),
        (
            "Amortised, not quadratic",
            """
The nested `while` inside a `for` looks O(n²). It is not.

`k` increases by at most 1 per iteration of the outer loop, so across the whole
run it increases at most `n` times. Every pass of the inner loop strictly
decreases `k`, and `k` never goes below 0. Therefore the inner loop runs at
most `n` times **in total**. O(n).

Interviewers ask for this argument by name. "Amortised, because `k` is a
potential function that only the outer loop can raise" is the answer; "it's
usually fast" is not.
""",
        ),
        (
            "Dry run — and the input that catches the wrong retreat",
            """
`s = "aabaaab"`:

```
i        0  1  2  3  4  5  6
s        a  a  b  a  a  a  b
failure  0  1  0  1  2  2  3
```

Position 5 is the interesting one. Coming in with `k = 2`, `s[5] = 'a'` does
not match `s[2] = 'b'`. The correct retreat goes to `failure[1] = 1`, where
`s[5] = 'a'` matches `s[1] = 'a'`, so `k` climbs back to 2. Position 6 then
extends to 3 and the answer is `"aab"` — and indeed `"aabaaab"` starts and ends
with `"aab"`.

Reset-to-zero instead: at position 5 you would get `k = 1`, then at position 6
`'b'` fails against `s[1] = 'a'`, drops to 0, fails against `s[0] = 'a'`, and
you report `""`. Silently wrong, and it passes `"level"` and `"ababab"`, which
is why it survives casual testing.

Two more: `"ababab"` gives `failure = [0,0,1,2,3,4]` → `"abab"`. `"level"`
gives `[0,0,0,0,1]` → `"l"`.
""",
        ),
        (
            "Follow-ups",
            """
- **Rolling hash instead.** Compare the hash of `s[:k]` with `s[n-k:]` for
  every `k` in O(1) each, O(n) overall. Faster to write, but probabilistic, and
  a single-mod hash with a fixed base is breakable — this problem family has
  anti-hash tests. Use two mods, or use KMP.
- **The Z-function.** `z[n - k] == k` characterises the same borders. Equally
  linear; pick whichever table you can write without a bug at 2 a.m.
- **What else the table gives you free.** The shortest period is
  `n - failure[n - 1]`, which settles Repeated Substring Pattern; the full
  chain of borders is `failure[n-1]`, `failure[failure[n-1]-1]`, …, which
  enumerates *every* happy prefix, not just the longest.
""",
        ),
    ],
}


def build_failure(pattern: str) -> list[int]:
    """failure[i] = length of the longest proper border of pattern[:i + 1]."""
    failure = [0] * len(pattern)
    k = 0

    for i in range(1, len(pattern)):
        while k and pattern[i] != pattern[k]:
            k = failure[k - 1]  # fall back along the chain of shorter borders
        if pattern[i] == pattern[k]:
            k += 1
        failure[i] = k

    return failure


def longest_prefix(s: str) -> str:
    if not s:
        return ""
    return s[: build_failure(s)[-1]]


CASES = [
    (("level",), "l"),
    (("ababab",), "abab"),
    (("leetcodeleet",), "leet"),
    (("aabaaab",), "aab"),  # reset-to-zero returns "" here
    (("aaaa",), "aaa"),
    (("abcdef",), ""),
    (("a",), ""),
    (("",), ""),
]


def solve(s: str) -> str:
    return longest_prefix(s)
