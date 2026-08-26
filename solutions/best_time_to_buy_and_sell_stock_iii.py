"""Best Time to Buy and Sell Stock III — LeetCode 123."""

from __future__ import annotations

META = {
    "pattern": "dp-advanced",
    "insight": "Two transactions is a four-state machine — hold-1, sold-1, hold-2, sold-2 — and each state is one running maximum.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Buy and sell a stock **at most twice**, never holding two positions at once,
and return the maximum profit.

Ask two things before writing anything. Can you buy and sell on the same day
(it never helps, so it does not matter — but saying so shows you checked the
overlap rule). And is it *at most* two or *exactly* two? "At most" is why
every state starts at a value that means "not done yet" rather than being
forced.

The obvious first answer — split the array at every index `i`, take the best
one-transaction profit on each half, maximise — is correct and O(n) after two
prefix passes. It is worth stating, because the interviewer usually wants the
state machine that generalises to LeetCode 188.
""",
        ),
        (
            "The insight",
            """
At the close of any day you are in exactly one of four states:

| state | meaning | best value so far |
|---|---|---|
| `buy1` | holding the first position | `max(buy1, -price)` |
| `sell1` | first transaction closed | `max(sell1, buy1 + price)` |
| `buy2` | holding the second position | `max(buy2, sell1 - price)` |
| `sell2` | second transaction closed | `max(sell2, buy2 + price)` |

Each line is a running maximum over "stay where I am" versus "move here from
the previous state, paying or receiving today's price". Cash-flow accounting
keeps it in one variable per state: buying subtracts the price, selling adds
it, so `sell2` is already the profit.

**Update them in order, in the same loop iteration.** `buy2` reading the
`sell1` that was just written this iteration models selling and rebuying on
the same day, which is a no-op that can never beat not doing it, so the
in-order update is safe — and it is one fewer array than the textbook version.

`sell2 >= sell1` always holds because the second transaction can be empty, so
returning `sell2` covers the "use only one transaction" and "trade nothing"
cases without a special branch.
""",
        ),
        (
            "Edge cases",
            """
- **Monotonically decreasing prices** (`[7,6,4,3,1]`): every `sell` stays at
  its 0 seed and the answer is 0. That is what the 0 seed is for — a negative
  seed would let a losing trade through.
- **Fewer than two prices**: the loop runs at most once, `sell2` stays 0.
- **A single long rise** (`[1,2,3,4,5]`): the answer is 4, not 8. The states
  cannot double-count the same rise because `buy2` is funded out of `sell1`,
  which already consumed it.
- **`buy1` seeded at −infinity**, not 0. Seeding it at 0 would mean "I am
  holding a position I acquired for free", which invents profit on the first
  day. Python's `float("-inf")` is fine; in an integer language use a
  sentinel like `-10**9`, not `INT_MIN`, or `buy1 + price` overflows.
- Do not sort or dedupe the prices. The order *is* the problem.
""",
        ),
    ],
}


def max_profit(prices: list[int]) -> int:
    # Cash on hand in each of the four states, best-so-far.
    buy1 = buy2 = float("-inf")  # holding position 1 / position 2
    sell1 = sell2 = 0  # position 1 closed / position 2 closed

    for price in prices:
        buy1 = max(buy1, -price)  # spend price to open the first
        sell1 = max(sell1, buy1 + price)  # close the first
        buy2 = max(buy2, sell1 - price)  # reopen out of the first profit
        sell2 = max(sell2, buy2 + price)  # close the second

    return int(sell2)  # >= sell1 >= 0, so it covers 1 and 0 transactions too


CASES = [
    (([3, 3, 5, 0, 0, 3, 1, 4],), 6),
    (([1, 2, 3, 4, 5],), 4),
    (([7, 6, 4, 3, 1],), 0),
    (([1, 2, 4, 2, 5, 7, 2, 4, 9, 0],), 13),
    (([2, 1, 2, 0, 1],), 2),
    (([5, 5, 5],), 0),
    (([1],), 0),
    (([],), 0),
]


def solve(prices: list[int]) -> int:
    return max_profit(prices)
