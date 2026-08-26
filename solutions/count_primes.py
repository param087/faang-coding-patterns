"""Count Primes — LeetCode 204."""

from __future__ import annotations

from math import isqrt

META = {
    "pattern": "math-geometry",
    "insight": "Do not ask each number whether it is prime; let each prime cross off its own multiples, starting at its square.",
    "time": "O(n log log n)",
    "space": "O(n) bits — a bytearray of n, or n/8 with a real bitset",
    "sections": [
        (
            "What it asks",
            """
Count the primes **strictly less than** `n`. LeetCode allows `n` up to
`5 × 10⁶`.

Read the boundary twice. It is *less than* `n`, not *up to* `n` — so
`countPrimes(3)` is `1` (just the 2), and `countPrimes(2)` is `0`. Getting
this backwards is the most common failure on an otherwise perfect sieve, and
it is the first thing to confirm out loud.
""",
        ),
        (
            "Trial division, and the number",
            """
The instinct is a helper: for each `k < n`, try dividing by every value up to
`√k`.

That is `Σ √k ≈ (2/3)·n^1.5` operations. At `n = 5 × 10⁶` it is roughly
**7 × 10⁹ divisions** — minutes, not milliseconds, and integer division is one
of the slowest instructions on the machine. Even skipping evens and stopping
at `√k` only buys a constant factor of about 2.

The sieve does about `n · log log n ≈ 5 × 10⁶ × 3 = 1.5 × 10⁷` writes. That
is a **500×** gap, and the operation is a byte store instead of a division.
""",
        ),
        (
            "The insight",
            """
Invert the question. Instead of asking *"is `k` prime?"* — which is expensive
— ask each prime to **eliminate its own multiples**, which is free: you just
step through the array with a stride.

```
for p = 2, 3, 4, ...:
    if p is still marked prime:
        mark 2p, 3p, 4p, ... composite
```

Every composite has a prime factor, so every composite gets crossed off by
its smallest one. Whatever survives is prime.

The cost is `Σ n/p` over primes `p < n`, and Mertens' theorem says that sum is
`n · ln ln n`. That `log log n` is essentially a constant — it is **3** at
`n = 5 × 10⁶` and only reaches 4 around `n = 10¹⁵`. Call it linear-with-a-
small-constant when explaining it.
""",
        ),
        (
            "The two bounds that matter",
            """
Both are one-token changes and both are asked about.

**Start crossing off at `p·p`, not `2p`.** Every multiple `k·p` with `k < p`
has a prime factor smaller than `p`, so it was already struck by that smaller
factor. Starting at `2p` is still correct but does redundant work — and it is
what turns the running time from `n log log n` into `n log n`, the harmonic
sum. The saving is real: for `p = 2000` you skip 1999 wasted stores.

**Stop the outer loop at `√n`.** If `p > √n` then `p·p ≥ n` and the inner loop
body never runs. Continuing past it is harmless but pointless. Precisely:
iterate `p` while `p·p < n`, i.e. `p ≤ isqrt(n - 1)`.

Together they are why the answer is `n log log n` and not `n log n` — worth
saying explicitly rather than letting the interviewer wonder if you knew.

One implementation note: `sieve[p*p::p] = bytearray(len(...))` hands the
striding to C. It is the same algorithm, but on `n = 5 × 10⁶` it is roughly an
order of magnitude faster than a Python `for` loop, which matters when the
grader has a time limit.
""",
        ),
        (
            "Dry run",
            """
`n = 30`. Only `p = 2, 3, 4, 5` are considered, since `isqrt(29) = 5`.

- `p = 2` → strike `4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28`
- `p = 3` → start at **9**, not 6: strike `9, 15, 21, 27` (12, 18, 24 already gone)
- `p = 4` → already struck, skip
- `p = 5` → start at **25**: strike `25` only

Survivors: `2, 3, 5, 7, 11, 13, 17, 19, 23, 29` → **10**. Note `p = 7` was
never visited, because `49 > 30`; nothing was missed, because every composite
below 30 has a factor at most 5.
""",
        ),
        (
            "Follow-ups",
            """
- **`n = 10¹²`, count primes below it** — the array does not fit. A
  **segmented sieve** is the answer: sieve `[2, √n]` normally, then sweep the
  range in cache-sized blocks, striking each block with those base primes.
  O(√n) memory. If they only want the *count*, that is the Meissel–Mertens /
  Lucy_Hedgehog territory and worth naming rather than deriving.
- **"Also give me the factorisation of any k < n"** — store the *smallest
  prime factor* instead of a boolean. Same sieve, `int32` array, and then
  factorising any `k` is O(log k) lookups.
- **Linear sieve** — O(n) exactly, by ensuring each composite is struck by its
  smallest prime factor precisely once. Faster in theory; usually *slower* in
  practice than the byte-slice sieve because it destroys the cache-friendly
  stride pattern. That trade-off is a good thing to have an opinion about.
- **Memory** — a `bytearray` is 1 byte per number; a bitset is 8× smaller, and
  skipping even numbers halves it again. At `n = 5 × 10⁶` a bytearray is 5 MB,
  which is fine; at `10⁹` it is not.
- **Sanity check** — the prime counting function `π(n) ≈ n / ln n`. For
  `n = 10⁶` that predicts ~72,000 against the true 78,498. Handy for catching
  an off-by-one that shifts the answer by a factor, not by one.
""",
        ),
    ],
}


def count_primes(n: int) -> int:
    if n < 3:  # strictly less than n, so n = 2 has no primes below it
        return 0

    sieve = bytearray([1]) * n
    sieve[0:2] = b"\x00\x00"  # 0 and 1 are not prime

    for p in range(2, isqrt(n - 1) + 1):  # largest p with p*p < n
        if sieve[p]:
            # Start at p*p: anything smaller already has a smaller prime factor.
            sieve[p * p :: p] = bytearray(len(range(p * p, n, p)))

    return sum(sieve)


CASES = [
    ((10,), 4),
    ((0,), 0),
    ((1,), 0),
    ((2,), 0),
    ((3,), 1),
    ((5,), 2),
    ((30,), 10),
    ((100,), 25),
    ((1000,), 168),
]


def solve(n: int) -> int:
    return count_primes(n)
