"""Beautiful Array — LeetCode 932."""

from __future__ import annotations

from functools import cache

META = {
    "pattern": "divide-and-conquer",
    "insight": "Odds first, evens second: an odd plus an even is never 2·A[k], and each half is a smaller beautiful array rescaled.",
    "time": "O(n log n)",
    "space": "O(n log n)",
    "sections": [
        (
            "What it asks",
            """
Produce any permutation of `1..n` in which no element is the **average of two
elements straddling it**: there is no `i < k < j` with
`A[i] + A[j] == 2 · A[k]`.

Any valid array is accepted, which is the licence you need — you are not
searching for a specific answer, you are *constructing* one. Say that out
loud, because the instinct is to backtrack over permutations, and at n = 1000
that search never returns.
""",
        ),
        (
            "The insight",
            """
Two facts, and the problem collapses.

**1. Parity separates.** Put all the odd values before all the even values.
Then any triple with `A[i]` odd and `A[j]` even has an **odd** sum, while
`2 · A[k]` is always even — so no violating triple can cross the boundary.
Only triples wholly inside the odd block or wholly inside the even block can
break the rule.

**2. Beauty survives affine maps.** If `A` is beautiful, so is
`{a·x + b}` for any `a ≠ 0`, because the condition
`A[i] + A[j] = 2·A[k]` is preserved and reflected exactly by
`a·A[i] + b + a·A[j] + b = 2·(a·A[k] + b)`.

The odd values `1, 3, 5, …` are `2x - 1` over `x = 1, 2, 3, …`, and the evens
are `2x`. So:

```
beautiful(n) = [2x - 1 for x in beautiful(⌈n/2⌉)]
             + [2x     for x in beautiful(⌊n/2⌋)]
```

`⌈n/2⌉` odd values and `⌊n/2⌋` even values in `1..n`. The recursion halves,
each level costs O(n), so it is O(n log n) — and there is no search anywhere in
it.
""",
        ),
        (
            "Why subsequences stay beautiful — and how to check the answer",
            """
The condition only ever forbids triples, so **deleting elements can never
create a violation**. Two consequences worth having ready:

- The popular iterative variant — start from `[1]`, apply the doubling step
  until the array is at least `n` long, then filter out everything `> n` —
  is correct for exactly this reason. It builds a beautiful permutation of
  `1..2^k` and keeps a subsequence.
- Memoising on `n` is free (`@cache`), and matters if the function is called
  repeatedly: the two recursive sizes differ by at most one, so the cache is
  hit almost every time.

Because any valid array passes, **verify by property, not by equality**. The
`check()` below asserts the output is a permutation of `1..n` and then does an
O(n²) sweep: for every pair `i < j` whose sum is even, look up
`(A[i] + A[j]) / 2` and confirm its position is not between them. That checker
is also the right thing to write in an interview — it is what convinces the
interviewer the construction is right without a proof on the whiteboard.
""",
        ),
    ],
}


@cache
def _beautiful(n: int) -> tuple[int, ...]:
    if n == 1:
        return (1,)
    odds = _beautiful((n + 1) // 2)  # ceil(n/2) odd values in 1..n
    evens = _beautiful(n // 2)  # floor(n/2) even values in 1..n
    return tuple(2 * x - 1 for x in odds) + tuple(2 * x for x in evens)


def beautiful_array(n: int) -> list[int]:
    return list(_beautiful(n))


CASES = [
    ((1,), [1]),
    ((2,), [1, 2]),
    ((3,), [1, 3, 2]),
    ((4,), [1, 3, 2, 4]),
    ((5,), [1, 5, 3, 2, 4]),
    ((6,), [1, 5, 3, 2, 6, 4]),
]


def solve(n: int) -> list[int]:
    return beautiful_array(n)


def _is_beautiful(array: list[int]) -> bool:
    position = {value: index for index, value in enumerate(array)}
    for i in range(len(array)):
        for j in range(i + 2, len(array)):
            total = array[i] + array[j]
            if total % 2:
                continue  # an odd sum is never 2·A[k]
            k = position.get(total // 2)
            if k is not None and i < k < j:
                return False
    return True


def check() -> None:
    for args, expected in CASES:
        assert solve(*args) == expected, f"beautiful_array{args} != {expected}"

    for n in [*range(1, 40), 63, 64, 65, 100, 257]:
        array = beautiful_array(n)
        assert sorted(array) == list(range(1, n + 1)), f"n={n} is not a permutation"
        assert _is_beautiful(array), f"n={n} has a straddling average"

    assert sorted(beautiful_array(1000)) == list(range(1, 1001))
