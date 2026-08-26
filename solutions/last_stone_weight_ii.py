"""Last Stone Weight II — LeetCode 1049."""

from __future__ import annotations

META = {
    "pattern": "dp-grid-knapsack",
    "insight": "Every smash just assigns a plus or minus sign to a stone, so the answer is the smallest |sum − 2·subset| — a subset-sum knapsack.",
    "time": "O(n · sum)",
    "space": "O(sum)",
    "sections": [
        (
            "What it asks",
            """
Repeatedly smash two stones together; equal weights annihilate, unequal ones
leave the difference. Return the smallest possible weight left at the end (0 if
nothing remains).

Ask whether you may choose **which** pair to smash each round — you may, and
that freedom is the whole problem. Weights are positive and `sum ≤ 3000`, which
is the tell that a table indexed by sum is intended.
""",
        ),
        (
            "The insight",
            """
Unfold the smashing. `a - b` is `+a - b`; smash the result against `c` and you
get `±(a - b) - c`. Every stone ends up with a **sign**, and any assignment of
signs (with at least one `+`) is achievable by choosing the smash order. So the
reachable end weights are

```
| Σ_{i ∈ S} w_i − Σ_{i ∉ S} w_i |  =  | total − 2 · sum(S) |
```

Minimising that means finding the subset sum closest to `total / 2` **without
exceeding it** — a 0/1 knapsack with weight = value = stone, capacity
`total // 2`. The answer is `total - 2 · best`.

> `reachable[s]` = can some subset of the stones processed so far total `s`?

The inner loop runs **downwards** from the capacity. Going upwards would let one
stone be reused within its own pass, silently turning this into unbounded
knapsack. `n · sum/2` is about 45 000 cell updates at the limits.
""",
        ),
        (
            "Pitfall: this is not Last Stone Weight I",
            """
Problem 1046 is a max-heap simulation: always smash the two heaviest. Reaching
for that here is the standard wrong answer, and it fails on the problem's own
example.

`[31, 26, 33, 21, 40]` under greedy: 40−33 = 7, then 31−26 = 5, then 21−7 = 14,
then 14−5 = **9**.

The DP finds the split `{33, 40} = 73` against `{31, 26, 21} = 78`, for an answer
of **5**. Total is 151, half is 75, and 73 is the largest reachable sum at or
below it.

Greedy is off by 80% on the problem's own example. Say out loud that the smash
order changes which signs are reachable, so local choices are not independent,
then write the knapsack.
""",
        ),
    ],
}


def last_stone_weight_ii(stones: list[int]) -> int:
    total = sum(stones)
    half = total // 2

    reachable = [False] * (half + 1)
    reachable[0] = True  # the empty subset

    for stone in stones:
        # Downwards: each stone may contribute to a sum only once.
        for s in range(half, stone - 1, -1):
            if reachable[s - stone]:
                reachable[s] = True

    best = max(s for s in range(half + 1) if reachable[s])
    return total - 2 * best


def last_stone_weight_ii_bitset(stones: list[int]) -> int:
    """The same DP as one big integer — bit `s` set means sum `s` is reachable."""
    total = sum(stones)
    reachable = 1
    for stone in stones:
        reachable |= reachable << stone

    half = total // 2
    best = max(s for s in range(half + 1) if reachable >> s & 1)
    return total - 2 * best


CASES = [
    (([2, 7, 4, 1, 8, 1],), 1),
    (([31, 26, 33, 21, 40],), 5),  # the max-heap greedy answers 9
    (([1],), 1),
    (([],), 0),
    (([1, 1],), 0),
    (([3, 3, 3],), 3),  # odd count of equal stones can never cancel out
    (([1, 2],), 1),
    (([2, 2, 2, 2, 2, 2, 2],), 2),
]


def solve(stones: list[int]) -> int:
    return last_stone_weight_ii(list(stones))


def check() -> None:
    for args, expected in CASES:
        assert last_stone_weight_ii(*args) == expected, args
        assert last_stone_weight_ii_bitset(*args) == expected, args
