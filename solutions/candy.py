"""Candy — LeetCode 135."""

from __future__ import annotations

META = {
    "pattern": "greedy",
    "insight": "Each neighbour is a one-way constraint, so satisfy the left-to-right ones in one sweep, the right-to-left ones in another, and take the max.",
    "time": "O(n)",
    "space": "O(n), reducible to O(1)",
    "sections": [
        (
            "What it asks",
            """
Children in a line with ratings. Every child gets at least one candy, and a
child with a **strictly higher** rating than an adjacent neighbour must get
more candies than that neighbour. Minimise the total.

Two clarifications decide the whole solution:

- **Strictly higher.** Equal ratings impose *no* constraint in either
  direction, so ties are a hard reset — `[1, 2, 2]` is `1 + 2 + 1 = 4`, not 5.
- The constraint is only against **immediate** neighbours, not the whole array.
  A child three seats away with a huge rating is irrelevant.
""",
        ),
        (
            "Brute force, and why it fails",
            """
The natural first move is relaxation: start everyone at 1, sweep repeatedly,
bump any child that violates a neighbour, stop when a full pass changes
nothing.

That is correct but the number of passes is the length of the longest
monotone run. On a strictly increasing array of n = 2·10⁴ ratings it needs
~n passes of n work each: **4·10⁸ operations** for an input LeetCode expects
you to handle instantly.

The other tempting move — sort the indices by rating and assign in increasing
order, taking `max(left, right) + 1` — is actually *correct*, and it is worth
knowing as the "prove it works" argument. But it costs O(n log n) for a
problem that is O(n), and it is fiddly to write under pressure.
""",
        ),
        (
            "The insight",
            """
Every edge in the line is really **two independent one-way constraints**:

- if `ratings[i] > ratings[i-1]` then `candy[i] > candy[i-1]`;
- if `ratings[i] > ratings[i+1]` then `candy[i] > candy[i+1]`.

The first family only ever propagates left→right; the second only ever
propagates right→left. So they do not interfere, and each can be solved by a
single sweep in its own direction:

```
left[i]  = left[i-1]  + 1  if ratings[i] > ratings[i-1]  else 1
right[i] = right[i+1] + 1  if ratings[i] > ratings[i+1]  else 1
```

Taking `max(left[i], right[i])` satisfies both families at once, and it is
minimal because each of `left[i]` and `right[i]` is itself a lower bound: to
sit at the top of an ascending run of length `k` you *must* have at least `k`
candies, whichever direction the run came from.

The max — not the sum, not the left value alone — is the entire trick.
""",
        ),
        (
            "The peak is what decides it",
            """
The single-array variant everyone writes first does the forward pass, then
walks backwards doing `candy[i] = max(candy[i], candy[i+1] + 1)`. That works
**only if you keep the max**. Writing the backward pass as a plain assignment
destroys the forward result and quietly breaks every peak.

Take `[1, 3, 4, 5, 2]`. Forward gives `[1, 2, 3, 4, 1]`. The backward pass
sees `2 < 5` at index 3, so index 3 needs more than index 4 → `max(4, 2) = 4`.
Overwriting instead of maxing would set it to 2 and break the ascent behind it.

The dual to that is a **valley**: `[1, 0, 2]`. Forward `[1, 1, 2]`, backward
`[2, 1, 2]`. The child at index 1 is the local minimum and correctly keeps 1.
If your code ever gives a strict local minimum more than one candy, you are
not minimal.
""",
        ),
        (
            "Dry run",
            """
`[1, 2, 87, 87, 87, 2, 1]` — the case that catches tie handling.

| i | rating | left | right | max |
|---|--------|------|-------|-----|
| 0 | 1  | 1 | 1 | 1 |
| 1 | 2  | 2 | 1 | 2 |
| 2 | 87 | 3 | 1 | 3 |
| 3 | 87 | 1 | 1 | 1 |
| 4 | 87 | 1 | 3 | 3 |
| 5 | 2  | 1 | 2 | 2 |
| 6 | 1  | 1 | 1 | 1 |

Total **13**. Index 3 sits between two 87s and gets a single candy — no
constraint binds it in either direction. Anyone treating `>=` as the trigger
returns 15 here.
""",
        ),
        (
            "Follow-ups",
            """
- **O(1) extra space.** There is a one-pass version that tracks the length of
  the current `up` run, the current `down` run, and the last peak, adding the
  triangular numbers as it goes and paying the peak an extra candy only when
  the descent grows longer than the ascent. It is genuinely harder to get
  right; offer it, then ask whether they want it written.
- **Children in a circle** — the two-sweep argument collapses, because the
  constraints are no longer acyclic. Handle it by cutting the circle at a
  position where the constraint is slack (a tie, or a strict local minimum);
  if the ratings are all equal the answer is just n.
- **A 2-D grid with the same rule** — now the constraint graph has no fixed
  sweep order, so you sort cells by value and relax in increasing order, which
  is exactly the O(n log n) fallback from above.
""",
        ),
    ],
}


def candy(ratings: list[int]) -> int:
    n = len(ratings)
    if n == 0:
        return 0

    candies = [1] * n

    # Left-to-right: satisfy "higher than my left neighbour".
    for i in range(1, n):
        if ratings[i] > ratings[i - 1]:
            candies[i] = candies[i - 1] + 1

    # Right-to-left: satisfy "higher than my right neighbour" without
    # destroying the forward result — hence max, not assignment.
    for i in range(n - 2, -1, -1):
        if ratings[i] > ratings[i + 1]:
            candies[i] = max(candies[i], candies[i + 1] + 1)

    return sum(candies)


CASES = [
    (([1, 0, 2],), 5),
    (([1, 2, 2],), 4),  # ties reset: no constraint between equal ratings
    (([1, 2, 87, 87, 87, 2, 1],), 13),
    (([1, 3, 4, 5, 2],), 11),  # peak needs the max of both sweeps
    (([5, 4, 3, 2, 1],), 15),  # pure descent, forward pass alone gives 5
    (([1, 2, 3, 4, 5],), 15),
    (([2, 2, 2, 2],), 4),
    (([7],), 1),
    (([],), 0),
]


def solve(ratings: list[int]) -> int:
    return candy(ratings)
