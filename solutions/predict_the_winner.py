"""Predict the Winner — LeetCode 486."""

from __future__ import annotations

from functools import cache

META = {
    "pattern": "dp-advanced",
    "insight": "Score one number — the mover's lead — and the opponent's optimal play enters as a minus sign, killing the whose-turn-is-it dimension.",
    "time": "O(n²)",
    "space": "O(n²) memo, O(n) if rolled into one array",
    "sections": [
        (
            "What it asks",
            """
Two players alternate taking a number from either **end** of the array. Both
play optimally. Player 1 wins if their total is greater than or **equal to**
player 2's.

Two clarifications carry real weight:

- **Ties go to player 1.** Stone Game (877) is the same recurrence with `> 0`;
  here it is `>= 0`. On `[1, 1]` the answer is `True`, and that single
  comparison is the most common wrong submission.
- **"Optimally" means maximise your own final total, not minimise theirs.**
  Zero-sum makes those identical, which is exactly what licences the
  single-number state below — say it, because it is the modelling step.
""",
        ),
        (
            "The insight",
            """
Do not track two scores and a turn flag. Track the **lead** the player to move
can force:

```
best(left, right) = max(nums[left]  - best(left+1, right),
                        nums[right] - best(left, right-1))
```

Whatever lead the opponent then builds is a deficit for you, so it comes back
negated — and because the recurrence is written from the mover's point of
view, both players use the same function. No turn parameter, no score pair,
`O(n²)` states with `O(1)` work each.

Base case `left == right`: take the last number, lead `nums[left]`.

Player 1 wins iff `best(0, n-1) >= 0`.

This is minimax with the two levels folded into one line. If you find yourself
writing `if is_player_one: max(...) else: min(...)`, you are writing twice the
code for the same table — mention that you *could*, then write the negation
form.
""",
        ),
        (
            "Edge cases and follow-ups",
            """
- **Single element**: player 1 takes it, lead ≥ 0, `True`. Empty input scores
  0–0, which the tie rule also awards to player 1 — worth stating rather than
  crashing on it.
- **All zeros**: `True` by the tie rule, and a good sanity check that you did
  not write `> 0`.
- **Sum parity shortcut does not exist here.** Unlike 877, `n` may be odd and
  the total may be even, so there is no O(1) answer. `[1, 5, 2]` and
  `[1, 3, 1]` both lose.
- **Greedy fails**: taking the larger end on `[1, 5, 233, 7]` grabs the 7 and
  hands over the 233.
- **Memory**: the memo can be rolled into one array of length `n` filled by
  increasing span, as in Stone Game — O(n) space.
- **Follow-up: return the actual moves.** Store which end won each cell and
  replay from `(0, n-1)`.
- **Follow-up: take up to `k` from the front** (Stone Game III / IV, Nim-like
  variants). The state stays "index + whose lead", but the transition becomes a
  loop over the number taken, and for the pure impartial versions the answer
  collapses to a Grundy/parity argument.
""",
        ),
    ],
}


def predict_the_winner(nums: list[int]) -> bool:
    n = len(nums)
    if n == 0:
        return True  # 0 - 0 is a tie, and ties go to player 1

    @cache
    def best(left: int, right: int) -> int:
        """Largest (mover − opponent) lead forceable on nums[left..right]."""
        if left == right:
            return nums[left]
        # The opponent's best lead is my deficit, hence the minus.
        return max(
            nums[left] - best(left + 1, right),
            nums[right] - best(left, right - 1),
        )

    lead = best(0, n - 1)
    best.cache_clear()  # the closure captures `nums`; do not keep it alive
    return lead >= 0  # tie counts as a win for player 1


CASES = [
    (([1, 5, 2],), False),
    (([1, 5, 233, 7],), True),
    (([1],), True),
    (([1, 1],), True),  # the tie rule: `>= 0`, not `> 0`
    (([0, 0],), True),
    (([1, 3, 1],), False),
    (([2, 4, 55, 6, 8],), False),
    (([1, 2, 3, 4, 5, 6],), True),
]


def solve(nums: list[int]) -> bool:
    return predict_the_winner(nums)
