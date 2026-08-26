"""Count Vowels Permutation — LeetCode 1220."""

from __future__ import annotations

META = {
    "pattern": "dp-advanced",
    "insight": "Read the rules backwards: track how many strings end in each vowel, and every rule becomes one sum.",
    "time": "O(n)",
    "space": "O(1) — five counters",
    "sections": [
        (
            "What it asks",
            """
Count strings of length `n` built only from `aeiou`, subject to a fixed
successor table: `a` may only be followed by `e`; `e` by `a` or `i`; `i` by
anything except another `i`; `o` by `i` or `u`; `u` by `a`. Answer modulo
`10⁹ + 7`.

Ask what `n` can be. LeetCode says 2·10⁴, which is small enough that an O(n)
scan is the expected answer — but if the interviewer says 10¹⁸, they are
asking for matrix exponentiation and you should say so immediately.
""",
        ),
        (
            "The insight",
            """
This is a state machine with five states, not a string problem. The only thing
a partial string's future depends on is its **last vowel**, so carry five
counters and rebuild them each step.

The trick that makes it writable in thirty seconds is to invert the table.
Forward rules ("a is followed by e") force you to push counts outward and
double-book. Backwards rules ("what can precede a?") let each new counter be a
plain sum of old ones:

```
a' = e + i + u      # a is preceded by e, i, u
e' = a + i
i' = e + o
o' = i
u' = i + o
```

Derive that inverse **at the whiteboard**, out loud, by reading each forward
rule and noting where its target appears. Doing it from memory is how you get
one term wrong and spend ten minutes debugging `n = 5`.

Start all five at 1 (every single vowel is a valid length-1 string) and apply
the update `n - 1` times. The answer is the sum, taken modulo as you go so the
integers stay machine-word sized in a language that is not Python.
""",
        ),
        (
            "Follow-ups",
            """
- **`n = 10¹⁸`.** The update is a fixed 5×5 linear map, so the answer is
  `Mⁿ⁻¹` applied to the all-ones vector. Binary exponentiation gives
  O(5³ log n) ≈ 6000 multiplies. This is the real point of the question at
  senior level; the O(n) loop is table stakes.
- **Reconstruct one such string** rather than count them: walk the counters
  backwards, choosing at each step the predecessor whose count covers the
  index you want. Same machine, run in reverse.
- **A different successor table** — the code should not change at all, only the
  five lines of the update. If your solution hard-codes vowel identities
  anywhere else, it is over-fitted.
""",
        ),
    ],
}

MOD = 10**9 + 7


def count_vowel_permutation(n: int) -> int:
    if n <= 0:
        return 0

    # Counts of strings of the current length ending in a, e, i, o, u.
    a = e = i = o = u = 1

    for _ in range(n - 1):
        # Each line reads "which vowels may precede this one".
        a, e, i, o, u = (
            (e + i + u) % MOD,
            (a + i) % MOD,
            (e + o) % MOD,
            i % MOD,
            (i + o) % MOD,
        )

    return (a + e + i + o + u) % MOD


CASES = [
    ((1,), 5),
    ((2,), 10),
    ((5,), 68),
    ((0,), 0),
    ((3,), 19),
    ((10,), 1739),
    ((144,), 18208803),
]


def solve(n: int) -> int:
    return count_vowel_permutation(n)
