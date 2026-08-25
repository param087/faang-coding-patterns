"""Stack fundamentals.

A stack is what you reach for when the meaning of what you are reading now
depends on something you read earlier and have not finished with — brackets,
nested structures, and any "undo the last thing" rule.
"""

from __future__ import annotations


def is_valid(s: str) -> bool:
    """Balanced brackets across three types.

    Mapping closers to openers means one dict lookup instead of a chain of
    comparisons. Both failure modes matter: a closer with a mismatched (or
    absent) opener, and leftover openers at the end.
    """
    pairs = {")": "(", "]": "[", "}": "{"}
    stack: list[str] = []

    for char in s:
        if char in pairs:
            if not stack or stack.pop() != pairs[char]:
                return False
        else:
            stack.append(char)

    return not stack  # anything left is an unclosed opener


class MinStack:
    """Push, pop, top and get_min, all O(1).

    The trick is storing the running minimum *alongside* each value, so the
    minimum is restored for free on pop. Trying to keep a single `min`
    variable fails: once you pop the minimum you have no way to recover the
    previous one without a scan.
    """

    def __init__(self) -> None:
        self._stack: list[tuple[int, int]] = []  # (value, min at or below)

    def push(self, value: int) -> None:
        smallest = value if not self._stack else min(value, self._stack[-1][1])
        self._stack.append((value, smallest))

    def pop(self) -> int:
        return self._stack.pop()[0]

    def top(self) -> int:
        return self._stack[-1][0]

    def get_min(self) -> int:
        return self._stack[-1][1]


def eval_rpn(tokens: list[str]) -> int:
    """Evaluate reverse Polish notation.

    Operand order is the thing to get right: the *first* pop is the
    right-hand operand. Division truncates toward zero, which `int(a / b)`
    does and `a // b` does not.
    """
    stack: list[int] = []

    for token in tokens:
        if token not in {"+", "-", "*", "/"}:
            stack.append(int(token))
            continue
        right = stack.pop()
        left = stack.pop()
        if token == "+":
            stack.append(left + right)
        elif token == "-":
            stack.append(left - right)
        elif token == "*":
            stack.append(left * right)
        else:
            stack.append(int(left / right))

    return stack[-1]


def asteroid_collision(asteroids: list[int]) -> list[int]:
    """Simulate collisions: positive moves right, negative moves left.

    Collisions only happen when a right-mover meets a left-mover, so the
    condition is `stack[-1] > 0 and asteroid < 0`. The `else` on the while
    loop is doing real work — it runs only when the incoming asteroid
    survived every collision, which is exactly when it should be pushed.
    """
    stack: list[int] = []

    for asteroid in asteroids:
        while stack and asteroid < 0 < stack[-1]:
            if stack[-1] < -asteroid:
                stack.pop()  # top explodes, keep checking further left
                continue
            if stack[-1] == -asteroid:
                stack.pop()  # both explode
            break  # incoming explodes (or both did)
        else:
            stack.append(asteroid)

    return stack


CASES = [
    (("()",), True),
    (("()[]{}",), True),
    (("(]",), False),
    (("([)]",), False),
    (("{[]}",), True),
    ((")",), False),
    (("(",), False),
    (("",), True),
]


def solve(s: str) -> bool:
    return is_valid(s)


def check() -> None:
    for args, expected in CASES:
        assert is_valid(*args) == expected

    stack = MinStack()
    for value in (-2, 0, -3):
        stack.push(value)
    assert stack.get_min() == -3
    assert stack.pop() == -3
    assert stack.top() == 0
    assert stack.get_min() == -2

    assert eval_rpn(["2", "1", "+", "3", "*"]) == 9
    assert eval_rpn(["4", "13", "5", "/", "+"]) == 6
    assert eval_rpn(["7", "2", "/"]) == 3
    assert eval_rpn(["-7", "2", "/"]) == -3  # truncation, not flooring

    assert asteroid_collision([5, 10, -5]) == [5, 10]
    assert asteroid_collision([8, -8]) == []
    assert asteroid_collision([10, 2, -5]) == [10]
    assert asteroid_collision([-2, -1, 1, 2]) == [-2, -1, 1, 2]
