"""Snakes and Ladders — LeetCode 909."""

from __future__ import annotations

from collections import deque

META = {
    "pattern": "graph-traversal",
    "insight": "Flatten the boustrophedon board into 1..n squares once, then it is BFS on a graph where every square has six out-edges.",
    "time": "O(n²)",
    "space": "O(n²)",
    "sections": [
        (
            "What it asks",
            """
An `n × n` board numbered 1 to n² in **boustrophedon** order — bottom row left
to right, the row above it right to left, and so on. From square `s` you may
move to any of `s+1 … s+6` that exist; if that destination holds a value other
than −1, you are teleported to that value. Return the fewest dice rolls to
reach n², or −1.

Two rules decide the whole problem, so confirm both:

1. A destination reached **via** a snake or ladder does **not** trigger a
   second one. One hop per roll, full stop.
2. You may choose any of the six numbers, not roll randomly — this is a
   shortest-path question, not a probability one.
""",
        ),
        (
            "The insight",
            """
Squares are nodes, one roll is one edge, all edges cost 1 — BFS. The problem
is not the search, it is the **coordinate conversion**, and that is where the
time actually goes.

Do it once, up front: walk the rows from the bottom upwards, reversing every
other row, and copy the board into a flat list indexed 1…n². After that, the
BFS reads like a toy:

```
for roll in range(1, 7):
    nxt = square + roll
    dest = flat[nxt] if flat[nxt] != -1 else nxt
```

Deriving `(row, col)` from `s` inside the loop with `divmod(s - 1, n)` and a
conditional column flip works too, and is the version people get wrong under
pressure — the off-by-one from 1-indexing and the parity of the row flip
interact. Flatten once and the bug class disappears.

For the record, the in-place formula: `r, c = divmod(s - 1, n)`, the actual
row is `n - 1 - r`, and the column is `c` when `r` is even and `n - 1 - c`
when it is odd.
""",
        ),
        (
            "Pitfalls",
            """
- **Marking the wrong square visited.** After a ladder you must mark the
  *destination*, not the square you landed on to trigger it. Marking the
  trigger square lets a different path re-enter it and re-ride the ladder,
  and marking only the destination is what stops that.
- **Chaining.** `dest = flat[nxt] if flat[nxt] != -1 else nxt`, and then you
  stop. No `while`. Chaining ladders looks generous and produces wrong,
  too-small answers.
- **Reaching the goal mid-roll.** Return as soon as `dest == n²`; a snake at
  n² cannot exist by the constraints, but a ladder *into* n² can, and that is
  the shortest answer.
- **n = 1** → 0 rolls, you are already there.
- The board can be **unwinnable** — a snake ring that never lets you past —
  and the queue simply drains to −1.

Follow-up worth mentioning: if the dice were weighted or rolls had costs, the
uniform-edge assumption breaks and it becomes Dijkstra. If instead you wanted
the *expected* number of rolls with a fair die, it is a linear system, not a
traversal at all.
""",
        ),
    ],
}


def snakes_and_ladders(board: list[list[int]]) -> int:
    n = len(board)
    target = n * n
    if target == 1:
        return 0  # a 1x1 board starts on the goal

    # Flatten boustrophedon order once: flat[1] is the bottom-left square.
    flat = [0] * (target + 1)
    square = 1
    for r in range(n - 1, -1, -1):
        row = board[r] if (n - 1 - r) % 2 == 0 else board[r][::-1]
        for value in row:
            flat[square] = value
            square += 1

    seen = [False] * (target + 1)
    seen[1] = True
    queue: deque[int] = deque([1])
    rolls = 0

    while queue:
        rolls += 1
        for _ in range(len(queue)):
            current = queue.popleft()
            for roll in range(1, 7):
                nxt = current + roll
                if nxt > target:
                    break
                dest = flat[nxt] if flat[nxt] != -1 else nxt  # one hop, never chained
                if dest == target:
                    return rolls
                if not seen[dest]:  # mark the destination, not the trigger
                    seen[dest] = True
                    queue.append(dest)

    return -1


CASES = [
    (
        (
            [
                [-1, -1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1, -1],
                [-1, 35, -1, -1, 13, -1],
                [-1, -1, -1, -1, -1, -1],
                [-1, 15, -1, -1, -1, -1],
            ],
        ),
        4,
    ),
    (([[-1, -1], [-1, 3]],), 1),
    (([[-1, -1], [-1, -1]],), 1),  # one roll covers a 2x2 board
    (([[-1]],), 0),  # already on the last square
    (([[-1, 4, -1], [6, 2, 6], [-1, 3, -1]],), 2),
    # Square 2 is a snake back to the start; square 5 is a ladder straight to the
    # goal, so the answer is 1 only if you return the moment dest == n².
    (([[-1, -1, -1], [-1, 9, 8], [-1, 1, -1]],), 1),
    (([[1, 1, -1], [1, 1, 1], [-1, 1, 1]],), -1),  # every roll loops back to 1
]


def solve(board: list[list[int]]) -> int:
    return snakes_and_ladders([row[:] for row in board])
