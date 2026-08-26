"""Find All Anagrams in a String — LeetCode 438."""

from __future__ import annotations

from collections import Counter

META = {
    "pattern": "arrays-hashing",
    "insight": "The window width is fixed, so every step is one character in and one out — anagram-ness updates in O(1), never rebuilt.",
    "time": "O(n)",
    "space": "O(k) — at most 26 distinct letters",
    "sections": [
        (
            "What it asks",
            """
Return the start index of every substring of `s` that is an anagram of `p`.
Overlaps count, so `"abab"` with `p = "ab"` yields `0, 1, 2`.

Ask: lowercase ASCII only (LeetCode says yes — which caps the alphabet at 26
and makes "compare two count maps" defensible)? Do indices need to come out
sorted (a left-to-right scan gives that for free)?
""",
        ),
        (
            "The insight",
            """
Two facts collapse this:

1. An anagram of `p` has **exactly** `len(p)` characters, so there is no
   search over window widths — only `n - k + 1` candidate windows.
2. Sliding from window `i` to window `i + 1` changes exactly two counts. So
   the equality test does not need to be recomputed; it needs to be
   **maintained**.

The naive version sorts each window: `O(n · k log k)`, which at n = 3·10⁴ and
k = 10⁴ is roughly 4·10⁹ character comparisons. Counting instead of sorting
already drops that to `O(n · k)`; sliding drops it to `O(n)`.

`matched` counts how many *distinct* letters currently sit at exactly the
required multiplicity. When `matched == len(need)`, the window is an anagram.
The two-branch update is the whole trick: a letter can cross the "correct"
line going up (`== need`) or going down off it (`== need + 1`), and both
directions have to be handled or the counter drifts.
""",
        ),
        (
            "Edge cases",
            """
- `len(p) > len(s)` — must return `[]` before any indexing. The window loop
  would otherwise emit a negative start index.
- Characters of `s` that never appear in `p` are ignored entirely rather than
  tracked; they simply never satisfy `matched`, and skipping them keeps the
  map at 26 keys rather than the full input alphabet.
- **The Python-specific trap** if you write the simpler `window == need`
  version: after decrementing a count to zero you must `del` the key, or the
  dictionaries compare unequal on a phantom `{'a': 0}`. `Counter` has compared
  as a multiset since 3.10 and forgives this; a plain `dict` never will. That
  is a silent wrong answer, not a crash — the reason to prefer maintaining a
  single integer.
- Duplicate letters in `p` (`"aab"`) are exactly what breaks a set-based
  solution. Keep counts, not membership.
""",
        ),
    ],
}


def find_anagrams(s: str, p: str) -> list[int]:
    n, k = len(s), len(p)
    if k == 0 or k > n:
        return []

    need = Counter(p)
    window: Counter[str] = Counter()
    matched = 0  # distinct letters sitting at exactly the required count
    result: list[int] = []

    for i, char in enumerate(s):
        if char in need:
            window[char] += 1
            if window[char] == need[char]:
                matched += 1
            elif window[char] == need[char] + 1:
                matched -= 1  # just went over; it was correct a moment ago

        if i >= k:  # evict the character leaving the window
            gone = s[i - k]
            if gone in need:
                if window[gone] == need[gone]:
                    matched -= 1
                elif window[gone] == need[gone] + 1:
                    matched += 1
                window[gone] -= 1

        if i >= k - 1 and matched == len(need):
            result.append(i - k + 1)

    return result


CASES = [
    (("cbaebabacd", "abc"), [0, 6]),
    (("abab", "ab"), [0, 1, 2]),
    (("abcabc", "cba"), [0, 1, 2, 3]),
    (("aabbcc", "abc"), []),  # right multiset overall, no window matches
    (("aaaaa", "aa"), [0, 1, 2, 3]),
    (("baa", "aa"), [1]),
    (("a", "ab"), []),  # p longer than s
    (("", "a"), []),
]


def solve(s: str, p: str) -> list[int]:
    return find_anagrams(s, p)
