"""Longest Repeating Character Replacement — LeetCode 424."""

from __future__ import annotations

from collections import defaultdict

META = {
    "pattern": "sliding-window",
    "insight": "A window is fixable when its length minus its most common count is at most k, so the window never has to shrink — only slide.",
    "time": "O(n)",
    "space": "O(1) — at most 26 counts",
    "sections": [
        (
            "What it asks",
            """
Change at most `k` characters of `s`, any characters to any letters, and
return the longest run of one repeated letter you can produce.

Ask: **do the k changes have to be used?** (No, at most.) **Is the alphabet
uppercase A–Z?** (Yes on LeetCode — that is what makes the count array O(1),
and it is worth saying rather than assuming.)

The reframing that does the work: you are looking for the longest window in
which all-but-one character kind can be repainted within budget.
""",
        ),
        (
            "The insight",
            """
Keep the letter that already dominates the window and repaint the rest. So a
window `[left, right]` is achievable exactly when

```
(right - left + 1) - maxCount <= k
```

where `maxCount` is the frequency of the most common letter inside it.

Grow `right` every step. When the window becomes unachievable, move `left`
**once** — not in a `while` loop. That is deliberate: the window is never
allowed to get smaller than the best one found so far, so it slides at fixed
width until a genuinely better width appears. The answer is therefore the
final width, `len(s) - left`, with no `best` variable at all.
""",
        ),
        (
            "The stale maxCount that everyone flags as a bug",
            """
`maxCount` is never decreased when a character leaves the window, so it can be
larger than any count actually present. Reviewers call this out every time —
and it is fine.

A stale `maxCount` can only make the validity test **too permissive**, and
being too permissive at width `w` cannot manufacture an answer larger than
`w`, because the width only grows when a real letter reaches a new record
count. In other words: a wrong-but-high `maxCount` keeps the window sliding,
it never widens it. Recomputing `max(counts.values())` each step is also
correct and costs O(26) per index — say that you know both and picked the
cheap one on purpose.

The trap in the other direction is writing `while` instead of `if` **and**
keeping the stale `maxCount`. That combination does shrink on stale data and
returns answers that are too small.
""",
        ),
    ],
}


def character_replacement(s: str, k: int) -> int:
    counts: defaultdict[str, int] = defaultdict(int)
    left = 0
    max_count = 0  # deliberately never decremented; see the notes

    for right, char in enumerate(s):
        counts[char] += 1
        max_count = max(max_count, counts[char])

        # `if`, not `while`: the window slides at its best-so-far width.
        if right - left + 1 - max_count > k:
            counts[s[left]] -= 1
            left += 1

    return len(s) - left


CASES = [
    (("ABAB", 2), 4),
    (("AABABBA", 1), 4),
    (("BAAAB", 2), 5),
    (("ABBB", 2), 4),
    (("ABCDE", 0), 1),
    (("AAAA", 2), 4),
    (("A", 0), 1),
    (("", 2), 0),
]


def solve(s: str, k: int) -> int:
    return character_replacement(s, k)
