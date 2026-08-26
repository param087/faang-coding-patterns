"""Valid Parentheses — LeetCode 20."""

from __future__ import annotations

META = {
    "pattern": "stack",
    "insight": "A closer must match the most recent unclosed opener, and 'most recent' is the only thing a stack knows how to answer.",
    "time": "O(n)",
    "space": "O(n) — a string of all openers stacks up entirely",
    "sections": [
        (
            "What it asks",
            """
A string of `()[]{}` is valid when every bracket is closed by the same type,
in the right order.

Worth asking: **can the string contain anything other than brackets?** On
LeetCode it cannot, which is why the `else` branch below can blindly push. In
a real tokeniser you would skip non-brackets, and that one word changes the
code. Also confirm the empty string is valid (it is).
""",
        ),
        (
            "The insight",
            """
The tempting first answer is three counters, one per bracket type. It accepts
`([)]` — every counter balances, the *order* does not. Counting throws away
exactly the information the problem is testing.

What you actually need is "which opener is still waiting, most recently first",
and that is a stack by definition. Map each closer to its opener so the whole
loop is one dict lookup:

- opener → push it;
- closer → the top must be its partner, so pop and compare.

Two distinct ways to fail on a closer: the stack is **empty** (a closer with no
opener) and the top is the **wrong type**. `not stack or stack.pop() != PAIRS[char]`
covers both, and short-circuiting means `pop()` never runs on an empty list.

Anything left on the stack at the end is an unclosed opener, so the return is
`not stack`, not `True`.
""",
        ),
        (
            "Edge cases",
            """
- `""` → `True`. Say it out loud; some candidates return `False`.
- `"]"` → the empty-stack guard. Without it this is an `IndexError`, which is
  the single most common way this gets failed.
- `"((("` → the final `not stack` check. Returning `True` at the end of the
  loop passes every LeetCode sample and fails this.
- `"([)]"` → the counting trap.
- Odd length can early-return `False`, and `len(s) & 1` is a cheap thing to
  mention, though it changes nothing asymptotically.
""",
        ),
    ],
}

PAIRS = {")": "(", "]": "[", "}": "{"}


def is_valid(s: str) -> bool:
    stack: list[str] = []

    for char in s:
        if char in PAIRS:
            # Empty stack or wrong opener on top — both are failures.
            if not stack or stack.pop() != PAIRS[char]:
                return False
        else:
            stack.append(char)

    return not stack  # leftovers are unclosed openers


CASES = [
    (("()",), True),
    (("()[]{}",), True),
    (("{[]}",), True),
    (("(]",), False),
    (("([)]",), False),  # every counter balances; the order does not
    (("]",), False),  # closer with an empty stack
    (("(((",), False),  # leftovers on the stack
    (("",), True),
]


def solve(s: str) -> bool:
    return is_valid(s)
