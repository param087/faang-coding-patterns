"""Design A Leaderboard — LeetCode 1244."""

from __future__ import annotations

from collections import defaultdict
from heapq import nlargest

META = {
    "pattern": "design",
    "symbol": "Leaderboard",
    "insight": "Only the sum of the top K matters, never the ordering, so store raw totals and pay for ranking lazily inside top().",
    "time": "O(1) add and reset, O(n log k) top",
    "space": "O(n) in players",
    "sections": [
        (
            "What it asks",
            """
This one is premium, so the statement is not public — described in my own
words: maintain a scoreboard supporting three operations. `add_score(player,
score)` adds points to a player's running total, creating the player if this
is their first score. `top(k)` returns the **sum** of the k highest totals.
`reset(player)` wipes that player's total back to zero.

Ask before writing anything: **does `top` need the players, or just the sum?**
(Just the sum — which is why no ordered structure is needed.) Is `k` bounded by
the player count (yes)? Can scores be negative? Does `reset` remove the player
or zero them — it matters only if zero-scored players can appear in `top`.
""",
        ),
        (
            "The insight",
            """
The tempting move is to keep a sorted structure of scores so `top` is a prefix
sum. Resist it: every `add_score` then costs a delete plus an insert to keep
the order, and the ordering is thrown away one line later when you sum.

A plain `dict` of player → total is the right store. `add_score` and `reset`
are O(1) hash operations. `top(k)` is `heapq.nlargest`, which runs a bounded
size-k heap over the values in **O(n log k)** — not a full O(n log n) sort.

With n = 10⁴ players and 10⁴ calls, that is comfortably inside limits, and the
data structure has no invariant to corrupt. Say out loud that you are choosing
where to pay: constant-time writes and a linear-ish read, because writes
dominate the call mix in a leaderboard.
""",
        ),
        (
            "Follow-ups",
            """
- **"What if `top` is called far more often than `add_score`?"** Now the
  trade-off flips. Keep a `SortedList` of scores (or a Fenwick tree indexed by
  score, if scores are small integers) so `top` is O(k log n) and updates are
  O(log n). Name the crossover rather than claiming one is simply better.
- **"Return the players, not the sum."** `nlargest` on `.items()` with a
  tie-break key — and now you must ask how ties are broken, because the sum
  version never had to care.
- **Real scale** — a global leaderboard is sharded by player id, each shard
  keeps its local top k, and a merge step combines them; the exact global rank
  of player 4,000,001 is usually not worth computing.
- **Concurrency** — `add_score` is read-modify-write, so it needs an atomic
  increment or a per-player lock, not a plain `+=`.
""",
        ),
    ],
}


class Leaderboard:
    def __init__(self) -> None:
        # Player -> running total. No ordering is maintained on purpose.
        self.scores: dict[int, int] = defaultdict(int)

    def add_score(self, player_id: int, score: int) -> None:
        self.scores[player_id] += score

    def top(self, k: int) -> int:
        # Bounded heap of size k: O(n log k), not a full sort.
        return sum(nlargest(k, self.scores.values()))

    def reset(self, player_id: int) -> None:
        self.scores.pop(player_id, None)


CASES: list[tuple[tuple, object]] = []


def check() -> None:
    board = Leaderboard()
    board.add_score(1, 73)
    board.add_score(2, 56)
    board.add_score(3, 39)
    board.add_score(4, 51)
    board.add_score(5, 4)
    assert board.top(1) == 73
    board.reset(1)
    board.reset(2)
    board.add_score(2, 51)
    assert board.top(3) == 141  # 51 + 51 + 39, ties are irrelevant to a sum

    # Repeated scores accumulate rather than replace.
    accumulating = Leaderboard()
    accumulating.add_score(7, 10)
    accumulating.add_score(7, 15)
    assert accumulating.top(1) == 25
    assert accumulating.top(5) == 25  # k larger than the roster is harmless

    # An empty board, and k = 0.
    empty = Leaderboard()
    assert empty.top(3) == 0
    assert empty.top(0) == 0

    # Reset removes the player entirely; resetting twice must not raise.
    removing = Leaderboard()
    removing.add_score(1, 100)
    removing.add_score(2, 20)
    removing.reset(1)
    removing.reset(1)
    assert removing.top(2) == 20

    # A player scoring again after a reset starts from zero.
    revived = Leaderboard()
    revived.add_score(1, 100)
    revived.reset(1)
    revived.add_score(1, 5)
    assert revived.top(1) == 5
