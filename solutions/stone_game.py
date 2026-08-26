"""Stone Game — LeetCode 877."""

from __future__ import annotations

META = {
    "pattern": "dp-advanced",
    "insight": "The first player can pre-commit to all odd-indexed piles or all even-indexed ones, and an odd total makes one group strictly bigger.",
    "time": "O(n²) for the interval DP, O(1) for the parity argument",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Piles in a row, two players alternate, each turn takes the whole pile from
one **end**. Both play optimally. Does the first player win?

The two constraints in the statement are not decoration and you should read
them aloud: the number of piles is **even**, and the total number of stones is
**odd**. Even means the players take exactly `n/2` piles each; odd means no
draw is possible.

The function here runs the general interval DP, so it also answers inputs that
break those constraints — an odd pile count, or a total that permits a tie.
Ties count as a loss for the first player, since the question is whether they
*win*.
""",
        ),
        (
            "The insight",
            """
**Track the difference, not two scores.** Let `dp[left][right]` be the best
`(me − opponent)` the player to move can force on `piles[left..right]`. Whoever
moves next faces the same problem one pile smaller, and their gain is your
loss, so the opponent's optimal difference is subtracted:

```
dp[left][right] = max(piles[left]  - dp[left+1][right],
                      piles[right] - dp[left][right-1])
```

One number per state instead of a score pair, and no "whose turn is it"
dimension — the recurrence is symmetric in the players. The first player wins
iff `dp[0][n-1] > 0`.

Fill it by increasing span length, and it collapses to a **single array**:
process length 1, 2, 3… in place, where `dp[left]` on the right-hand side still
holds the previous length's `[left, right-1]` and `dp[left+1]` holds
`[left+1, right]`. That is the O(n) space version.

**And then the punchline.** Under the stated constraints the answer is always
`True`, in O(1). Index the piles 0…n−1. Since `n` is even, the two ends always
have opposite parity, so the first player can decide up front to take *only*
even-indexed piles (or *only* odd-indexed ones) and the second player is never
offered a choice that breaks it — taking the left end at index `i` leaves ends
`i+1` and `right`, both odd if `i` was even. The odd total means
`sum(even) != sum(odd)`, so one of the two pre-commitments strictly wins, and
the first player simply picks that one.
""",
        ),
        (
            "The trap in the O(1) answer",
            """
`return True` is the right final answer and the wrong opening one. Leading
with it reads as a memorised trick, and the interviewer's next sentence is
always "now drop the even/odd guarantee" — which is LeetCode 486, the identical
DP with a different comparison.

So: state the DP, note it is O(n²) time and O(n) space, then say *"and given
that n is even and the total is odd, the answer is unconditionally true, here
is why"*. That ordering shows you can do both.

Two ways people get the parity proof wrong:

- **"The first player takes the bigger end each turn."** Plainly false —
  `[1, 3, 1]`-style shapes punish it, and with `[2, 100, 99, 1]` greedy takes 2,
  handing over 100.
- **"n even means the first player picks half, so it is symmetric."** The
  argument needs the *colouring*: the pre-commitment works only because
  removing one pile from either end of an even-length run flips both ends to the
  same parity class. On an odd-length run it fails, which is why `[1, 3, 1]`
  loses.
""",
        ),
    ],
}


def stone_game(piles: list[int]) -> bool:
    n = len(piles)
    if n == 0:
        return False  # nothing to win

    # dp[left] rolls forward by span length; at span L it holds the best
    # (me - opponent) difference on piles[left .. left + L - 1].
    dp = piles[:]  # span 1: take the only pile

    for length in range(2, n + 1):
        for left in range(n - length + 1):
            right = left + length - 1
            # dp[left+1] is still [left+1, right]; dp[left] is still [left, right-1].
            dp[left] = max(piles[left] - dp[left + 1], piles[right] - dp[left])

    # Under the problem's own constraints (n even, total odd) this is always
    # True: pre-commit to all even indices or all odd indices and take the
    # larger group. The odd total guarantees the two groups differ.
    return dp[0] > 0  # a tie is not a win


CASES = [
    (([5, 3, 4, 5],), True),
    (([3, 7, 2, 3],), True),
    (([1, 2],), True),
    (([2, 1],), True),
    (([1],), True),
    (([1, 3, 1],), False),  # odd length: the parity trick does not apply
    (([2, 2],), False),  # a tie is not a win
    (([],), False),
]


def solve(piles: list[int]) -> bool:
    return stone_game(piles)
