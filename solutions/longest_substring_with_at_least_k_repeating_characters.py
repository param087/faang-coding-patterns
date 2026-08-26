"""Longest Substring with At Least K Repeating Characters — LeetCode 395."""

from __future__ import annotations

from collections import Counter

META = {
    "pattern": "divide-and-conquer",
    "insight": "A character that appears fewer than k times in the whole string can appear in no answer at all — split there and recurse on the pieces.",
    "time": "O(26 · n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
The length of the longest substring in which **every** character present
occurs at least `k` times. Characters absent from the substring have no
constraint — that is the whole subtlety, and it is worth restating before you
write code, because it is what stops "count the distinct characters" from
working.

`s` is lowercase letters only, so the alphabet is 26. That bound is in the
constraints for a reason and both good solutions use it.
""",
        ),
        (
            "The insight",
            """
Look for a character that **cannot possibly be in the answer**. If `c` occurs
fewer than `k` times in all of `s`, then it occurs fewer than `k` times in
every substring too, so no valid substring may contain it. Every candidate
answer therefore lies strictly inside one of the pieces of `s.split(c)`.

That gives a three-line recursion:

- `len(s) < k` → 0, nothing can qualify;
- some character is globally under-represented → split on it and take the best
  piece;
- otherwise every character already clears `k` → the answer is `len(s)`.

Depth is bounded by **26**, not by `n`: each level permanently removes one
distinct character from every piece it produces, so after 26 levels there is
nothing left to split on. Each level touches at most `n` characters in total,
hence O(26 · n). Say the depth bound explicitly — the recursion looks
unbounded otherwise, and "won't this stack overflow?" is the obvious
follow-up.
""",
        ),
        (
            "The pitfall: a plain sliding window does not work here",
            """
The reflex on "longest substring with property P" is two pointers: expand
right, shrink left while invalid. It fails, because **validity is not monotone
in this problem**. `"aaabb"` with `k = 3` is invalid; extending it to
`"aaabbb"` makes it valid. Shrinking from the left when the window is invalid
therefore throws away windows that a further expansion would have rescued.
Two pointers need "invalid stays invalid as you grow", and that is exactly
what is missing.

The repair is to add the missing monotonicity by hand: fix a target number of
distinct characters `t` and run a normal window that keeps at most `t`
distinct. *Now* the window is monotone, and a window is an answer when it has
exactly `t` distinct and all of them reach `k`. Loop `t` from 1 to 26 →
O(26 · n), same bound as the recursion and O(1) extra space.

Have both ready. The divide and conquer is faster to write correctly under
pressure; the windowed version is the one to describe when asked for constant
space or a streaming variant.
""",
        ),
    ],
}


def longest_substring(s: str, k: int) -> int:
    if len(s) < k:
        return 0

    counts = Counter(s)
    for char, count in counts.items():
        if count < k:
            # `char` is in no valid substring, so every candidate sits in a piece.
            return max(longest_substring(piece, k) for piece in s.split(char))

    return len(s)  # every character already clears k


CASES = [
    (("aaabb", 3), 3),
    (("ababbc", 2), 5),
    # The answer is neither the whole string nor adjacent to the first split:
    # drop 'd', then drop 'c', and "bbb" survives.
    (("aacbbbdc", 2), 3),
    (("bbaaacbd", 3), 3),
    (("", 1), 0),
    (("a", 1), 1),
    (("a", 2), 0),
    (("weitong", 2), 0),
    (("aabbcc", 2), 6),
]


def solve(s: str, k: int) -> int:
    return longest_substring(s, k)
