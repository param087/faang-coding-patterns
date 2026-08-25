"""Topological sort and cycle detection.

Any "do B only after A" question is a DAG, and the answer is either a valid
order or a proof that none exists. Kahn's algorithm gives both at once: if the
output is shorter than the node count, the leftovers are in a cycle.
"""

from __future__ import annotations

from collections import deque


def topological_order(n: int, edges: list[tuple[int, int]]) -> list[int]:
    """A valid ordering of nodes 0..n-1, or [] if the graph has a cycle.

    Kahn's algorithm. Start with everything that has no prerequisite, and each
    time a node is emitted, decrement its dependants — any that reach zero are
    now ready.
    """
    adjacency: list[list[int]] = [[] for _ in range(n)]
    indegree = [0] * n

    for before, after in edges:
        adjacency[before].append(after)
        indegree[after] += 1

    queue = deque(node for node in range(n) if indegree[node] == 0)
    order: list[int] = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbour in adjacency[node]:
            indegree[neighbour] -= 1
            if indegree[neighbour] == 0:
                queue.append(neighbour)

    # Short output means some nodes never reached indegree 0 — a cycle.
    return order if len(order) == n else []


def can_finish(n: int, prerequisites: list[list[int]]) -> bool:
    """Course Schedule: is any complete ordering possible?"""
    return bool(topological_order(n, [(b, a) for a, b in prerequisites])) or n == 0


def has_cycle_directed(n: int, edges: list[tuple[int, int]]) -> bool:
    """Cycle detection by DFS colouring, as an alternative to Kahn.

    Three states matter: unvisited (0), on the current path (1), fully done
    (2). Meeting a node in state 1 means you have looped back onto your own
    path — that is a cycle. Meeting state 2 is fine; it is a shared dependency,
    not a cycle, and conflating the two is the usual bug.
    """
    adjacency: list[list[int]] = [[] for _ in range(n)]
    for before, after in edges:
        adjacency[before].append(after)

    state = [0] * n

    def visit(node: int) -> bool:
        if state[node] == 1:
            return True  # back edge onto the current path
        if state[node] == 2:
            return False  # already fully explored, no cycle through here
        state[node] = 1
        for neighbour in adjacency[node]:
            if visit(neighbour):
                return True
        state[node] = 2
        return False

    return any(state[node] == 0 and visit(node) for node in range(n))


def alien_order(words: list[str]) -> str:
    """Alien Dictionary: derive the alphabet from a sorted word list.

    Two thirds of this problem is building the graph, not sorting it. Only
    the *first differing character* between adjacent words carries
    information, and the prefix case (`["abc", "ab"]`) is invalid input rather
    than a no-op — missing that check is the standard failure.
    """
    letters = {char for word in words for char in word}
    adjacency: dict[str, set[str]] = {char: set() for char in letters}
    indegree = dict.fromkeys(letters, 0)

    for first, second in zip(words, words[1:], strict=False):
        if len(first) > len(second) and first.startswith(second):
            return ""  # a longer word cannot precede its own prefix
        for a, b in zip(first, second, strict=False):
            if a != b:
                if b not in adjacency[a]:
                    adjacency[a].add(b)
                    indegree[b] += 1
                break  # only the first difference is informative

    queue = deque(sorted(char for char in letters if indegree[char] == 0))
    order: list[str] = []
    while queue:
        char = queue.popleft()
        order.append(char)
        for neighbour in sorted(adjacency[char]):
            indegree[neighbour] -= 1
            if indegree[neighbour] == 0:
                queue.append(neighbour)

    return "".join(order) if len(order) == len(letters) else ""


CASES = [
    ((2, [[1, 0]]), True),
    ((2, [[1, 0], [0, 1]]), False),
    ((4, [[1, 0], [2, 1], [3, 2]]), True),
    ((1, []), True),
]


def solve(n: int, prerequisites: list[list[int]]) -> bool:
    return can_finish(n, prerequisites)


def check() -> None:
    for args, expected in CASES:
        assert can_finish(*args) == expected

    order = topological_order(4, [(0, 1), (0, 2), (1, 3), (2, 3)])
    assert order[0] == 0 and order[-1] == 3
    assert topological_order(2, [(0, 1), (1, 0)]) == []

    assert has_cycle_directed(3, [(0, 1), (1, 2)]) is False
    assert has_cycle_directed(3, [(0, 1), (1, 2), (2, 0)]) is True
    # A shared dependency is not a cycle — the state-2 case.
    assert has_cycle_directed(4, [(0, 1), (0, 2), (1, 3), (2, 3)]) is False

    assert alien_order(["wrt", "wrf", "er", "ett", "rftt"]) == "wertf"
    assert alien_order(["z", "x"]) == "zx"
    assert alien_order(["z", "x", "z"]) == ""
    assert alien_order(["abc", "ab"]) == ""  # invalid: prefix ordering
