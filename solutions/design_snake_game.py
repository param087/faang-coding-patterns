"""Design Snake Game — LeetCode 353."""

from __future__ import annotations

from collections import deque

META = {
    "pattern": "ood",
    "symbol": "SnakeGame",
    "insight": "The snake is a queue with a membership index — and the tail must vacate its cell before the head is tested against the body.",
    "time": "O(1) per move",
    "space": "O(length of the snake), never O(width x height)",
    "sections": [
        (
            "What it asks",
            """
This one is **premium**, so the statement is not public — described here in my
own words.

Model the arcade game on a `height x width` grid:

- `SnakeGame(width, height, food)` — the snake starts one cell long at the
  top-left corner. `food` is the **ordered** list of cells where food will
  appear; only the first one is on the board at any moment, and the next
  appears the instant the current one is eaten.
- `move(direction)` with direction `"U"`, `"D"`, `"L"` or `"R"` — advance one
  cell and return the score, or `-1` if the game is over.

The game ends when the head leaves the grid or enters a cell the snake's own
body occupies. Eating grows the snake by one; otherwise the tail follows the
head and the length is unchanged.

Ask the two questions that change the code. **Does food ever appear under the
snake?** (No — guaranteed, which is why `move` never has to search for a fresh
food position.) **What happens after `-1`?** (No further calls, so the object
need not be left in a consistent state — but say you noticed, because a real
implementation would latch a `game_over` flag.)
""",
        ),
        (
            "The obvious board, and why it fails",
            """
The first design is a `height x width` grid of cells plus a list for the body:
paint the head, unpaint the tail, and check the target cell.

The grid is the cheap part; the body list is what hurts. `move` has to ask "is
the head inside the body?", and over a list that is a linear scan. A snake fed
10⁴ times is 10⁴ cells long, so 10⁴ moves cost 10⁴ x 10⁴ = **10⁸ comparisons**
for what should be constant work — and the grid itself is `height x width`
cells even when the snake occupies twelve of them.

Both problems have the same fix, and it is the standard one: an index. Keep the
body for **order** and a hash set for **membership**, and drop the grid
entirely — the walls are two comparisons, not stored cells.
""",
        ),
        (
            "The insight",
            """
A snake is a queue. Every move appends a head and — unless it ate — pops a
tail, which is precisely `appendleft` / `pop` on a `deque`. That gives O(1) at
both ends; a plain list would be O(n) on one of them.

Growth is not a special case, it is the *absence* of the usual case: eating
means "skip the tail pop this turn". Written that way there is one code path.

Alongside it, a `set` of occupied cells kept in lockstep with the deque answers
the collision test in O(1). Two structures over the same data, each doing what
the other cannot — order from the deque, membership from the set. Say that out
loud; it is the transferable idea, and it is exactly the LRU-cache trick.

Food is a `deque` too. It is consumed strictly in order, so `popleft` on a
match and `food[0]` to peek — no scanning, no index bookkeeping.
""",
        ),
        (
            "The detail that decides it: the tail moves first",
            """
Order the three steps inside `move` wrongly and you get a bug that only fires
on tight turns, which no small test will catch:

1. bounds check the new head;
2. eat, **or** pop the tail out of both the deque and the set;
3. *then* test the head against the set.

Step 2 must precede step 3. The cell the tail is standing on this instant is
free by the time the head arrives — moving into it is legal and common, because
a snake chasing its own tail does it every turn. Test collisions before popping
and you kill the player for a legal move.

Two further orderings that bite:

- **Bounds before body.** A head that has left the grid is not in the set
  either, so testing the set first still ends the game — but only by accident;
  swap in a wrap-around board later and the bug appears.
- **Eat before pop.** If the head lands on food, there is no pop at all. Popping
  first and re-appending on a match gives the same length but silently allows a
  move into the old tail cell that eating should have forbidden.

Also: a length-1 snake reversing into itself is fine — the single cell is the
tail and it vacates. The first genuinely fatal self-collision needs length 4,
which is why hand-written tests miss this.
""",
        ),
        (
            "Dry run: the tail-chase",
            """
A 3 x 3 board, `food = [(0,1), (0,2), (1,2)]`, head at `(0,0)`.

- `R` → head `(0,1)`, the food. Score **1**, body `[(0,1), (0,0)]`.
- `R` → head `(0,2)`, the next food. Score **2**, body grows to three cells.
- `D` → head `(1,2)`, the last food. Score **3**, body
  `[(1,2), (0,2), (0,1), (0,0)]`.
- `L` → head `(1,1)`, no food left. Tail `(0,0)` pops. Body
  `[(1,1), (1,2), (0,2), (0,1)]`, score **3**.
- `U` → head `(0,1)`. That is the **current tail**. It pops first, so the move
  is legal and the score is still **3**. Test collisions before popping and
  this returns `-1`.

From that same position, `D` → head `(1,1)`, the segment directly behind the
head. Nothing pops it, so it is a real collision: **-1**. Reversing into your
own neck is death; stepping into your own tail is not. One test each, or the
implementation is unverified.
""",
        ),
        (
            "Follow-ups",
            """
- **Random food instead of a script.** Now you must place food on a free cell,
  and rejection sampling degrades as the board fills. The clean answer is a
  vector of free cells plus a position map — swap-with-last removal, O(1) —
  which is the *Insert Delete GetRandom O(1)* structure.
- **Wrap-around edges.** Replace the bounds check with `% height` and `% width`.
  This is where "bounds before body" stops being a stylistic preference.
- **Rendering.** The game loop should not walk the whole snake to draw; emit the
  two cells that changed (head added, tail removed) and let the renderer patch.
- **Undo a move.** The deque loses the popped tail, so store it — an undo stack
  of `(head_added, tail_removed, ate)` triples replays backwards exactly.
- **Two players on one board.** The collision set becomes shared and each move
  needs a winner rule for simultaneous entry into the same cell; that is a
  design conversation about tick ordering, not a data-structure one.
""",
        ),
    ],
}

