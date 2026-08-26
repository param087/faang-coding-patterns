"""Longest Substring with At Most K Distinct Characters — LeetCode 340 (Premium)."""

from __future__ import annotations

META = {
    "pattern": "sliding-window",
    "insight": "Always widen right, shrink left only while the distinct count exceeds k; counts rather than a set are what make the shrink correct.",
    "time": "O(n)",
    "space": "O(k)",
    "sections": [
        (
            "What it asks",
            """
Given a string `s` and an integer `k`, return the length of the longest
**contiguous substring** containing at most `k` distinct characters.

This one is LeetCode Premium, so the statement is not public — the task is as
described above, in my own words. It is the parent problem of *Longest
Substring Without Repeating Characters* (`k` unbounded but each count capped at
1) and of *Fruit Into Baskets* (LC 904), which is literally this with `k = 2`.

Ask: is the alphabet bounded (it decides whether "distinct count" costs O(1) or
O(k) to maintain, and whether an array beats a hash map)? Return the length or
the substring itself (track `left` if it is the substring)? And what happens at
`k = 0` — the answer is 0, and an interviewer who says "assume `k >= 1`" has
just told you they will test `k = 0`.
""",
        ),
        (
            "The insight",
            """
The window is **monotone**: if `s[left:right]` has at most `k` distinct
characters, so does every substring of it. That is what licenses the two-
pointer scan — once a window is invalid, no shorter right end helps, so `left`
never needs to move backwards. Both pointers only advance, giving 2n pointer
moves in total, hence O(n) despite the nested `while`.

The part that decides the problem is the map holding **counts, not
membership**. On `"abaccc"` with `k = 2`, when `left` walks past the first `a`
the window still contains another `a` at index 2; a `set` would drop `a`
outright, wrongly shrink the distinct count to 1, and let the window swallow a
third character. Only when a count hits zero does the character genuinely leave
— and you must `del` the key at that moment, because `len(counts)` is the
distinct count and a lingering `{'a': 0}` inflates it by one, quietly costing
you valid windows rather than crashing.

Note the loop shrinks with `while`, not `if`. Here one addition can only push
the distinct count to `k + 1`, so `if` happens to suffice — but writing `while`
costs nothing, is the shape every other variable window needs, and survives the
follow-up where you evict by a different predicate.
""",
        ),
        (
            "Follow-ups",
            """
- **Return the substring, not the length.** Keep `best_left` alongside `best`
  and slice at the end; recomputing from the final pointers is a classic
  off-by-one, since `left` has usually moved past the winning window.
- **`k = 2` exactly** is *Fruit Into Baskets*; the same code, and a good
  sanity check that your general version handles the small case.
- **At most `k` distinct with the window required to be an anagram / fixed
  width** — then the window stops being variable and every step is one in, one
  out, as in LC 438.
- **Unicode or a huge alphabet**: the hash map already handles it at O(k)
  space. Swap in a 128-slot array only when the alphabet is provably ASCII;
  premature array indexing is the usual source of an `IndexError` on the
  interviewer's test.
- **Streaming input** where `s` arrives character by character and you cannot
  index backwards: keep a deque of the characters currently in the window. Same
  O(n), and the answer becomes "longest so far" rather than a slice.
""",
        ),
    ],
}


def length_of_longest_substring_k_distinct(s: str, k: int) -> int:
    if k <= 0:
        return 0

    counts: dict[str, int] = {}
    left = 0
    best = 0

    for right, char in enumerate(s):
        counts[char] = counts.get(char, 0) + 1

        while len(counts) > k:
            leaving = s[left]
            counts[leaving] -= 1
            if counts[leaving] == 0:
                del counts[leaving]  # or len(counts) stops meaning "distinct"
            left += 1

        best = max(best, right - left + 1)

    return best


CASES = [
    (("eceba", 2), 3),  # "ece"
    (("abaccc", 2), 4),  # "accc" — a set-based window gets this wrong
    (("abcadcacacaca", 3), 11),
    (("aa", 1), 2),
    (("aabbcc", 1), 2),
    (("aabbcc", 3), 6),
    (("abc", 10), 3),  # k larger than the alphabet present
    (("a", 0), 0),
    (("", 2), 0),
]


def solve(s: str, k: int) -> int:
    return length_of_longest_substring_k_distinct(s, k)
