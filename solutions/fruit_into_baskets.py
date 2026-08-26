"""Fruit Into Baskets — LeetCode 904."""

from __future__ import annotations

META = {
    "pattern": "sliding-window",
    "insight": "Two baskets and no skipping is just the longest subarray with at most two distinct values.",
    "time": "O(n)",
    "space": "O(1) — the map holds at most three keys",
    "sections": [
        (
            "What it asks",
            """
A row of trees, each with a fruit type. You pick from every tree starting at
some position and moving right, one fruit per tree, and you must stop the
moment you would need a **third** type. Two baskets, unlimited capacity.
Return the most fruit you can collect.

The translation is the whole trick, so do it out loud in the first thirty
seconds: **longest contiguous subarray containing at most two distinct
values**. Once phrased that way the story about baskets is noise.

Ask: can you skip a tree (no — that is what makes it contiguous), and are
fruit types bounded (they are not, so use a hash map rather than an array).
""",
        ),
        (
            "The insight",
            """
Keep a map from fruit type to its count inside the window. Grow `right`
always; while the map has more than two keys, drop `nums[left]` and delete the
key when its count hits zero — the deletion is what keeps `len(counts)` an
honest distinct-count.

"At most two distinct" is monotone under shrinking, which is what licenses the
two-pointer: removing an element can never increase the number of distinct
values. Any problem with a monotone "at most" invariant takes this same shape.

The map never exceeds three keys, so `len(counts)` is O(1) and so is the whole
loop's space.
""",
        ),
        (
            "Follow-ups",
            """
- **k baskets** — change `> 2` to `> k` and you have LeetCode 340, Longest
  Substring with At Most K Distinct Characters. Writing the helper with `k` as
  a parameter from the start costs nothing and answers the follow-up before it
  is asked.
- **Exactly k distinct** — not a single window: "exactly" is not monotone, so
  you need `atMost(k) - atMost(k - 1)`. That is LeetCode 992.
- **Streaming input, report the best window's bounds** — keep `best_left`
  alongside `best`; only update it when the width strictly improves, or you
  will report a later window of equal size.
- **Follow-up that catches people: does the answer change if you may start
  anywhere and move in either direction?** No — a leftward run is just a
  window read backwards, so the same scan covers it.
""",
        ),
    ],
}


def total_fruit(fruits: list[int], baskets: int = 2) -> int:
    counts: dict[int, int] = {}
    left = 0
    best = 0

    for right, fruit in enumerate(fruits):
        counts[fruit] = counts.get(fruit, 0) + 1

        while len(counts) > baskets:
            leaving = fruits[left]
            counts[leaving] -= 1
            if counts[leaving] == 0:
                del counts[leaving]  # the delete is what keeps len() honest
            left += 1

        best = max(best, right - left + 1)

    return best


CASES = [
    (([1, 2, 1],), 3),
    (([0, 1, 2, 2],), 3),
    (([1, 2, 3, 2, 2],), 4),
    (([3, 3, 3, 1, 2, 1, 1, 2, 3, 3, 4],), 5),
    (([1, 2, 3, 4, 5],), 2),
    (([1, 1, 1, 1],), 4),
    (([5],), 1),
    (([],), 0),
]


def solve(fruits: list[int]) -> int:
    return total_fruit(fruits)
