"""Advanced graph algorithms: bipartite checking, bridges, SCCs, Eulerian paths.

Rare, and worth exactly the effort of recognising them plus one template each.
The recognition matters more than the implementation: knowing that "critical
connection" means *bridge* gets you most of the way, because the algorithm is
short once you know its name.
"""

from __future__ import annotations

from collections import defaultdict, deque


def is_bipartite(graph: list[list[int]]) -> bool:
    """Can the nodes be two-coloured so no edge joins same-coloured nodes?

    BFS colouring. Equivalent to "no odd-length cycle", which is the phrasing
    that makes Possible Bipartition recognisable as this problem. Every
    component needs its own start, since the graph may be disconnected.
    """
    colour: dict[int, int] = {}

    for start in range(len(graph)):
        if start in colour:
            continue
        colour[start] = 0
        queue = deque([start])
        while queue:
            node = queue.popleft()
            for neighbour in graph[node]:
                if neighbour not in colour:
                    colour[neighbour] = 1 - colour[node]
                    queue.append(neighbour)
                elif colour[neighbour] == colour[node]:
                    return False

    return True


def critical_connections(n: int, connections: list[list[int]]) -> list[list[int]]:
    """Bridges: edges whose removal disconnects the graph. Tarjan, O(V + E).

    `disc[u]` is when u was discovered; `low[u]` is the earliest discovery
    time reachable from u's subtree using at most one back edge. Edge (u, v)
    is a bridge exactly when `low[v] > disc[u]` — v's subtree has no other way
    back up, so that edge is the only link.
    """
    adjacency: dict[int, list[int]] = defaultdict(list)
    for a, b in connections:
        adjacency[a].append(b)
        adjacency[b].append(a)

    disc = [-1] * n
    low = [0] * n
    bridges: list[list[int]] = []
    timer = 0

    def dfs(node: int, parent: int) -> None:
        nonlocal timer
        disc[node] = low[node] = timer
        timer += 1
        for neighbour in adjacency[node]:
            if neighbour == parent:
                continue  # don't treat the edge we arrived on as a back edge
            if disc[neighbour] == -1:
                dfs(neighbour, node)
                low[node] = min(low[node], low[neighbour])
                if low[neighbour] > disc[node]:
                    bridges.append([node, neighbour])
            else:
                low[node] = min(low[node], disc[neighbour])

    for node in range(n):
        if disc[node] == -1:
            dfs(node, -1)

    return bridges


def find_eulerian_path(tickets: list[list[str]], start: str = "JFK") -> list[str]:
    """Reconstruct Itinerary — an Eulerian path using every edge exactly once.

    Hierholzer's algorithm, and the counter-intuitive part is that the answer
    is built **backwards**: a node is appended only once it has no unused
    edges left, and the finished list is reversed. A plain greedy DFS gets
    stuck in a dead end and cannot back out.
    """
    graph: dict[str, list[str]] = defaultdict(list)
    for source, destination in sorted(tickets, reverse=True):
        graph[source].append(destination)  # reverse-sorted so pop() is smallest

    route: list[str] = []
    stack = [start]

    while stack:
        while graph[stack[-1]]:
            stack.append(graph[stack[-1]].pop())
        route.append(stack.pop())  # no edges left: this node is finished

    return route[::-1]


def find_celebrity(knows: list[list[int]], n: int) -> int:
    """The one person everybody knows and who knows nobody. O(n) calls.

    The elimination pass is the trick: if `candidate` knows `i`, the candidate
    cannot be the celebrity, so move on; if not, `i` cannot be. Either way one
    person is eliminated per comparison, so n-1 comparisons leave one
    candidate — who must then be verified.
    """
    candidate = 0
    for i in range(1, n):
        if knows[candidate][i]:
            candidate = i

    for i in range(n):
        if i == candidate:
            continue
        if knows[candidate][i] or not knows[i][candidate]:
            return -1

    return candidate


CASES = [
    (([[1, 3], [0, 2], [1, 3], [0, 2]],), True),
    (([[1, 2, 3], [0, 2], [0, 1, 3], [0, 2]],), False),
    (([[]],), True),
    (([[1], [0]],), True),
]


def solve(graph: list[list[int]]) -> bool:
    return is_bipartite(graph)


def check() -> None:
    for args, expected in CASES:
        assert is_bipartite(*args) == expected

    bridges = critical_connections(4, [[0, 1], [1, 2], [2, 0], [1, 3]])
    assert bridges == [[1, 3]]  # the triangle has no bridges
    assert critical_connections(2, [[0, 1]]) == [[0, 1]]

    assert find_eulerian_path([["MUC", "LHR"], ["JFK", "MUC"], ["SFO", "SJC"], ["LHR", "SFO"]]) == [
        "JFK",
        "MUC",
        "LHR",
        "SFO",
        "SJC",
    ]
    # The greedy trap: JFK->ATL->JFK->SFO->ATL->SFO, not the lexically eager route.
    assert find_eulerian_path(
        [["JFK", "SFO"], ["JFK", "ATL"], ["SFO", "ATL"], ["ATL", "JFK"], ["ATL", "SFO"]]
    ) == ["JFK", "ATL", "JFK", "SFO", "ATL", "SFO"]

    knows = [[0, 1, 1], [0, 0, 1], [0, 0, 0]]
    assert find_celebrity(knows, 3) == 2
    assert find_celebrity([[0, 1], [1, 0]], 2) == -1
