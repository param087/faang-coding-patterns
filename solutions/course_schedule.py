"""Course Schedule — LeetCode 207."""

from __future__ import annotations

from collections import deque

META = {
    "pattern": "topological-sort",
    "insight": "You never need the order, only whether Kahn's queue drains every node — a node left with a positive indegree is a cycle.",
    "time": "O(V + E)",
    "space": "O(V + E)",
    "sections": [
        (
            "What it asks",
            """
`numCourses` courses labelled `0 .. n-1`, and pairs `[a, b]` meaning *b before
a*. Decide whether all courses can be finished — i.e. whether the directed
graph is acyclic.

Ask which way the pair points. `[a, b]` here means the **edge runs b → a**, and
building the adjacency backwards is the single most common way people lose this
one. State your convention out loud before you write the loop.

Also worth asking: can `prerequisites` contain duplicates or self-pairs
(`[0, 0]`)? Both are handled below without special-casing, but say so.
""",
        ),
        (
            "The insight",
            """
Cycle detection *is* topological sorting with the output thrown away.

Kahn's algorithm repeatedly removes a node with indegree 0. That is exactly the
set of courses you could take right now. Removing one decrements its
successors' indegrees, unlocking the next wave. If the queue empties before you
have popped all `n` nodes, whatever is left has every member waiting on another
member of the leftover set — which is precisely a cycle.

So the whole answer is a counter:

```
popped == numCourses
```

The alternative is DFS with three colours (white / grey / black), where hitting
a **grey** node means a back edge, hence a cycle. Both are O(V + E); Kahn wins
in an interview because there is no recursion depth to defend and the same code
becomes Course Schedule II by appending the popped node to a list.

Note what *does not* work: a plain visited set on a DFS. That detects a node you
have seen before, not a node currently on the stack, and it will call the
diamond `0→1→3, 0→2→3` a cycle. The three-state colouring exists for exactly
this reason.
""",
        ),
        (
            "Edge cases",
            """
- **Duplicate edges.** `[[1,0],[1,0]]` pushes 1 into the adjacency twice and
  raises its indegree to 2. Both decrements fire, so it still reaches 0. No
  dedupe needed — but if you switch to `set` adjacency you must guard the
  indegree increment too, or you will orphan a node forever.
- **Self-loop** `[0, 0]`: indegree of 0 never reaches zero, so it never enters
  the queue. Falls out for free.
- **No prerequisites** — every node starts at indegree 0, one pass, `True`.
- **Disconnected components.** Seeding the queue with *every* indegree-0 node
  rather than just node 0 is what makes this work; a cycle hiding in a component
  you never reached would otherwise be missed.
- **n up to 2000, edges up to 5000** — nothing here needs to be clever, but an
  adjacency matrix would be 4·10⁶ cells for a graph with 5000 edges. Use lists.
""",
        ),
    ],
}


def can_finish(num_courses: int, prerequisites: list[list[int]]) -> bool:
    adjacency: list[list[int]] = [[] for _ in range(num_courses)]
    indegree = [0] * num_courses

    for course, prerequisite in prerequisites:  # [a, b] means b -> a
        adjacency[prerequisite].append(course)
        indegree[course] += 1

    queue = deque(node for node in range(num_courses) if indegree[node] == 0)
    taken = 0

    while queue:
        node = queue.popleft()
        taken += 1
        for successor in adjacency[node]:
            indegree[successor] -= 1
            if indegree[successor] == 0:
                queue.append(successor)

    return taken == num_courses  # anything left behind is inside a cycle


CASES = [
    ((2, [[1, 0]]), True),
    ((2, [[1, 0], [0, 1]]), False),
    ((1, []), True),
    ((0, []), True),
    ((2, [[0, 0]]), False),
    ((3, [[1, 0], [1, 0], [2, 1]]), True),
    ((4, [[1, 0], [2, 0], [3, 1], [3, 2]]), True),
    ((5, [[1, 0], [2, 1], [4, 3], [3, 4]]), False),
]


def solve(num_courses: int, prerequisites: list[list[int]]) -> bool:
    return can_finish(num_courses, prerequisites)
