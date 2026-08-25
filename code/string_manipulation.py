"""String parsing and manipulation.

These are small parsers wearing a string problem's clothes. Once you see the
grammar — expression, term, factor — the code writes itself, and the stack is
there to hold the context you suspend when you descend into a bracket.
"""

from __future__ import annotations


def calculate(expression: str) -> int:
    """Evaluate `+ - * /` with integer division truncating toward zero.

    The trick that removes all the precedence bookkeeping: push every term
    onto a stack, but when the *previous* operator was `*` or `/`, pop and
    combine immediately. The final answer is the sum of the stack, because
    everything left is additive by construction.
    """
    stack: list[int] = []
    number = 0
    operator = "+"

    for i, char in enumerate(expression):
        if char.isdigit():
            number = number * 10 + int(char)

        # Act on the *pending* operator at a boundary, not when we read it.
        if (not char.isdigit() and char != " ") or i == len(expression) - 1:
            if operator == "+":
                stack.append(number)
            elif operator == "-":
                stack.append(-number)
            elif operator == "*":
                stack.append(stack.pop() * number)
            else:
                # Python floors; interviews want truncation toward zero.
                stack.append(int(stack.pop() / number))
            operator = char
            number = 0

    return sum(stack)


def decode_string(encoded: str) -> str:
    """Expand `3[a2[c]]` into `accaccacc`.

    The general shape for nested structures: on `[`, push the context you are
    suspending; on `]`, pop it and splice the finished piece back in. Two
    stacks — one for counts, one for the partial string — keep it readable.
    """
    counts: list[int] = []
    parts: list[str] = []
    current = ""
    number = 0

    for char in encoded:
        if char.isdigit():
            number = number * 10 + int(char)
        elif char == "[":
            counts.append(number)
            parts.append(current)
            number = 0
            current = ""
        elif char == "]":
            current = parts.pop() + current * counts.pop()
        else:
            current += char

    return current


def full_justify(words: list[str], width: int) -> list[str]:
    """Greedy line packing with spaces distributed left-heavy.

    Two rules people miss: the last line is *left*-justified with a single
    space between words, and a line holding one word is also left-justified
    because there are no gaps to distribute into.
    """
    lines: list[str] = []
    line: list[str] = []
    length = 0

    for word in words:
        # +len(line) accounts for one mandatory space after each existing word.
        if length + len(word) + len(line) > width:
            gaps = len(line) - 1
            if gaps == 0:
                lines.append(line[0].ljust(width))
            else:
                space, extra = divmod(width - length, gaps)
                built = ""
                for i, w in enumerate(line[:-1]):
                    built += w + " " * (space + (1 if i < extra else 0))
                lines.append(built + line[-1])
            line, length = [], 0
        line.append(word)
        length += len(word)

    if line:
        lines.append(" ".join(line).ljust(width))
    return lines


CASES = [
    (("3+2*2",), 7),
    ((" 3/2 ",), 1),
    ((" 3+5 / 2 ",), 5),
    (("1",), 1),
    (("14-3/2",), 13),
]


def solve(expression: str) -> int:
    return calculate(expression)


def check() -> None:
    for args, expected in CASES:
        assert calculate(*args) == expected

    assert decode_string("3[a]2[bc]") == "aaabcbc"
    assert decode_string("3[a2[c]]") == "accaccacc"
    assert decode_string("2[abc]3[cd]ef") == "abcabccdcdcdef"
    assert decode_string("abc") == "abc"

    assert full_justify(["This", "is", "an", "example", "of", "text", "justification."], 16) == [
        "This    is    an",
        "example  of text",
        "justification.  ",
    ]
    assert full_justify(["What", "must", "be"], 16) == ["What must be    "]
