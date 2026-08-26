"""Stone Game II — LeetCode 1140."""

from __future__ import annotations

from functools import cache

META = {
    "pattern": "dp-advanced",
    "insight": "Both players want the same thing, so one function suffices: my best is the suffix total minus my opponent's best.",
    "time": "O(n³) — O(n²) states, O(n) choices each",
    "space": "O(n²)",
    "sections": [
        (
            "What it asks",
            """
Piles sit in a row and are taken **from the front only**. A parameter `M`
starts at 1; a player takes the first `X` piles for any `1 ≤ X ≤ 2M`, then `M`
becomes `max(M, X)`. Both play optimally to maximise their own stone total.
Return Alice's total.

The clarifying question that saves you: *"optimal means maximise my own stones,
not maximise the difference?"* Here they coincide because the totals sum to a
constant, but say it — the same wording in other game problems does not.
""",
        ),
        (
            "The insight",
            """
Two things collapse this.

**The state is `(i, M)`, nothing else.** Piles are consumed strictly left to
right, so the past is fully summarised by how far in you are; whose turn it is
does not matter because both players optimise identically.

**Write one function for "the player to move", not two for Alice and Bob.**
Let `best(i, M)` be the most stones the mover can end up with from `piles[i:]`.
If they take `X` piles, the opponent then faces `best(i + X, max(M, X))` — and
since everything left is split between exactly the two of them:

```
best(i, M) = max over X of  suffix[i] - best(i + X, max(M, X))
```

That subtraction is the whole trick. Trying to model "Alice's turn" and "Bob's
turn" as separate recurrences doubles the code and adds nothing.

Base case: if `i + 2M ≥ n` the mover can sweep the rest, so return `suffix[i]`.
Precompute suffix sums; recomputing them inside the loop turns O(n³) into
O(n⁴) and is the usual reason this times out.
""",
        ),
        (
            "Edge cases and the bound on M",
            """
- **`M` is unbounded in the state space in principle** but capped in practice:
  once `2M ≥ n - i` the base case fires, so `M` never usefully exceeds `n`.
  That is what keeps the state count at O(n²) rather than something worse. With
  `n ≤ 100`, O(n³) is 10⁶ — instant.
- **`M` only ever grows** (`max(M, X)`), so there is no cycle and memoisation
  on a plain dict is safe.
- **Single pile**: Alice takes it, answer is the whole pile. **Empty input**
  is not in the constraints, but returning 0 costs one line.
- **Taking the most is not optimal.** `[1, 2, 3, 4, 5, 100]`: grabbing greedily
  hands the 100 to Bob. The answer is 104 — Alice takes one pile, forcing a
  sequence that leaves her the 100. Any greedy heuristic dies on this case, so
  lead with it when you are asked "why DP?".
- **Purity**: a `@cache` on a nested function keeps the closure alive between
  calls. Clear it before returning if the function will be called repeatedly
  with different inputs.
""",
        ),
    ],
}


def stone_game_ii(piles: list[int]) -> int:
    n = len(piles)
    if n == 0:
        return 0

    suffix = [0] * (n + 1)
    for i in range(n - 1, -1, -1):
        suffix[i] = suffix[i + 1] + piles[i]

    @cache
    def best(i: int, m: int) -> int:
        """Most stones the player to move can get from piles[i:]."""
        if i + 2 * m >= n:
            return suffix[i]  # sweep everything that is left
        # Whatever the opponent secures next, the rest is mine.
        return max(suffix[i] - best(i + x, max(m, x)) for x in range(1, 2 * m + 1))

    result = best(0, 1)
    best.cache_clear()  # drop the closure's memo so repeated calls stay cheap
    return result


CASES = [
    (([2, 7, 9, 4, 4],), 10),
    (([1, 2, 3, 4, 5, 100],), 104),
    (([1],), 1),
    (([],), 0),
    (([1, 2],), 3),
    (([100, 1, 1, 1, 1, 1],), 102),
    (([2, 7, 9, 4, 4, 3, 1, 8],), 18),
    (([9, 9, 9, 9, 9, 9, 9, 9, 9, 9],), 54),
]


def solve(piles: list[int]) -> int:
    return stone_game_ii(list(piles))
