"""Find Eventual Safe States — LeetCode 802."""

from __future__ import annotations

from collections import deque

META = {
    "pattern": "topological-sort",
    "insight": "Reverse every edge and outdegree becomes indegree, so Kahn's algorithm peels safe nodes back from the terminals.",
    "time": "O(V + E)",
    "space": "O(V + E)",
    "sections": [
        (
            "What it asks",
            """
A directed graph given as `graph[i] = [successors of i]`. A node is **safe** if
*every* walk starting there reaches a terminal node (one with no outgoing
edges) in a bounded number of steps. Return the safe nodes in ascending order.

The definition is universally quantified — *every* path, not *some* path. That
is the whole problem. Anyone who answers "reachable from a terminal" has
flipped the quantifier and will return unsafe nodes that merely *happen* to
have one good exit.

Restated: a node is safe iff no path from it can enter a cycle.
""",
        ),
        (
            "The insight",
            """
Terminal nodes are safe by definition. A node is safe iff **all** its
successors are safe. That is a bottom-up recurrence over the graph, and the
bottom is the set of outdegree-0 nodes.

Run Kahn's algorithm on the **reversed** graph:

- `outdegree[v]` in the original plays the role of an indegree;
- seed the queue with every node whose outdegree is 0 (the terminals);
- popping a safe node `v` decrements the outdegree of each of its original
  predecessors, and when a predecessor hits 0, *all* of its successors have been
  confirmed safe, so it is safe too.

Whatever never enters the queue is a cycle or feeds into one — exactly the
unsafe set. The reverse adjacency exists only so a popped node can find who was
waiting on it.

The DFS alternative is a three-colour cycle detection with memoisation: grey
means "on the current stack", and any node that reaches a grey node is unsafe.
Equally O(V + E), but you have to be careful to cache the *unsafe* verdict as
well, or a diamond of failures re-explores exponentially.
""",
        ),
        (
            "The wrong first answer",
            """
The tempting shortcut is "run a normal topological sort and call every node in
it safe". That is nearly right, but it silently mishandles nodes *upstream* of a
cycle: they are not in a cycle themselves, so a naive Kahn on the forward graph
would happily emit them, yet they are unsafe because one of their paths falls
into the cycle and never terminates.

In `[[1,2],[2,3],[5],[0],[5],[],[]]`, node 0 sits on the cycle `0 → 1 → 3 → 0`,
so it is unsafe — but so would a hypothetical node pointing only *into* node 0
be, even though it is acyclic itself. Reversing the graph is what makes the
answer propagate in the direction the definition actually runs.

Return order matters: the problem asks for ascending node labels, and a
`range(n)` filter at the end gives that for free rather than sorting the pop
order.
""",
        ),
    ],
}


def eventual_safe_nodes(graph: list[list[int]]) -> list[int]:
    n = len(graph)
    reverse: list[list[int]] = [[] for _ in range(n)]
    outdegree = [0] * n

    for node, successors in enumerate(graph):
        outdegree[node] = len(successors)
        for successor in successors:
            reverse[successor].append(node)

    queue = deque(node for node in range(n) if outdegree[node] == 0)  # terminals
    safe = [False] * n

    while queue:
        node = queue.popleft()
        safe[node] = True
        for predecessor in reverse[node]:
            outdegree[predecessor] -= 1
            if outdegree[predecessor] == 0:  # all its exits are now known safe
                queue.append(predecessor)

    return [node for node in range(n) if safe[node]]


CASES = [
    (([[1, 2], [2, 3], [5], [0], [5], [], []],), [2, 4, 5, 6]),
    (([[1, 2, 3, 4], [1, 2], [3, 4], [0, 4], []],), [4]),
    (([[]],), [0]),
    (([[0]],), []),
    (([[], [0], [1]],), [0, 1, 2]),
    (([[1], [2], [0], []],), [3]),
    (([[1, 2], [3], [3], []],), [0, 1, 2, 3]),
    (([],), []),
]


def solve(graph: list[list[int]]) -> list[int]:
    return eventual_safe_nodes(graph)
