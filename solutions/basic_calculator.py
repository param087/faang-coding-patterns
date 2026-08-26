"""Basic Calculator — LeetCode 224."""

from __future__ import annotations

META = {
    "pattern": "string-manipulation",
    "insight": "With only + and -, a '(' never needs a sub-parser: push the running result and the sign in front of it, and restore them at the ')'.",
    "time": "O(n)",
    "space": "O(d) for nesting depth d",
    "sections": [
        (
            "What it asks",
            """
Evaluate an expression string containing non-negative integers, `+`, `-`,
parentheses and spaces. No `*` or `/` — that is Basic Calculator II (no
brackets) and III (both).

The question that decides your code: **is unary minus in scope?** It is —
LeetCode explicitly allows `"-2 + 1"` and `"-(3 + 4)"`, and every solution that
assumes a number precedes each operator dies on the first one. Also worth
asking: is the expression guaranteed well formed (yes), can it exceed 32-bit
range (the answer fits, intermediates may not in other languages), and how deep
does nesting go (deep enough that recursion needs a word about stack depth).
""",
        ),
        (
            "The insight",
            """
Because there is no precedence to resolve, the expression is just a **signed
sum**: every number carries a `+1` or `-1` that is fully determined by the
operators outside it. `1 - (2 - (3 - 4))` is `1 - 2 + 3 - 4`.

So keep three registers — `result` (the sum so far), `sign` (what applies to
the number being read), `number` (the digits accumulating) — and let the stack
hold only what a `(` interrupts:

```python
stack.append(result)   # everything summed before the bracket
stack.append(sign)     # the sign sitting in front of it
result, sign = 0, 1    # start the sub-expression clean
```

At the `)`, close out the sub-expression and fold it back:

```python
result = result * stack.pop() + stack.pop()   # sign first, then the prefix
```

Pop order matters and is the opposite of push order. Swapping the two lines
multiplies the prefix by the sub-result, which produces plausible-looking
wrong answers on nested input.

That is the whole algorithm — no recursion, no operator stack, no precedence
table. The recursive-descent version is equally valid and reads better, but it
must return the cursor position alongside the value, and it is that threading
that people get wrong under time pressure.
""",
        ),
        (
            "Unary minus, and the flush at the end",
            """
The `+`/`-` branch does `result += sign * number` **before** reading the new
sign. When `-` is the very first character, `number` is still 0, so it adds
nothing and simply sets `sign = -1`. Unary minus therefore needs no special
case at all — provided you fold the pending number *first*. `"-(2 + 3)"` works
the same way: the `-` sets the sign, the `(` pushes it, and the `)` multiplies
the sub-result by it.

Two more that decide the submission:

- **The final flush.** The loop only folds `number` into `result` when it hits
  an operator or a `)`. An expression ending in a digit — which is most of them
  — needs `return result + sign * number`. Forgetting it drops the last term,
  and `"1 + 1"` returns 1.
- **Reset `number` at `)`** as well as at operators, and reset `sign` to `+1`
  there too. Leaving a stale `sign` after a bracket flips the term that follows.

Spaces need no branch: they match none of the four cases and fall through.

Follow-up to have ready: adding `*` and `/` means precedence, and the cleanest
answer is the Basic Calculator II stack (push additive terms, resolve `*` and
`/` immediately) called **recursively** at each `(`. That is Basic Calculator
III, and the interviewer asks for it roughly half the time.
""",
        ),
    ],
}


def calculate(expression: str) -> int:
    stack: list[int] = []  # alternating (result, sign) frames, one per open bracket
    result = 0
    number = 0
    sign = 1

    for char in expression:
        if char.isdigit():
            number = number * 10 + int(char)
        elif char in "+-":
            result += sign * number  # fold first: this is what makes unary minus free
            number = 0
            sign = 1 if char == "+" else -1
        elif char == "(":
            stack.append(result)
            stack.append(sign)
            result, sign = 0, 1
        elif char == ")":
            result += sign * number
            number = 0
            result = result * stack.pop() + stack.pop()  # sign, then prefix
            sign = 1
        # spaces fall through untouched

    return result + sign * number  # the flush an expression ending in a digit needs


CASES = [
    (("1 + 1",), 2),
    ((" 2-1 + 2 ",), 3),
    (("(1+(4+5+2)-3)+(6+8)",), 23),
    (("2-(5-6)",), 3),
    (("-2+ 1",), -1),
    (("-(2+3)",), -5),
    (("1-(-2)",), 3),
    (("1-(2-(3-4))",), -2),
    (("2147483647",), 2147483647),
]


def solve(expression: str) -> int:
    return calculate(expression)