DIRECTIONS = {"U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1)}


class SnakeGame:
    """Deque for order, set for membership — the grid itself is never stored."""

    def __init__(self, width: int, height: int, food: list[list[int]]) -> None:
        self.width = width
        self.height = height
        self.food = deque(tuple(cell) for cell in food)  # consumed strictly in order
        self.body: deque[tuple[int, int]] = deque([(0, 0)])
        self.occupied: set[tuple[int, int]] = {(0, 0)}
        self.score = 0

    def move(self, direction: str) -> int:
        row_step, col_step = DIRECTIONS[direction]
        row, col = self.body[0]
        head = (row + row_step, col + col_step)

        # 1. Walls first — an out-of-grid head is not in `occupied` either.
        if not (0 <= head[0] < self.height and 0 <= head[1] < self.width):
            return -1

        # 2. Eat (no pop, so the snake grows) or advance the tail out of the way.
        if self.food and head == self.food[0]:
            self.food.popleft()
            self.score += 1
        else:
            self.occupied.discard(self.body.pop())

        # 3. Only now is the body test meaningful: the old tail cell is free.
        if head in self.occupied:
            return -1

        self.body.appendleft(head)
        self.occupied.add(head)
        return self.score


def check() -> None:
    game = SnakeGame(3, 2, [[1, 2], [0, 1]])
    assert game.move("R") == 0
    assert game.move("D") == 0
    assert game.move("R") == 1  # ate the food at (1, 2)
    assert game.move("U") == 1
    assert game.move("L") == 2  # ate the food at (0, 1)
    assert game.move("U") == -1  # off the top edge

    # The tail-chase: moving into the cell the tail is vacating is legal.
    chase = SnakeGame(3, 3, [[0, 1], [0, 2], [1, 2]])
    assert chase.move("R") == 1
    assert chase.move("R") == 2
    assert chase.move("D") == 3
    assert chase.move("L") == 3  # tail (0,0) pops, body is now a 4-cell hook
    assert chase.move("U") == 3  # into the old tail (0,1) — allowed
    assert list(chase.body) == [(0, 1), (1, 1), (1, 2), (0, 2)]

    # Same shape, but into the neck rather than the tail: fatal.
    neck = SnakeGame(3, 3, [[0, 1], [0, 2], [1, 2]])
    for direction, expected in (("R", 1), ("R", 2), ("D", 3), ("L", 3), ("U", 3)):
        assert neck.move(direction) == expected
    assert neck.move("D") == -1  # (1,1) is the segment directly behind the head

    # A one-cell snake may reverse into itself: the single cell is the tail.
    tiny = SnakeGame(3, 3, [])
    assert tiny.move("R") == 0
    assert tiny.move("L") == 0

    # A 1 x 1 board: every direction is a wall.
    boxed = SnakeGame(1, 1, [])
    assert boxed.move("D") == -1

    # Food exhausted: the snake keeps moving at a frozen score.
    starved = SnakeGame(4, 1, [[0, 1]])
    assert starved.move("R") == 1
    assert starved.move("R") == 1
    assert starved.move("R") == 1
    assert starved.move("R") == -1  # ran off the right edge
