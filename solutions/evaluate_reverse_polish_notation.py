"""Evaluate Reverse Polish Notation — LeetCode 150."""

from __future__ import annotations

META = {
    "pattern": "stack",
    "insight": "RPN exists so you never need precedence — operands accumulate on a stack and an operator consumes the two most recent.",
    "time": "O(n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Evaluate an expression in reverse Polish (postfix) notation given as a list of
tokens.

Ask: is the expression guaranteed valid (yes); is division by zero possible
(no); **truncate or floor** the integer division (truncate toward zero); can
operands be negative (yes).
""",
        ),
        (
            "The insight",
            """
Postfix notation exists precisely so that **precedence is unnecessary** —
the order of the tokens already encodes it.

Operands accumulate on a stack; an operator consumes the two most recent and
pushes the result. Whatever is left at the end is the answer.
""",
        ),
        (
            "Operand order",
            """
The **first** value you pop is the *right*-hand operand.

`left - right`, not `right - left`. Addition and multiplication hide this
mistake completely; subtraction and division expose it immediately.

Pop into two clearly named variables rather than inlining — it costs one line
and removes the whole class of error.
""",
        ),
        (
            "Truncation, not flooring",
            """
`int(a / b)` truncates toward zero. Python's `//` **floors**.

`-7 // 2` is `-4`; the problem wants `-3`.

This is the same trap as in Basic Calculator II and Divide Two Integers, and
it is worth internalising once: whenever a problem says "truncate toward
zero", `//` is wrong in Python.
""",
        ),
        (
            "Dry run",
            """
`["4","13","5","/","+"]`

Push 4, 13, 5. Then `/` pops 5 (right) and 13 (left) → `13/5` = **2**
truncated. Then `+` pops 2 and 4 → **6**.

Then run `["-7","2","/"]` and confirm you get **−3**, not −4. That single case
is the difference between passing and failing.
""",
        ),
        (
            "Follow-ups",
            """
- **Convert infix to postfix** — the shunting-yard algorithm.
- **Evaluate infix directly** — that is
  [Basic Calculator](../../patterns/string-manipulation/), which needs a
  precedence strategy because the tokens do not encode it.
- **Add more operators** (`^`, unary minus) — the stack structure is
  unchanged; only the arity and associativity differ.
""",
        ),
    ],
}

OPERATORS = {"+", "-", "*", "/"}


def eval_rpn(tokens: list[str]) -> int:
    stack: list[int] = []

    for token in tokens:
        if token not in OPERATORS:
            stack.append(int(token))
            continue

        # The FIRST pop is the right-hand operand.
        right = stack.pop()
        left = stack.pop()

        if token == "+":
            stack.append(left + right)
        elif token == "-":
            stack.append(left - right)
        elif token == "*":
            stack.append(left * right)
        else:
            # int(a / b) truncates toward zero; // would floor.
            stack.append(int(left / right))

    return stack[-1]


CASES = [
    ((["2", "1", "+", "3", "*"],), 9),
    ((["4", "13", "5", "/", "+"],), 6),
    ((["7", "2", "/"],), 3),
    ((["-7", "2", "/"],), -3),  # truncation, not flooring
    ((["5", "3", "-"],), 2),  # operand order
    ((["3", "5", "-"],), -2),
    ((["42"],), 42),
    (
        (
            [
                "10", "6", "9", "3", "+", "-11", "*", "/", "*", "17", "+", "5", "+",
            ],
        ),
        22,
    ),
]


def solve(tokens: list[str]) -> int:
    return eval_rpn(tokens)
