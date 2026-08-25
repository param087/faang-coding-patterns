"""Minimum Window Substring — LeetCode 76."""

from __future__ import annotations

from collections import Counter, defaultdict

META = {
    "pattern": "sliding-window",
    "insight": "Count how many requirements are met, not how many characters — then the validity check is one integer comparison.",
    "time": "O(|s| + |t|)",
    "space": "O(|t|)",
    "sections": [
        (
            "What it asks",
            """
The smallest substring of `s` containing every character of `t`, **including
duplicates**. Empty string if none exists.

Ask: does `t = "AABC"` need two As (yes — that is why counts are needed rather
than a set)? Is the answer unique (not necessarily; any minimum will do)? Are
`s` and `t` the same case?
""",
        ),
        (
            "The structure",
            """
Grow the window until it is valid, then **shrink while it is still valid**,
recording as you shrink.

This is the reverse of the maximum-window case, and it is worth pointing at
explicitly because it looks like a mistake to anyone skimming: for a *minimum*
window you record inside the shrink loop, while the window is still good; for
a *maximum* window you record after repairing.
""",
        ),
        (
            "The trick that makes it linear",
            """
Comparing two frequency dictionaries on every step is O(alphabet) per index.

Instead track `missing` — how many **kinds** of required character are still
unmet. It changes only when a count crosses its requirement exactly, so the
validity check becomes `missing == 0`, an integer comparison.

Note the `==` in `window[char] == need[char]`, not `>=`. With `>=` you
decrement `missing` once per surplus character rather than once per satisfied
requirement, and the whole thing breaks on inputs with repeats.
""",
        ),
        (
            "Why it is O(n) despite the nested loop",
            """
`left` never resets — it only moves forward, across the entire scan. So each
index enters the window once and leaves once, and the inner `while` costs O(n)
in total.

Interviewers ask this. "It looks quadratic but `left` is monotonic, so it's
amortised linear" is the answer.
""",
        ),
        (
            "Follow-ups",
            """
- **"What if `t` is very long?"** The space is O(|t|) and unavoidable, but the
  window map only ever needs the characters that appear in `t`.
- **Substring with Concatenation of All Words** — the same idea with words
  instead of characters, and a window per starting offset.
- **Permutation in String** — a fixed-size window, which is simpler because
  there is no shrink loop at all.
""",
        ),
    ],
}


def min_window(s: str, t: str) -> str:
    if not s or not t:
        return ""

    need = Counter(t)
    window: dict[str, int] = defaultdict(int)
    missing = len(need)  # distinct requirements still unmet
    best = (len(s) + 1, 0, 0)
    left = 0

    for right, char in enumerate(s):
        window[char] += 1
        # `==`, not `>=`: count each requirement the moment it is satisfied.
        if char in need and window[char] == need[char]:
            missing -= 1

        while missing == 0:
            if right - left + 1 < best[0]:
                best = (right - left + 1, left, right)
            dropped = s[left]
            window[dropped] -= 1
            if dropped in need and window[dropped] < need[dropped]:
                missing += 1
            left += 1

    return "" if best[0] > len(s) else s[best[1] : best[2] + 1]


CASES = [
    (("ADOBECODEBANC", "ABC"), "BANC"),
    (("a", "a"), "a"),
    (("a", "aa"), ""),
    (("ab", "b"), "b"),
    (("aa", "aa"), "aa"),
    (("", "a"), ""),
]


def solve(s: str, t: str) -> str:
    return min_window(s, t)
