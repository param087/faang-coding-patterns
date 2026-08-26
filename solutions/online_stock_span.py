"""Online Stock Span — LeetCode 901."""

from __future__ import annotations

META = {
    "pattern": "monotonic-stack",
    "insight": "A price that swallows an earlier one inherits its span, so a swallowed day is never looked at again.",
    "time": "O(1) amortised per call, O(n) over n calls",
    "space": "O(n) worst case, one entry per strictly decreasing price",
    "sections": [
        (
            "What it asks",
            """
Stream prices one at a time. After each, return the **span**: how many
consecutive days ending today had a price less than or equal to today's.
The span always counts today, so the minimum answer is 1.

Ask what the interviewer means at ties — LeetCode's definition is
*less than or equal*, which makes the pop test `<=`. And ask whether the whole
history has to be kept: it does not, and noticing that is half the answer.
""",
        ),
        (
            "The insight",
            """
Keep a stack of `(price, span)` pairs with prices strictly decreasing from
bottom to top. When today's price is at least the top's, that day is finished
forever — today already covers everything it covered — so pop it and **add its
span to today's**.

```python
span = 1
while stack and stack[-1][0] <= price:
    span += stack.pop()[1]
```

The absorbed span is the whole point. Without it you would have to re-walk the
swallowed days; with it, a day that leaves the stack never costs anything
again. Each price is pushed once and popped once, so n calls cost O(n) total —
**amortised O(1)**, not O(1), and say the word "amortised" out loud, because a
single call can pop the entire stack.

The naive alternative stores every price and walks backwards per query: O(n)
per call, O(n²) overall. At 10⁴ calls that is 10⁸ comparisons for something
that should be a few thousand.
""",
        ),
        (
            "Edge cases",
            """
- **Ties.** `<=`, not `<`. On `[85, 85]` the second call must return 2. A strict
  test returns 1 and the bug survives every strictly-increasing test you write.
- **Monotone increasing input** — `[10, 20, 30]` gives spans `1, 2, 3` and the
  stack holds a single entry, because each price absorbs the last.
- **Monotone decreasing input** — every span is 1 and the stack grows to n. That
  is the space worst case; there is no way around it, since any of those days
  could still be swallowed later.
- **Nothing is ever peeked without popping**, so no "look at the previous price"
  variable is needed. Adding one is the usual way this gets over-engineered.
""",
        ),
    ],
    "symbol": "StockSpanner",
}


class StockSpanner:
    def __init__(self) -> None:
        # (price, span), prices strictly decreasing bottom -> top.
        self._stack: list[tuple[int, int]] = []

    def next(self, price: int) -> int:
        span = 1
        # `<=`: today's span includes days that merely tied.
        while self._stack and self._stack[-1][0] <= price:
            span += self._stack.pop()[1]  # inherit the swallowed day's reach
        self._stack.append((price, span))
        return span


def check() -> None:
    # The canonical sequence: 75 swallows three days, 85 swallows five.
    spanner = StockSpanner()
    prices = [100, 80, 60, 70, 60, 75, 85]
    assert [spanner.next(p) for p in prices] == [1, 1, 1, 2, 1, 4, 6]

    # Ties count — `<` instead of `<=` returns 1 here and passes everything else.
    spanner = StockSpanner()
    assert [spanner.next(p) for p in [85, 85, 85]] == [1, 2, 3]

    # Strictly increasing: each price absorbs the whole stack, which stays at one entry.
    spanner = StockSpanner()
    assert [spanner.next(p) for p in [10, 20, 30, 40]] == [1, 2, 3, 4]
    assert len(spanner._stack) == 1

    # Strictly decreasing: nothing is ever absorbed, the stack is the space worst case.
    spanner = StockSpanner()
    assert [spanner.next(p) for p in [40, 30, 20, 10]] == [1, 1, 1, 1]
    assert len(spanner._stack) == 4

    # A single call, and negatives (a spread, say, rather than a price).
    assert StockSpanner().next(7) == 1
    spanner = StockSpanner()
    assert [spanner.next(p) for p in [-5, -10, -7, -3]] == [1, 1, 2, 4]

    # 10_000 calls stay linear: a quadratic version would do ~5 * 10^7 comparisons.
    spanner = StockSpanner()
    assert [spanner.next(-p) for p in range(10_000)] == [1] * 10_000
    spanner = StockSpanner()
    spans = [spanner.next(p) for p in range(10_000)]
    assert spans[-1] == 10_000
    assert len(spanner._stack) == 1
