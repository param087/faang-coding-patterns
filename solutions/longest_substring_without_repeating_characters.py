"""Longest Substring Without Repeating Characters — LeetCode 3."""

from __future__ import annotations

META = {
    "pattern": "sliding-window",
    "insight": "Jump the left edge past the previous occurrence — and never let it move backwards.",
    "time": "O(n)",
    "space": "O(min(n, charset))",
    "sections": [
        (
            "What it asks",
            """
The length of the longest substring containing no repeated character.
Substring, so contiguous.

Ask: what is the alphabet — ASCII, lowercase only, Unicode? It decides whether
a 128-slot array beats a dict, and whether an "O(1) space" claim is honest.
Also: the length, or the substring itself?
""",
        ),
        (
            "Brute force",
            """
Every substring, checked for uniqueness: O(n³), or O(n²) with an incremental
set. At n = 5·10⁴ both are far too slow.
""",
        ),
        (
            "The insight",
            """
Keep a window with the invariant **"no repeated character"**. Grow it on the
right; when the incoming character is already inside, shrink from the left
until the invariant holds again.

The optimisation that makes it clean: rather than stepping the left edge one
position at a time, **jump it past the previous occurrence** of the incoming
character. `last_seen` remembers where that was.
""",
        ),
        (
            "The bug this problem has",
            """
`last_seen[char] >= left` is the guard, and it is load-bearing.

Without it, a character seen long *before* the current window drags the left
edge backwards, and the window stops being a window. The length then comes out
too small.

`"dvdf"` is the input that exposes it. The window grows to `dv`, then `d`
arrives — its previous position was 0, which is still `>= left`, so left
becomes 1 and the window is `vd`. Then `f` gives `vdf`, length **3**. Without
the guard, or by resetting left to 0, you get 2.

Run `"dvdf"`, not `"abcabcbb"`.
""",
        ),
        (
            "Follow-ups",
            """
- **At most k distinct characters** — the same loop with the invariant
  swapped, and a good moment to show the template generalising.
- **Return the substring** — track the start index alongside the best length.
- **Longest substring with at most one repeat** — a counting variant.
""",
        ),
    ],
}


def length_of_longest_substring(s: str) -> int:
    last_seen: dict[str, int] = {}
    left = 0
    best = 0

    for right, char in enumerate(s):
        # Only jump forward — a stale occurrence must not drag `left` back.
        if char in last_seen and last_seen[char] >= left:
            left = last_seen[char] + 1
        last_seen[char] = right
        best = max(best, right - left + 1)

    return best


CASES = [
    (("abcabcbb",), 3),
    (("bbbbb",), 1),
    (("pwwkew",), 3),
    (("dvdf",), 3),
    ((" ",), 1),
    (("au",), 2),
    (("",), 0),
]


def solve(s: str) -> int:
    return length_of_longest_substring(s)
