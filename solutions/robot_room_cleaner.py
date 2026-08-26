"""Robot Room Cleaner — LeetCode 489."""

from __future__ import annotations

META = {
    "pattern": "matrix",
    "symbol": "clean_room",
    "insight": "Invent your own coordinate frame, then make every recursive call restore the robot's exact cell and heading before it returns.",
    "time": "O(n) — n reachable cells, at most four turns and two moves each",
    "space": "O(n) for the visited set and the recursion stack",
    "sections": [
        (
            "What it asks",
            """
This one is **premium**, so the statement is not public — described here in my
own words.

A robot sits somewhere on a rectangular grid of open cells and obstacles. You
cannot read the grid: no dimensions, no coordinates, no way to look ahead. The
entire API is four methods:

- `move()` — step one cell forward. Returns `False` and **does not move** if an
  obstacle or the edge of the grid is in the way.
- `turnLeft()` / `turnRight()` — rotate 90° in place, always succeeds.
- `clean()` — clean the cell the robot is standing on.

The robot starts on an open cell, at an unknown position, facing an unknown
direction. Clean every cell reachable from where it started.

Worth asking: is `move()` the *only* way to detect a wall (yes — it is a probe
with a side effect, which is the whole difficulty); is there any signal that
the job is done (no); does the robot have to end anywhere in particular (no,
but the solution below ends where it started, which is worth mentioning).
""",
        ),
        (
            "The insight",
            """
The robot has no coordinates, so **give it some**. Declare the starting cell
to be `(0, 0)` and the starting heading to be "up", and track every subsequent
position yourself. It does not matter that this frame has no relation to the
real grid — it only has to be *consistent*, and relative offsets are all a DFS
ever needs.

Once you have a frame, this is an ordinary four-neighbour DFS. The `visited`
set is not an optimisation here, it is the termination condition: there is no
grid to mark, so the set is the only thing standing between you and a robot
that walks the same loop forever.

One line carries the trap:

```python
if (nr, nc) not in visited and robot.move():
```

`move()` is a **probe with a side effect**. Short-circuit order is load
bearing: check `visited` first, or you step onto a cell you meant to skip, and
now your bookkeeping and the robot disagree about where it is. Every cell
after that is cleaned in the wrong place, and nothing in the API tells you.
""",
        ),
        (
            "The invariant that decides it",
            """
> Every call to the recursion must leave the robot on the **same cell facing
> the same direction** as when it was entered.

Hold that and the code is short. Break it anywhere and the robot silently
cleans the wrong cells — there is no exception, no wrong return value, just a
dirty room.

Two places enforce it:

- **`go_back()`** — turn 180°, `move()`, turn 180° again. The step back cannot
  fail, because the robot just came from that cell. Turning twice at the end
  is the part people drop; without it the caller resumes with a rotated
  heading and every remaining direction is off by 180°.
- **The unconditional `turnRight()` at the bottom of the loop.** Four
  iterations, four right turns, so the heading is back to `d` when the loop
  ends. Turning only when the move *failed* is the classic bug: it looks like
  an optimisation and it destroys the invariant.

The other silent killer is the direction table. It must be in **turnRight
order** — up, right, down, left — so that `(d + 1) % 4` really is what
`turnRight()` did. Paste in the usual up/down/left/right table out of habit and
headings desync from coordinates; an open rectangular room still comes out
spotless, and only a room with a real obstacle exposes it.

Because the invariant holds at the top level too, the robot finishes on its
starting cell facing its original direction. Say so — it is a free correctness
argument, and it is the property `check()` below asserts.
""",
        ),
    ],
}


class Robot:
    """Test double for the hidden robot API. Room: 1 = open, 0 = obstacle."""

    # turnRight order, so (facing + 1) % 4 is a right turn.
    DIRECTIONS = ((-1, 0), (0, 1), (1, 0), (0, -1))  # up, right, down, left

    def __init__(self, room: list[list[int]], row: int, col: int, facing: int = 0) -> None:
        if room[row][col] != 1:
            raise ValueError("the robot must start on an open cell")
        self.room = room
        self.row, self.col, self.facing = row, col, facing
        self.cleaned: set[tuple[int, int]] = set()

    def move(self) -> bool:
        dr, dc = self.DIRECTIONS[self.facing]
        r, c = self.row + dr, self.col + dc
        if not (0 <= r < len(self.room) and 0 <= c < len(self.room[0])):
            return False  # outside the grid counts as a wall
        if self.room[r][c] == 0:
            return False
        self.row, self.col = r, c
        return True

    def turnLeft(self) -> None:
        self.facing = (self.facing - 1) % 4

    def turnRight(self) -> None:
        self.facing = (self.facing + 1) % 4

    def clean(self) -> None:
        self.cleaned.add((self.row, self.col))


