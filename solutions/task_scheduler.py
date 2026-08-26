"""Task Scheduler — LeetCode 621."""

from __future__ import annotations

from collections import Counter

META = {
    "pattern": "greedy",
    "insight": "The most frequent task defines a skeleton of gaps; if there are enough other tasks to fill them, there is no idling at all.",
    "time": "O(n)",
    "space": "O(1) — at most 26 task types",
    "sections": [
        (
            "What it asks",
            """
Tasks must be separated by at least `n` intervals between **identical** ones.
Return the least total time, counting idle slots.

Ask: is the output the schedule or just its **length**? (Just the length — and
that is what makes a closed form possible.) Can tasks be reordered freely
(yes)? Is the cooldown between identical tasks only (yes)?
""",
        ),
        (
            "The simulation, and why to move past it",
            """
A max-heap of counts plus a cooldown queue works, and is a perfectly good
answer. O(total time · log 26).

But there is a **closed form**, and finding it is the point of the question.
""",
        ),
        (
            "The skeleton",
            """
Let `maxCount` be the frequency of the most common task. Lay those out first,
separated by the required cooldown:

```
A _ _ A _ _ A
```

That is `(maxCount - 1)` gaps, each of length `(n + 1)`, plus the final `A`.
Any *other* task tied at `maxCount` also has to appear at the end, so add one
per tie.

```
skeleton = (maxCount - 1) * (n + 1) + tiedAtMax
```
""",
        ),
        (
            "The other branch",
            """
If there are **enough distinct tasks to fill every idle slot**, there is no
idling at all and the answer is simply `len(tasks)`.

`max(len(tasks), skeleton)` handles both regimes in one line — and being able
to explain *both branches* is what makes it a real answer rather than a
remembered formula:

- the skeleton dominates when one task is very frequent;
- `len(tasks)` dominates when the work is spread out.
""",
        ),
        (
            "Dry run both branches",
            """
`["A","A","A","B","B","B"], n = 2` → skeleton = `2·3 + 2` = **8**. There are 6
tasks, so the skeleton wins: `A B _ A B _ A B`.

`["A","A","A","B","C","D","E","F","G"], n = 2` → skeleton = `2·3 + 1` = 7, but
there are **9** tasks, so the answer is **9**. Every idle slot gets filled.

That second case is what catches a formula written without the `max`.
""",
        ),
        (
            "Follow-ups",
            """
- **Return the actual schedule** — now you need the simulation, because the
  formula only gives the length.
- **Task Scheduler II**, where the cooldown is per task type and given per
  task — a hash map of "earliest next allowed time".
""",
        ),
    ],
}


def least_interval(tasks: list[str], n: int) -> int:
    if not tasks:
        return 0

    counts = Counter(tasks)
    max_count = max(counts.values())
    tied_at_max = sum(1 for count in counts.values() if count == max_count)

    # (maxCount - 1) gaps of length (n + 1), plus everything tied at the end.
    skeleton = (max_count - 1) * (n + 1) + tied_at_max

    # If there are enough other tasks to fill every idle slot, none are idle.
    return max(len(tasks), skeleton)


CASES = [
    ((["A", "A", "A", "B", "B", "B"], 2), 8),
    ((["A", "A", "A", "B", "B", "B"], 0), 6),
    ((["A", "A", "A", "B", "C", "D", "E", "F", "G"], 2), 9),
    ((["A"], 5), 1),
    ((["A", "B", "C"], 10), 3),
    ((["A", "A"], 3), 5),
    (([], 2), 0),
]


def solve(tasks: list[str], n: int) -> int:
    return least_interval(tasks, n)
