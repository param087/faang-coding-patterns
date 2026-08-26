"""Baseball Game — LeetCode 682."""

from __future__ import annotations

META = {
    "pattern": "stack",
    "insight": "Every operation touches only the tail of the record, so the record is a stack and the problem is a four-way branch.",
    "time": "O(n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Replay a list of string operations against a record of scores and return the
total:

- an integer → append it;
- `"+"` → append the sum of the previous two scores;
- `"D"` → append double the previous score;
- `"C"` → remove the previous score.

Ask whether the input is guaranteed well-formed — LeetCode promises `"+"`
always has two prior scores and `"C"` always has one, which is the only reason
the code below can index `record[-2]` without a guard. In production you would
raise instead.
""",
        ),
        (
            "The insight",
            """
There is no algorithm here; there is a **reading-comprehension test**. Every
operation refers to the *last valid score*, never to a position, so a list used
as a stack is exactly the right shape and the answer is `sum(record)`.

The one thing worth saying out loud is that `"C"` removes the last **score**,
not the last **token** — after `["5", "2", "C"]` the record is `[5]`, and a
solution that tries to undo by re-parsing the operations list gets this wrong.

Interviewers use this as a warm-up and watch how you structure the branch. A
flat `if/elif` chain reads better than a dict of lambdas here, because two of
the four cases have different arities.
""",
        ),
        (
            "The detail that bites",
            """
**Scores can be negative**, and `"-2".isdigit()` is `False`. Dispatching with

```python
if op.isdigit():
    record.append(int(op))
```

silently drops every negative score and produces a plausible-looking wrong
total. Test the three known operations first and let `int(op)` handle
everything else — it parses `"-2"` fine, and if the input really is malformed
you get a `ValueError` rather than a wrong answer.

The other quiet trap: the final total can be negative, so a `max(0, ...)` or an
unsigned accumulator is wrong.
""",
        ),
    ],
}


def cal_points(operations: list[str]) -> int:
    record: list[int] = []

    for op in operations:
        if op == "+":
            record.append(record[-1] + record[-2])
        elif op == "D":
            record.append(2 * record[-1])
        elif op == "C":
            record.pop()  # removes the last score, not the last token
        else:
            record.append(int(op))  # int() parses "-2"; isdigit() rejects it

    return sum(record)


CASES = [
    ((["5", "2", "C", "D", "+"],), 30),
    ((["5", "-2", "4", "C", "D", "9", "+", "+"],), 27),
    ((["7", "D", "D", "C", "+"],), 42),
    ((["-1", "-1", "+"],), -4),  # negatives, and a negative total
    ((["1", "C"],), 0),  # the record empties out
    ((["1"],), 1),
    (([],), 0),
]


def solve(operations: list[str]) -> int:
    return cal_points(operations)
