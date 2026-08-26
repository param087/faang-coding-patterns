"""Two City Scheduling — LeetCode 1029."""

from __future__ import annotations

META = {
    "pattern": "greedy",
    "insight": "Send everyone to city A, then refund the n people whose B-minus-A saving is largest — i.e. sort by the cost difference.",
    "time": "O(n log n)",
    "space": "O(n) for the sorted copy",
    "sections": [
        (
            "What it asks",
            """
`2n` candidates, each with a cost to fly to city A and a cost to fly to city B.
Exactly `n` must go to each city. Minimise the total.

The balance constraint is the entire difficulty. Without it you would pick the
cheaper city per person and be done in one pass; with it, a person who is cheap
for A may still have to go to B because someone else needs the A slot more.
""",
        ),
        (
            "The insight",
            """
Think in terms of **regret**, not absolute cost. Pretend everyone flies to A,
paying `sum(a)`. Sending person `i` to B instead changes the bill by
`b[i] - a[i]` — negative means it saves money, positive means it costs money.

You must move exactly `n` people, and the moves are independent: the totals add
with no interaction. So move the `n` people with the smallest `b[i] - a[i]`.
Equivalently, sort by `a[i] - b[i]` ascending and give A to the first half, B to
the second half.

The exchange argument in one line: if an optimal assignment sends `x` to A and
`y` to B while `a[x] - b[x] > a[y] - b[y]`, swapping them changes the total by
`(a[y] + b[x]) - (a[x] + b[y]) < 0`, so it was not optimal. Hence any optimum
is sorted by the difference.

Do not reach for min-cost-max-flow or the 2-D DP `dp[i][j]` here. Both are
correct; both are the answer to a harder question than the one asked. Name the
DP as your fallback if the interviewer disputes the greedy, then prove the
exchange.
""",
        ),
        (
            "Edge cases",
            """
- **Odd-length input** is invalid by the constraints; `n = len(costs) // 2`
  silently truncates rather than raising, which is the pragmatic choice in an
  interview but worth flagging as an assumption.
- **Empty list → 0.** The slice arithmetic handles it without a special case.
- **Ties in the difference** are genuinely arbitrary — either ordering yields
  the same total, so a stable sort is fine and no tie-breaker is needed.
- **Sorting by `a[i]` alone** is the common wrong answer: it ignores that a
  cheap A-flight matters only relative to that person's B-flight. `[[10, 20],
  [30, 200]]` — person 0 is cheaper for A in absolute terms, but person 1 has
  far more to lose by going to B, so person 1 takes the A slot.
- The input rows must not be mutated: sort a copy, since `solve` is reused
  across runs.
""",
        ),
    ],
}


def two_city_sched_cost(costs: list[list[int]]) -> int:
    # Ascending by regret: negative first = "much cheaper in A than in B".
    ordered = sorted(costs, key=lambda pair: pair[0] - pair[1])
    n = len(ordered) // 2

    return sum(a for a, _ in ordered[:n]) + sum(b for _, b in ordered[n:])


CASES = [
    (([[10, 20], [30, 200], [400, 50], [30, 20]],), 110),
    (([[259, 770], [448, 54], [926, 667], [184, 139], [840, 118], [577, 469]],), 1859),
    (
        (
            [
                [515, 563],
                [451, 713],
                [537, 709],
                [343, 819],
                [855, 779],
                [457, 60],
                [650, 359],
                [631, 42],
            ],
        ),
        3086,
    ),
    (([[10, 20], [30, 200]],), 50),  # cheaper-in-A alone picks the wrong person
    (([[1, 2], [2, 1]],), 2),
    (([[5, 5], [5, 5]],), 10),  # ties: any split is optimal
    (([],), 0),
]


def solve(costs: list[list[int]]) -> int:
    return two_city_sched_cost(costs)