def clean_room(robot: Robot) -> None:
    # Up, right, down, left — must match what turnRight() does.
    directions = ((-1, 0), (0, 1), (1, 0), (0, -1))
    visited: set[tuple[int, int]] = set()

    def go_back() -> None:
        """Return to the previous cell, restoring the heading."""
        robot.turnRight()
        robot.turnRight()
        robot.move()  # cannot fail: the robot just came from there
        robot.turnRight()
        robot.turnRight()

    def explore(row: int, col: int, facing: int) -> None:
        visited.add((row, col))
        robot.clean()

        for turn in range(4):
            heading = (facing + turn) % 4  # the robot's actual heading right now
            dr, dc = directions[heading]
            nr, nc = row + dr, col + dc
            # visited first: move() has a side effect and must not be probed
            # for a cell we have already decided to skip.
            if (nr, nc) not in visited and robot.move():
                explore(nr, nc, heading)
                go_back()
            robot.turnRight()  # four turns across the loop restore `facing`

    explore(0, 0, 0)  # our own frame; it need not match the real grid


CASES = [
    # Single cell.
    (([[1]], 0, 0), [[2]]),
    # Diagonal neighbours are not neighbours — the far cell stays dirty.
    (([[1, 0], [0, 1]], 0, 0), [[2, 0], [0, 1]]),
    # A wall of obstacles seals off the right-hand column entirely.
    (
        ([[1, 0, 1], [1, 0, 1], [1, 0, 1]], 0, 0),
        [[2, 0, 1], [2, 0, 1], [2, 0, 1]],
    ),
    # Snake corridor: only reachable if go_back() restores position correctly.
    (
        ([[1, 1, 1], [0, 0, 1], [1, 1, 1], [1, 0, 0], [1, 1, 1]], 0, 0),
        [[2, 2, 2], [0, 0, 2], [2, 2, 2], [2, 0, 0], [2, 2, 2]],
    ),
    # Ring around a central obstacle, entered from the middle of a side.
    (
        ([[1, 1, 1], [1, 0, 1], [1, 1, 1]], 1, 0),
        [[2, 2, 2], [2, 0, 2], [2, 2, 2]],
    ),
    # Starting heading is unknown to the algorithm: facing left, mid-room.
    (([[1, 1, 1], [1, 1, 1]], 1, 1, 3), [[2, 2, 2], [2, 2, 2]]),
    # A realistic room: two obstacle bands, one single-cell doorway at (3, 3).
    (
        (
            [
                [1, 1, 1, 1, 1, 0, 1, 1],
                [1, 1, 1, 1, 1, 0, 1, 1],
                [1, 0, 1, 1, 1, 1, 1, 1],
                [0, 0, 0, 1, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
            ],
            1,
            3,
        ),
        [
            [2, 2, 2, 2, 2, 0, 2, 2],
            [2, 2, 2, 2, 2, 0, 2, 2],
            [2, 0, 2, 2, 2, 2, 2, 2],
            [0, 0, 0, 2, 0, 0, 0, 0],
            [2, 2, 2, 2, 2, 2, 2, 2],
        ],
    ),
]


def solve(room: list[list[int]], row: int, col: int, facing: int = 0) -> list[list[int]]:
    """Return the room with every cell the robot cleaned marked 2."""
    robot = Robot([line[:] for line in room], row, col, facing)
    clean_room(robot)
    return [
        [2 if (r, c) in robot.cleaned else value for c, value in enumerate(line)]
        for r, line in enumerate(room)
    ]


def check() -> None:
    for index, (args, expected) in enumerate(CASES):
        actual = solve(*args)
        assert actual == expected, f"case {index}: got {actual!r}"

    # The invariant, stated as a test: the robot ends where it began, facing
    # the direction it began with, whatever the room looks like.
    for room, row, col, *rest in (case[0] for case in CASES):
        facing = rest[0] if rest else 0
        robot = Robot([line[:] for line in room], row, col, facing)
        clean_room(robot)
        assert (robot.row, robot.col, robot.facing) == (row, col, facing)

    # A cell walled off from the start is never touched, not merely left dirty.
    robot = Robot([[1, 0, 1]], 0, 0)
    clean_room(robot)
    assert robot.cleaned == {(0, 0)}
