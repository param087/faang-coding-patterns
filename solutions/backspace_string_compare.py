"""Backspace String Compare — LeetCode 844."""

from __future__ import annotations

META = {
    "pattern": "stack",
    "insight": "The O(1)-space answer walks both strings backwards, because only from the right does a backspace collapse into a pending-deletion count.",
    "time": "O(n + m)",
    "space": "O(1) for the two-pointer version, O(n + m) for the stack",
    "sections": [
        (
            "What it asks",
            """
Two strings in which `#` means backspace. Do they type out the same?

The clarifying question that matters: **what does `#` do on an empty string?**
It is a no-op, not an error — `"#####"` types out as `""`. Confirm it, because
a candidate who treats it as invalid input writes a guard that changes nothing
and wastes a minute.

LeetCode states the follow-up explicitly: O(n) time and **O(1) space**. Assume
you will be asked for it whether or not it is mentioned.
""",
        ),
        (
            "The insight",
            """
The stack version is thirty seconds of work: push a character, pop on `#` if
the stack is non-empty, compare the two results. O(n) time, O(n) space, done.
Write it, say it is correct, then go after the real question.

Why O(1) forces you **backwards**: reading left to right, you cannot know how
many of the characters you have already emitted will later be deleted, so you
must buffer them — that buffer is the O(n). Reading right to left, a `#` is a
promise about characters you have **not read yet**, so it collapses to a single
counter of pending deletions. One integer per string, no buffer.

So each pointer skips: while there is a `#`, increment `pending`; while
`pending > 0`, consume a real character and decrement. What it lands on is the
next surviving character, and the two survivors are compared in lockstep.
""",
        ),
        (
            "The exhaustion check that decides it",
            """
The loop runs while **either** pointer is still in range, not while both. After
skipping, exactly three things can be true:

- both landed on a character → compare them;
- both ran out → the strings ended together, keep going and finish `True`;
- **one ran out and the other did not** → `False`.

That third case is the whole bug surface. `"a"` versus `""` and `"ab#"` versus
`"a"` both hinge on it, and a loop written as `while i >= 0 and j >= 0` skips
the check entirely and returns `True` for the first pair.

Note the skip helper returns `-1` for "nothing survives", so the caller uses a
plain sign test rather than a sentinel character.
""",
        ),
    ],
}


def _previous(text: str, index: int) -> int:
    """Index of the next surviving character at or before `index`, else -1."""
    pending = 0
    while index >= 0:
        if text[index] == "#":
            pending += 1  # a promise about characters not yet read
        elif pending:
            pending -= 1  # this one is deleted by an earlier '#'
        else:
            return index
        index -= 1
    return -1


def backspace_compare(s: str, t: str) -> bool:
    i, j = len(s) - 1, len(t) - 1

    while i >= 0 or j >= 0:  # *or*: one string may still have survivors
        i = _previous(s, i)
        j = _previous(t, j)
        if i >= 0 and j >= 0 and s[i] != t[j]:
            return False
        if (i >= 0) != (j >= 0):
            return False  # one ran out, the other did not
        i -= 1
        j -= 1

    return True


def backspace_compare_stack(s: str, t: str) -> bool:
    """The O(n)-space version worth writing first."""

    def typed(text: str) -> list[str]:
        out: list[str] = []
        for char in text:
            if char == "#":
                if out:
                    out.pop()  # '#' on empty is a no-op, not an error
            else:
                out.append(char)
        return out

    return typed(s) == typed(t)


CASES = [
    (("ab#c", "ad#c"), True),
    (("ab##", "c#d#"), True),  # both type out empty
    (("a#c", "b"), False),
    (("bxj##tw", "bxo#j##tw"), True),
    (("bxj##tw", "bxj###tw"), False),  # one extra backspace changes everything
    (("a", ""), False),  # the exhaustion check
    (("#####", ""), True),  # backspace on empty is a no-op
    (("", ""), True),
]


def solve(s: str, t: str) -> bool:
    return backspace_compare(s, t)


def check() -> None:
    for (s, t), expected in CASES:
        assert backspace_compare(s, t) is expected, (s, t)
        assert backspace_compare_stack(s, t) is expected, (s, t)
