"""Assign Cookies — LeetCode 455."""

from __future__ import annotations

META = {
    "pattern": "greedy",
    "insight": "Sort both sides and give the smallest adequate cookie to the hungriest child you can still satisfy — spending a bigger cookie never buys more children.",
    "time": "O(n log n + m log m)",
    "space": "O(1) beyond the sort",
    "sections": [
        (
            "What it asks",
            """
Each child `i` has a greed factor `g[i]`; each cookie `j` has a size `s[j]`.
A child is content if they receive one cookie with `s[j] >= g[i]`. One cookie
per child. Maximise the number of content children.

This is bipartite matching with an interval-like structure — and that
structure is exactly why you do not need a matching algorithm.
""",
        ),
        (
            "The insight",
            """
Sort both arrays and walk them with two pointers. For the current smallest
unsatisfied child, hand over the **smallest cookie that fits**; if the current
cookie is too small, discard it forever.

The exchange argument, which is what you should actually say:

- Discarding a cookie that cannot satisfy the *least greedy* remaining child is
  free, because it cannot satisfy anyone greedier either.
- If an optimal solution gives that child a larger cookie `s[k]` while our
  smallest fitting cookie `s[j]` sits unused, swap them. `s[j] >= g[i]` so the
  child is still content, and whoever held `s[k]`... nobody did, we just freed
  a strictly bigger cookie. The count never drops, so the greedy choice is safe.

Sorting dominates the cost; the walk itself is O(n + m).
""",
        ),
        (
            "Edge cases",
            """
- **Either array empty** → 0. The loop guard has to be `child < len(g) and
  cookie < len(s)`; a single-condition loop walks off the end.
- **More cookies than children, or the reverse** — both are normal, and the
  answer is capped by the shorter list. Cookies left over are simply unused.
- **Duplicates on both sides** are common and correct: `g = [1, 1]`,
  `s = [1, 1]` → 2. Nothing here requires distinct values.
- The wrong greedy is "give the biggest cookie to the greediest child". It
  happens to score the same on this problem, but it is far easier to get the
  pointer bookkeeping wrong, and it fails immediately on the variant where
  cookies can be **combined**.
- Advancing the child pointer on a failed match is the classic bug: a child too
  greedy for the current cookie may still be satisfiable by a later, larger one.
  Only the **cookie** pointer moves on failure.
""",
        ),
    ],
}


def find_content_children(g: list[int], s: list[int]) -> int:
    greed = sorted(g)
    sizes = sorted(s)

    child = cookie = 0
    while child < len(greed) and cookie < len(sizes):
        if sizes[cookie] >= greed[child]:
            child += 1  # content; move to the next child
        cookie += 1  # this cookie is spent or discarded either way

    return child


CASES = [
    (([1, 2, 3], [1, 1]), 1),
    (([1, 2], [1, 2, 3]), 2),
    (([10, 9, 8, 7], [5, 6, 7, 8]), 2),  # unsorted input, must sort first
    (([1, 1], [1, 1]), 2),  # duplicates on both sides
    (([], [1, 2, 3]), 0),
    (([1, 2, 3], []), 0),
    (([5], [1, 2, 3, 4]), 0),  # every cookie discarded
    (([1, 2, 3], [3]), 1),  # one big cookie serves only one child
]


def solve(g: list[int], s: list[int]) -> int:
    return find_content_children(g, s)
