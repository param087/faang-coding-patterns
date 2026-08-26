"""Basic Calculator III — LeetCode 772."""

from __future__ import annotations

META = {
    "pattern": "string-manipulation",
    "insight": "Basic Calculator II's stack, called recursively at every '(' — each call returns both a value and where it stopped.",
    "time": "O(n)",
    "space": "O(n) — stack depth is the nesting depth, plus one list per frame",
    "sections": [
        (
            "What it asks",
            """
This one is premium, so the statement is not public — in my own words: evaluate
a string expression built from non-negative integers, `+ - * /`, parentheses
and spaces. Division truncates toward zero. It is Basic Calculator I
(parentheses) and II (precedence) fused into one problem.

Ask before coding: **unary minus** (`"-2+3"`, `"3*-2"`) — the first falls out
for free, the second needs an extra flag; is the expression guaranteed valid
(assume yes, and say so, or you will waste ten minutes on error handling);
truncate or floor.
""",
        ),
        (
            "The insight",
            """
Do not write a shunting-yard parser. Basic Calculator II already handles
precedence with one stack: push additive terms, resolve `*` and `/` against the
top immediately, answer is `sum(stack)`. Parentheses add exactly one thing —
**recursion**.

The detail that makes it work is the return type. `evaluate(i)` returns
`(value, index_of_matching_paren)`. Without the second element the caller has no
idea where the sub-expression ended and you end up re-scanning to find the
matching `)`, which is where the O(n²) versions come from.

A `(` is then treated as if it were a number: recurse, take the value into
`number`, and carry on with the same loop. The pending operator is still applied
one boundary late, exactly as in Basic Calculator II.
""",
        ),
        (
            "Traps",
            """
- **`int(a / b)` truncates, `//` floors.** `-7 // 2` is `-4`; this problem wants
  `-3`. Test it with something like `"(0-7)/2"` before you claim you are done.
- **Return on `)`, do not fall through.** The pending operator has to be flushed
  *before* returning, or the last operand inside the group is dropped.
- **Leading unary minus works, unary after an operator does not.** `"-2+3"`
  parses because the pending operator starts as `+` with `number = 0`, so the
  `-` just flushes a harmless `0`. But `"3*-2"` would flush `3 * 0`. If the
  interviewer wants that case, track "am I expecting an operand" and fold the
  sign into the next number.
- Nesting depth is the recursion depth. On an adversarial `"((((...1...))))"`
  with 10⁴ characters you will hit Python's 1000-frame limit — mention the
  explicit-stack rewrite rather than pretending it cannot happen.
""",
        ),
    ],
}


def _apply(stack: list[int], operator: str, operand: int) -> None:
    """Fold `operand` in under the pending operator; * and / resolve now."""
    if operator == "+":
        stack.append(operand)
    elif operator == "-":
        stack.append(-operand)
    elif operator == "*":
        stack.append(stack.pop() * operand)
    else:
        stack.append(int(stack.pop() / operand))  # truncate toward zero, not floor


def calculate(expression: str) -> int:
    def evaluate(i: int) -> tuple[int, int]:
        """Evaluate from `i` to the matching ')' or the end; return (value, i)."""
        stack: list[int] = []
        number = 0
        operator = "+"  # the *pending* operator, acted on at the next boundary

        while i < len(expression):
            char = expression[i]
            if char.isdigit():
                number = number * 10 + int(char)
            elif char == "(":
                number, i = evaluate(i + 1)  # i lands on the matching ')'
            elif char == ")":
                _apply(stack, operator, number)  # flush before returning
                return sum(stack), i
            elif char != " ":
                _apply(stack, operator, number)
                operator, number = char, 0
            i += 1

        _apply(stack, operator, number)
        return sum(stack), i

    return evaluate(0)[0]


CASES = [
    (("1+1",), 2),
    (("6-4/2",), 4),
    (("2*(5+5*2)/3+(6/2+8)",), 21),
    (("(2+6*3+5-(3*14/7+2)*5)+3",), -12),
    (("(0-7)/2",), -3),
    (("1-(-2)",), 3),
    (("(((10)))",), 10),
    (("0",), 0),
]


def solve(expression: str) -> int:
    return calculate(expression)
