"""Sort Items by Groups Respecting Dependencies — LeetCode 1203."""

from __future__ import annotations

from collections import defaultdict, deque

META = {
    "pattern": "topological-sort",
    "insight": "Two topological sorts, not one: order the groups as super-nodes, order the items inside each group, then concatenate.",
    "time": "O(n + m + E)",
    "space": "O(n + m + E)",
    "sections": [
        (
            "What it asks",
            """
`n` items, `m` groups, `group[i]` is item `i`'s group or `-1` for none, and
`beforeItems[i]` lists items that must precede `i`. Produce any ordering in
which every dependency is respected **and items of the same group are
contiguous**. Return `[]` if impossible.

The clarifying question that decides the whole solution: **must a dependency
inside a group also be respected?** Yes — the contiguity constraint sits on top
of the ordering constraint, it does not replace it. And: **do items with
`group == -1` form one shared group?** No. Each is independent; treating them
as a single group is the classic wrong answer, because it forces unrelated
loners to sit together and invents cycles that are not there.
""",
        ),
        (
            "The insight",
            """
Contiguity means the groups behave as **super-nodes**. Any edge `u → v` is one
of two kinds:

- **same group** — an ordering constraint *inside* one block;
- **different groups** — an ordering constraint *between* blocks, i.e. an edge
  `group[u] → group[v]` in a second, smaller graph.

So run Kahn twice on two independent graphs, then interleave: sort the groups,
sort the items using only intra-group edges, bucket the item order by group,
and emit the buckets in group order. Either sort coming up short means a cycle
and the answer is `[]` — a cycle among groups is just as fatal as one among
items.

The enabling trick is the first three lines: give every `-1` item a **fresh
group id** of its own. After that the code has no special case at all — a
lone item is simply a group of size one, free to be placed wherever the group
sort puts it.

Sorting the items globally (over intra-group edges only) rather than
per-group is a small simplification worth taking: a topological order stays
topological when you filter it down to a subset, so bucketing the single order
by group gives each block a valid internal order for free.
""",
        ),
        (
            "The traps",
            """
- **All `-1` items lumped together.** `n = 3`, no groups, and an edge
  `0 → 1`: with one shared pseudo-group the intra-group graph now owns that
  edge and everything still works — but add an item that must sit between two
  *real* groups and the fake block cannot be split. Fresh ids per item, always.
- **Only checking the item sort for cycles.** Groups can deadlock while every
  item is individually orderable: item 0 in group A before item 1 in group B,
  and item 2 in group B before item 3 in group A. No item cycle exists; the
  group graph is `A → B → A`. Answer `[]`.
- **Cross-group edges added to the item graph too.** They must go to exactly
  one of the two graphs. Adding them to both re-imposes a global order that the
  group sort has already handled, and can reject satisfiable inputs.
- **Duplicate edges** are harmless — each copy increments an indegree once and
  decrements it once — so there is no need to deduplicate under time pressure.
""",
        ),
    ],
}


def _kahn(adjacency: list[list[int]], indegree: list[int]) -> list[int] | None:
    """Kahn's algorithm; None when a cycle leaves nodes unemitted."""
    queue = deque(node for node, degree in enumerate(indegree) if degree == 0)
    order: list[int] = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbour in adjacency[node]:
            indegree[neighbour] -= 1
            if indegree[neighbour] == 0:
                queue.append(neighbour)

    return order if len(order) == len(indegree) else None


def sort_items(n: int, m: int, group: list[int], before_items: list[list[int]]) -> list[int]:
    # Every ungrouped item becomes a group of one, killing the -1 special case.
    owner = list(group)
    groups = m
    for item in range(n):
        if owner[item] == -1:
            owner[item] = groups
            groups += 1

    item_adjacency: list[list[int]] = [[] for _ in range(n)]
    item_indegree = [0] * n
    group_adjacency: list[list[int]] = [[] for _ in range(groups)]
    group_indegree = [0] * groups

    for after, befores in enumerate(before_items):
        for before in befores:
            if owner[before] == owner[after]:
                item_adjacency[before].append(after)  # inside one block
                item_indegree[after] += 1
            else:
                group_adjacency[owner[before]].append(owner[after])  # between blocks
                group_indegree[owner[after]] += 1

    group_order = _kahn(group_adjacency, group_indegree)
    item_order = _kahn(item_adjacency, item_indegree)
    if group_order is None or item_order is None:
        return []

    # A topological order restricted to a subset is still topological.
    buckets: dict[int, list[int]] = defaultdict(list)
    for item in item_order:
        buckets[owner[item]].append(item)

    result: list[int] = []
    for block in group_order:
        result.extend(buckets[block])
    return result


CASES = [
    (
        (8, 2, [-1, -1, 1, 0, 0, 1, 0, -1], [[], [6], [5], [6], [3, 6], [], [], []]),
        [6, 3, 4, 5, 2, 0, 7, 1],
    ),
    (
        (8, 2, [-1, -1, 1, 0, 0, 1, 0, -1], [[], [6], [5], [6], [3], [], [4], []]),
        [],  # 6 -> 4 -> 3 -> 6 is a cycle inside group 0
    ),
    ((1, 1, [-1], [[]]), [0]),
    ((3, 0, [-1, -1, -1], [[], [0], [1]]), [0, 1, 2]),  # every item its own group
    (
        (4, 2, [0, 1, 1, 0], [[], [0], [], [2]]),
        [],  # group 0 -> 1 (via 0 -> 1) and group 1 -> 0 (via 2 -> 3)
    ),
    ((3, 1, [0, 0, 0], [[], [0], [1]]), [0, 1, 2]),  # single group, pure chain
    ((2, 2, [0, 1], [[], []]), [0, 1]),  # no edges at all
]


def check() -> None:
    for index, (args, expected) in enumerate(CASES):
        actual = solve(*args)
        assert actual == expected, f"case {index}: got {actual!r}, expected {expected!r}"

    # Any valid arrangement is acceptable, so also verify the properties rather
    # than one blessed permutation.
    for args, expected in CASES:
        if not expected:
            continue
        n, m, group, before_items = args
        order = solve(n, m, group, before_items)
        assert sorted(order) == list(range(n)), f"{order!r} is not a permutation"

        position = {item: index for index, item in enumerate(order)}
        for after, befores in enumerate(before_items):
            for before in befores:
                assert position[before] < position[after], f"{before} must precede {after}"

        seen: set[int] = set()
        previous: int | None = None
        for item in order:
            block = group[item] if group[item] != -1 else ~item  # loners are distinct
            if block != previous:
                assert block not in seen, f"group {block} is not contiguous in {order!r}"
                seen.add(block)
                previous = block


def solve(n: int, m: int, group: list[int], before_items: list[list[int]]) -> list[int]:
    return sort_items(n, m, list(group), [list(row) for row in before_items])
