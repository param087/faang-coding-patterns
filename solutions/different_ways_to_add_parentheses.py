"""Different Ways to Add Parentheses — LeetCode 241."""

from __future__ import annotations

import operator
from functools import cache

META = {
    "pattern": "divide-and-conquer",
    "insight": "Every parenthesisation is fixed by which operator runs last; make that one the root and the two sides become independent subproblems.",
    "time": "O(Cₙ · n) for n operators, where Cₙ is the nth Catalan number",
    "space": "O(Cₙ · n)",
    "sections": [
        (
            "What it asks",
            """
Given an arithmetic expression of non-negative integers and `+ - *`, return
**every** value obtainable by parenthesising it differently. Any order,
duplicates kept.

Duplicates kept is the detail to confirm: `2*3-4*5` yields `-10` twice, from
two genuinely different trees, and de-duplicating fails the judge.
""",
        ),
        (
            "The insight",
            """
Stop thinking about brackets and think about the **expression tree**. A
parenthesisation is exactly a choice of which operator sits at the root — the
one evaluated last. Fix that operator at position `i`, and:

- everything left of `i` is an independent subexpression,
- everything right of `i` is another,
- and the results combine as a cross product.

```
for each operator at i:
    for a in ways(expr[:i]):
        for b in ways(expr[i+1:]):
            emit(a OP b)
```

The base case is a substring with no operator: return the number itself. There
is no separate bracket-matching step and no stack — the recursion *is* the
bracketing. This is the cleanest instance of "split, solve, combine" on the
list, and the reason it shows up as a warm-up before real parser questions.
""",
        ),
        (
            "Edge cases and cost",
            """
- **Multi-digit numbers.** `10*10-5` has three characters that are not
  operators in a row. Parse the base case with `int(expr)` on the whole
  substring, never character by character. Walking one character at a time
  gives `1`, `0`, `1`, `0` and a wrong answer that still looks plausible.
- **No operator at all.** `"11"` must return `[11]`, not `[]`. Falling out of
  the loop with an empty list is the usual off-by-one here.
- **Cost.** With `n` operators the number of results is the Catalan number
  `Cₙ ≈ 4ⁿ / n^1.5` — `n = 10` is 16,796 values, `n = 19` (the constraint
  ceiling) is about 1.8 × 10⁹, which is why the constraint caps the expression
  at 20 characters. The output itself is exponential, so no algorithm is
  polynomial; the honest claim is "linear in the size of the output".
- **Memoise on the substring** (`@cache` over the slice). It does not change
  the asymptotics — the answer is still exponentially large — but `2*3-4*5*6`
  asks for `ways("4*5*6")` from several places and the cache collapses those.
  Cache the results as a **tuple**, so a caller cannot mutate a cached list.
- **Determinism for testing.** LeetCode accepts any order; `solve` sorts so
  the cases below can compare exactly.
""",
        ),
    ],
}

OPS = {"+": operator.add, "-": operator.sub, "*": operator.mul}


def diff_ways_to_compute(expression: str) -> list[int]:
    @cache
    def ways(expr: str) -> tuple[int, ...]:
        results: list[int] = []
        for i, char in enumerate(expr):
            if char in OPS:
                # `char` is applied last, so both sides are independent.
                results.extend(
                    OPS[char](a, b) for a in ways(expr[:i]) for b in ways(expr[i + 1 :])
                )
        # No operator seen: the whole slice is one (possibly multi-digit) number.
        return tuple(results) if results else (int(expr),)

    return list(ways(expression))


CASES = [
    (("2-1-1",), [0, 2]),
    (("2*3-4*5",), [-34, -14, -10, -10, 10]),
    (("11",), [11]),
    (("0",), [0]),
    # Multi-digit on both sides: (10*10)-5 = 95, 10*(10-5) = 50.
    (("10*10-5",), [50, 95]),
    (("1+1",), [2]),
    (("2*3*4",), [24, 24]),
]


def solve(expression: str) -> list[int]:
    return sorted(diff_ways_to_compute(expression))
