"""Graph traversal: BFS and DFS, on grids and adjacency lists.

The choice is not stylistic. **BFS gives shortest path in an unweighted
graph; DFS does not.** If the question says "fewest steps", "minimum moves"
or "shortest", it is BFS. If it says "does a path exist" or "explore this
region", either works and DFS is shorter to write.
"""

from __future__ import annotations

from collections import deque

DIRECTIONS = ((0, 1), (1, 0), (0, -1), (-1, 0))


def num_islands(grid: list[list[str]]) -> int:
    """Count connected regions of '1' in a grid.

    Sinking each island as you visit it — overwriting '1' with '0' — is the
    O(1)-space alternative to a `visited` set. Mention that it mutates the
    input; some interviewers care, and offering to restore it or use a set
    instead is the right answer.
    """
    if not grid or not grid[0]:
        return 0

    rows, cols = len(grid), len(grid[0])
    count = 0

    def sink(start_r: int, start_c: int) -> None:
        # Iterative, not recursive: a 300x300 grid of land overflows the stack.
        stack = [(start_r, start_c)]
        grid[start_r][start_c] = "0"
        while stack:
            r, c = stack.pop()
            for dr, dc in DIRECTIONS:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == "1":
                    grid[nr][nc] = "0"  # mark on push, not on pop
                    stack.append((nr, nc))

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1":
                count += 1
                sink(r, c)

    return count


def rotting_oranges(grid: list[list[int]]) -> int:
    """Minutes until every fresh orange rots, or -1.

    Multi-source BFS: seed the queue with *every* rotten orange at once and
    the level count is the answer. Running a separate BFS per source would be
    O(sources · cells) and gives the wrong answer anyway, because rot spreads
    simultaneously.
    """
    if not grid or not grid[0]:
        return 0

    rows, cols = len(grid), len(grid[0])
    queue: deque[tuple[int, int]] = deque()
    fresh = 0

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2:
                queue.append((r, c))
            elif grid[r][c] == 1:
                fresh += 1

    if fresh == 0:
        return 0

    minutes = 0
    while queue and fresh:
        for _ in range(len(queue)):  # one minute = one level
            r, c = queue.popleft()
            for dr, dc in DIRECTIONS:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                    grid[nr][nc] = 2
                    fresh -= 1
                    queue.append((nr, nc))
        minutes += 1

    return minutes if fresh == 0 else -1


def shortest_path_unweighted(
    graph: dict[int, list[int]], start: int, goal: int
) -> int:
    """Fewest edges from start to goal, or -1.

    The template for "minimum moves" questions. Mark visited **when you
    enqueue**, not when you dequeue — otherwise a node can be queued many
    times before it is first processed, and the queue blows up.
    """
    if start == goal:
        return 0

    visited = {start}
    queue: deque[int] = deque([start])
    steps = 0

    while queue:
        steps += 1
        for _ in range(len(queue)):
            node = queue.popleft()
            for neighbour in graph.get(node, ()):
                if neighbour == goal:
                    return steps
                if neighbour not in visited:
                    visited.add(neighbour)  # on enqueue
                    queue.append(neighbour)

    return -1


CASES = [
    (
        (
            [
                ["1", "1", "0", "0", "0"],
                ["1", "1", "0", "0", "0"],
                ["0", "0", "1", "0", "0"],
                ["0", "0", "0", "1", "1"],
            ],
        ),
        3,
    ),
    (([["1", "1"], ["1", "1"]],), 1),
    (([["0"]],), 0),
    (([],), 0),
]


def solve(grid: list[list[str]]) -> int:
    return num_islands(grid)


def check() -> None:
    for args, expected in CASES:
        assert num_islands(*[[row[:] for row in a] if a else a for a in args]) == expected

    assert rotting_oranges([[2, 1, 1], [1, 1, 0], [0, 1, 1]]) == 4
    assert rotting_oranges([[2, 1, 1], [0, 1, 1], [1, 0, 1]]) == -1
    assert rotting_oranges([[0, 2]]) == 0

    graph = {1: [2, 3], 2: [4], 3: [4], 4: [5]}
    assert shortest_path_unweighted(graph, 1, 5) == 3
    assert shortest_path_unweighted(graph, 1, 1) == 0
    assert shortest_path_unweighted(graph, 5, 1) == -1
