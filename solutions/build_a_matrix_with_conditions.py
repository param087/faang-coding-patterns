"""Build a Matrix With Conditions — LeetCode 2392."""

from __future__ import annotations

from collections import deque

META = {
    "pattern": "topological-sort",
    "insight": "Rows and columns are independent: two separate topological sorts of 1..k, then value v lands at (rowRank[v], colRank[v]).",
    "time": "O(k + conditions)",
    "space": "O(k²) for the output, O(k + conditions) for the sorts",
    "sections": [
        (
            "What it asks",
            """
Place each of `1 .. k` exactly once in a `k × k` grid (all other cells 0) so
that every `rowConditions[i] = [a, b]` puts `a` in a **strictly earlier row**
than `b`, and every `colConditions[i] = [a, b]` puts `a` in a strictly earlier
column. Return any valid matrix, or `[]` if none exists.

Read the word "row" carefully: the constraint is on row *index*, and says
nothing about columns. Same for the column constraints. That independence is
the entire problem — everything else is bookkeeping.

Ask whether the conditions may repeat or contradict each other. Both happen, and
neither needs special handling beyond the cycle check.
""",
        ),
        (
            "The insight",
            """
The two constraint families never interact. A row condition never mentions a
column and vice versa, so:

1. Topologically sort `1 .. k` under `rowConditions` → `rowRank[v]`.
2. Topologically sort `1 .. k` under `colConditions` → `colRank[v]`.
3. Write `v` at `(rowRank[v], colRank[v])`.

Because each sort is a permutation of `1 .. k`, every row index is used exactly
once and every column index exactly once — the placements can never collide.
That is why a `k × k` grid is always big enough and why no packing or
backtracking is needed. If you find yourself trying to place values one at a
time and checking conflicts, you have missed the decomposition.

Impossible exactly when one of the two sorts has a cycle; then return `[]`.

The trap that costs people the question: after computing the two orders, filling
the matrix by *iterating over the orders* and incrementing a shared counter. You
must index by the value — `matrix[rowRank[v]][colRank[v]] = v` — because the row
order and column order are different permutations.

O(k + conditions). At k = 400 and 10⁴ conditions this is trivial; the difficulty
rating is entirely about spotting the independence.
""",
        ),
        (
            "Edge cases",
            """
- **A cycle in *either* family** → `[]`. `rowConditions = [[1,2],[2,3],[3,1]]`
  fails even if the column conditions are perfectly consistent. Check both
  before building anything.
- **Duplicate conditions.** `[[1,2],[1,2]]` doubles `indegree[2]`; both
  decrements fire, so Kahn is unaffected. But if you switch to `set` adjacency,
  guard the indegree increment or node 2 never becomes ready and you return `[]`
  for a solvable input.
- **A self-condition** `[1, 1]` is a self-loop → `[]`, for free.
- **No conditions at all** → any permutation works; Kahn emits `1, 2, ..., k`
  and the answer is the identity diagonal.
- **`k = 1`** → `[[1]]`.
- **Values with no constraints** still have to be placed. Seeding the queue from
  every indegree-0 node in `1 .. k`, not just from nodes that appear in the
  conditions, is what covers them.
- The answer is not unique, so the tests below **verify** a returned matrix
  against the conditions rather than comparing it to a fixed grid.
""",
        ),
    ],
}


def _topological_order(k: int, conditions: list[list[int]]) -> list[int] | None:
    adjacency: list[list[int]] = [[] for _ in range(k + 1)]
    indegree = [0] * (k + 1)

    for earlier, later in conditions:
        adjacency[earlier].append(later)
        indegree[later] += 1

    queue = deque(value for value in range(1, k + 1) if indegree[value] == 0)
    order: list[int] = []

    while queue:
        value = queue.popleft()
        order.append(value)
        for successor in adjacency[value]:
            indegree[successor] -= 1
            if indegree[successor] == 0:
                queue.append(successor)

    return order if len(order) == k else None  # None means a cycle


def build_matrix(
    k: int,
    row_conditions: list[list[int]],
    col_conditions: list[list[int]],
) -> list[list[int]]:
    row_order = _topological_order(k, row_conditions)
    col_order = _topological_order(k, col_conditions)
    if row_order is None or col_order is None:
        return []

    row_rank = {value: index for index, value in enumerate(row_order)}
    col_rank = {value: index for index, value in enumerate(col_order)}

    matrix = [[0] * k for _ in range(k)]
    for value in range(1, k + 1):  # index by value, not by position in the order
        matrix[row_rank[value]][col_rank[value]] = value
    return matrix


def _assert_valid(
    k: int,
    row_conditions: list[list[int]],
    col_conditions: list[list[int]],
    matrix: list[list[int]],
) -> None:
    assert len(matrix) == k, matrix
    assert all(len(row) == k for row in matrix), matrix

    position: dict[int, tuple[int, int]] = {}
    for r, row in enumerate(matrix):
        for c, value in enumerate(row):
            if value:
                assert value not in position, (value, matrix)
                position[value] = (r, c)

    assert set(position) == set(range(1, k + 1)), matrix
    for above, below in row_conditions:
        assert position[above][0] < position[below][0], (above, below, matrix)
    for left, right in col_conditions:
        assert position[left][1] < position[right][1], (left, right, matrix)


def check() -> None:
    solvable = [
        (3, [[1, 2], [3, 2]], [[2, 1], [3, 2]]),
        (1, [], []),
        (2, [[1, 2]], [[1, 2]]),
        (4, [[1, 2], [2, 3], [3, 4]], [[4, 3], [3, 2], [2, 1]]),
        (3, [[1, 2], [1, 2]], [[1, 3]]),
        (5, [], []),
        (4, [[2, 1]], []),
    ]
    for k, row_conditions, col_conditions in solvable:
        matrix = build_matrix(k, row_conditions, col_conditions)
        _assert_valid(k, row_conditions, col_conditions, matrix)

    impossible = [
        (3, [[1, 2], [2, 3], [3, 1], [2, 3]], [[2, 1]]),
        (2, [], [[1, 2], [2, 1]]),
        (2, [[1, 1]], []),
        (3, [[1, 2], [2, 1]], [[1, 2], [2, 3]]),
    ]
    for k, row_conditions, col_conditions in impossible:
        assert build_matrix(k, row_conditions, col_conditions) == [], (k, row_conditions)
