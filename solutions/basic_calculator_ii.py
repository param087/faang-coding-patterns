"""Basic Calculator II — LeetCode 227."""

from __future__ import annotations

META = {
    "pattern": "string-manipulation",
    "insight": "Push additive terms onto a stack, but resolve * and / immediately — then the answer is just the sum.",
    "time": "O(n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Evaluate a string expression with `+ - * /` and non-negative integers.
Integer division truncates toward zero.

Ask: are there parentheses (**no** — that is Basic Calculator I/III and a
different solution); negative numbers in the input; is the expression
guaranteed valid; truncate or floor.
""",
        ),
        (
            "The two-pass idea",
            """
Resolve all `*` and `/` first, then sum what remains. Correct, and worth
mentioning — because the stack version is exactly that idea made single-pass.
""",
        ),
        (
            "The insight",
            """
Push every additive term onto a stack. When the **pending** operator was `*`
or `/`, pop the top and combine immediately.

Everything left on the stack is additive by construction, so the answer is
`sum(stack)`. No precedence table, no recursive descent.
""",
        ),
        (
            "Act on the pending operator",
            """
The subtle bit: at each boundary you apply the operator you saw **last time**,
not the one you just read. The current character only tells you what to do
*next*.

`i == len(expression) - 1` is what flushes the final term — without it the
last number is silently dropped.
""",
        ),
        (
            "Truncation, not flooring",
            """
`int(a / b)` truncates toward zero. Python's `//` **floors**.

`-7 // 2` is `-4`; the problem wants `-3`. This is the single most common
wrong answer on this problem, and the same trap appears in Evaluate Reverse
Polish Notation and Divide Two Integers.
""",
        ),
        (
            "Dry run",
            """
`"3+2*2"` → 7. Push 3. Then 2 arrives with pending `+` → push 2. At the end
the pending operator is `*` → pop 2, push 4. Stack `[3, 4]`, sum **7**.

Then run `"14-3/2"` → 13, which exercises multi-digit parsing *and*
truncation in one string. Those are the two bugs this problem has.
""",
        ),
        (
            "Follow-ups",
            """
- **Add parentheses** (Basic Calculator I). Either recurse on `(`, or push the
  running result and sign onto a stack. The two-stack version is worth
  knowing.
- **Basic Calculator III** — both parentheses and precedence, which is this
  algorithm called recursively.
- **Unary minus** (`"-2+3"`, `"3*-2"`) — ask whether it is in scope; it is a
  meaningfully different parse.
""",
        ),
    ],
}


def calculate(expression: str) -> int:
    stack: list[int] = []
    number = 0
    operator = "+"  # the *pending* operator, acted on at the next boundary

    for i, char in enumerate(expression):
        if char.isdigit():
            number = number * 10 + int(char)  # multi-digit

        if (not char.isdigit() and char != " ") or i == len(expression) - 1:
            if operator == "+":
                stack.append(number)
            elif operator == "-":
                stack.append(-number)
            elif operator == "*":
                stack.append(stack.pop() * number)
            else:
                # int(a / b) truncates toward zero; // would floor.
                stack.append(int(stack.pop() / number))
            operator = char
            number = 0

    return sum(stack)  # everything left is additive by construction


CASES = [
    (("3+2*2",), 7),
    ((" 3/2 ",), 1),
    ((" 3+5 / 2 ",), 5),
    (("14-3/2",), 13),
    (("1",), 1),
    (("0-2147483647",), -2147483647),
    (("100/3",), 33),
]


def solve(expression: str) -> int:
    return calculate(expression)
