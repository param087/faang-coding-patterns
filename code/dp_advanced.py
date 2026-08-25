"""Advanced DP: state machines, bitmask, interval DP, tree DP, game theory.

These share one idea — the state is richer than an index. It might be an index
plus a *mode* (holding a stock or not), a *set* of visited nodes packed into
an integer, an *interval* rather than a prefix, or a node in a tree.

The tell for bitmask DP is a constraint of n <= 20. Nothing else lets you
afford 2^n states.
"""

from __future__ import annotations

from functools import cache


def max_profit_with_cooldown(prices: list[int]) -> int:
    """Best Time to Buy and Sell Stock with Cooldown — a state machine.

    Three states, and naming them is the solution: `holding` (own a share),
    `sold` (just sold, so tomorrow is a cooldown), `resting` (free to buy).
    Drawing the three-node transition diagram before coding turns this from
    a puzzle into transcription.
    """
    if not prices:
        return 0

    holding = -prices[0]
    sold = float("-inf")
    resting = 0

    for price in prices[1:]:
        previous_sold = sold
        sold = holding + price  # sell today
        holding = max(holding, resting - price)  # keep, or buy from rest
        resting = max(resting, previous_sold)  # rest, or come off cooldown

    return int(max(sold, resting))


def burst_balloons(nums: list[int]) -> int:
    """Maximum coins from bursting balloons — interval DP.

    The reframe that makes it tractable: iterating over which balloon to burst
    *first* fails, because the neighbours keep changing. Instead ask which
    balloon in an interval is burst **last** — then its neighbours are the
    fixed interval boundaries, and the two sides become independent
    subproblems.

    O(n^3), and the padding with 1s removes every boundary special case.
    """
    balloons = [1, *nums, 1]
    n = len(balloons)
    dp = [[0] * n for _ in range(n)]

    # `length` is the gap between the (exclusive) boundaries.
    for length in range(2, n):
        for left in range(n - length):
            right = left + length
            for last in range(left + 1, right):
                dp[left][right] = max(
                    dp[left][right],
                    dp[left][last]
                    + balloons[left] * balloons[last] * balloons[right]
                    + dp[last][right],
                )

    return dp[0][n - 1]


def rob_tree(edges: dict[int, list[int]], values: dict[int, int], root: int) -> int:
    """House Robber III — DP over a tree.

    Each node returns a *pair*: the best if this node is robbed, and the best
    if it is not. Returning a single number cannot work, because the parent's
    choice depends on whether the child was taken. That pair-return shape is
    the tree-DP idiom.
    """

    def visit(node: int, parent: int) -> tuple[int, int]:
        robbed = values[node]
        skipped = 0
        for child in edges.get(node, ()):
            if child == parent:
                continue
            child_robbed, child_skipped = visit(child, node)
            robbed += child_skipped  # can't rob adjacent
            skipped += max(child_robbed, child_skipped)
        return robbed, skipped

    return max(visit(root, -1))


def shortest_path_all_nodes(graph: list[list[int]]) -> int:
    """Visit every node at least once — bitmask BFS over (node, visited-set).

    n <= 12 in the original problem, which is the constraint announcing
    bitmask. The state is a node plus the set of nodes seen so far, packed
    into an int; there are n·2^n such states, which is 49,152 at n = 12.
    """
    from collections import deque

    n = len(graph)
    if n == 1:
        return 0

    full = (1 << n) - 1
    queue: deque[tuple[int, int, int]] = deque((i, 1 << i, 0) for i in range(n))
    seen = {(i, 1 << i) for i in range(n)}

    while queue:
        node, visited, steps = queue.popleft()
        for neighbour in graph[node]:
            mask = visited | (1 << neighbour)
            if mask == full:
                return steps + 1
            if (neighbour, mask) not in seen:
                seen.add((neighbour, mask))
                queue.append((neighbour, mask, steps + 1))

    return 0


def stone_game(piles: list[int]) -> bool:
    """Can the first player win, both playing optimally? Minimax DP.

    The idiom: define the state as the *difference* in scores rather than two
    separate totals. `best(i, j)` is how far ahead the player to move can get,
    so the opponent's turn is simply a subtraction — one number instead of a
    whose-turn-is-it flag.
    """

    @cache
    def best(i: int, j: int) -> int:
        if i > j:
            return 0
        take_left = piles[i] - best(i + 1, j)
        take_right = piles[j] - best(i, j - 1)
        return max(take_left, take_right)

    result = best(0, len(piles) - 1) > 0
    best.cache_clear()
    return result


CASES = [
    (([1, 2, 3, 0, 2],), 3),
    (([1],), 0),
    (([],), 0),
    (([2, 1, 4],), 3),
]


def solve(prices: list[int]) -> int:
    return max_profit_with_cooldown(prices)


def check() -> None:
    for args, expected in CASES:
        assert max_profit_with_cooldown(*args) == expected

    assert burst_balloons([3, 1, 5, 8]) == 167
    assert burst_balloons([1, 5]) == 10
    assert burst_balloons([]) == 0

    edges = {1: [2, 3], 2: [4], 3: [], 4: []}
    values = {1: 3, 2: 2, 3: 3, 4: 1}
    # Robbing the root (3) forces skipping 2 and 3, leaving only 4: total 4.
    # Skipping the root allows 2 and 3: total 5.
    assert rob_tree(edges, values, 1) == 5

    assert shortest_path_all_nodes([[1, 2, 3], [0], [0], [0]]) == 4
    assert shortest_path_all_nodes([[1], [0, 2, 4], [1, 3, 4], [2], [1, 2]]) == 4
    assert shortest_path_all_nodes([[]]) == 0

    assert stone_game([5, 3, 4, 5]) is True
    assert stone_game([3, 7, 2, 3]) is True
