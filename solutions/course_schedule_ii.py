"""Course Schedule II — LeetCode 210."""

from __future__ import annotations

from collections import deque

META = {
    "pattern": "topological-sort",
    "insight": "Kahn's algorithm gives the ordering and the cycle check at once — a short output means the leftovers are in a cycle.",
    "time": "O(V + E)",
    "space": "O(V + E)",
    "sections": [
        (
            "What it asks",
            """
Given `numCourses` and prerequisite pairs, return an order in which every
course can be taken, or an empty list if impossible.

**Ask about the direction of the pair.** LeetCode's `[a, b]` means "take b
**before** a", which is an edge **b → a**. The naming is genuinely ambiguous
and reversing it produces a valid-looking answer to the wrong question. Also
ask: any valid order or a specific one; what should an impossible schedule
return.
""",
        ),
        (
            "The insight",
            """
Prerequisites form a directed graph. A valid schedule is a **topological
order**, and "impossible" means the graph has a cycle.

Kahn's algorithm gives both at once: start with everything that has no
prerequisite, and each time a course is emitted, decrement its dependants —
any that reach zero are now ready.
""",
        ),
        (
            "The cycle check is free",
            """
This is the elegant part. If fewer than `n` courses came out, the leftovers
must be in a cycle — a node inside a cycle can never reach indegree zero,
because something in the cycle always still points at it.

So one `len(order) == n` comparison replaces an entire separate
cycle-detection pass. That comparison alone is the whole of Course Schedule I.
""",
        ),
        (
            "Dry run",
            """
`n = 4`, prerequisites `[[1,0],[2,0],[3,1],[3,2]]` — so edges 0→1, 0→2, 1→3,
2→3.

Indegrees: 0 has none. Emit 0 → 1 and 2 both drop to zero. Emit 1 and 2 in
either order → 3 drops to zero. Emit 3.

Order `[0,1,2,3]` or `[0,2,1,3]` — **both correct**. Flag that two valid
answers exist; interviewers sometimes have one in mind.

Then run the cycle case `[[1,0],[0,1]]`: neither node ever reaches indegree
zero, the output is short, return `[]`.
""",
        ),
        (
            "Follow-ups",
            """
- **Lexicographically smallest valid order** — swap the deque for a heap.
  O((V + E) log V).
- **Alien Dictionary** — the same sort, but two thirds of the problem is
  *building* the graph from adjacent words.
- **Parallel Courses** — the answer is the number of BFS levels, i.e. the
  longest path in the DAG.
- **The DFS alternative** — three-colour marking, where meeting a node on the
  current path is a cycle. Reverse the finish order for the topological sort.
  Kahn is easier to get right under pressure.
""",
        ),
    ],
}


def find_order(num_courses: int, prerequisites: list[list[int]]) -> list[int]:
    adjacency: list[list[int]] = [[] for _ in range(num_courses)]
    indegree = [0] * num_courses

    # [a, b] means "take b before a", i.e. an edge b -> a.
    for after, before in prerequisites:
        adjacency[before].append(after)
        indegree[after] += 1

    queue = deque(course for course in range(num_courses) if indegree[course] == 0)
    order: list[int] = []

    while queue:
        course = queue.popleft()
        order.append(course)
        for dependant in adjacency[course]:
            indegree[dependant] -= 1
            if indegree[dependant] == 0:
                queue.append(dependant)

    # Short output means some course never reached indegree 0 — a cycle.
    return order if len(order) == num_courses else []


CASES = [
    ((2, [[1, 0]]), [0, 1]),
    ((1, []), [0]),
    ((2, [[1, 0], [0, 1]]), []),
    ((4, [[1, 0], [2, 0], [3, 1], [3, 2]]), [0, 1, 2, 3]),
    ((3, [[1, 0], [2, 1]]), [0, 1, 2]),
]


def solve(num_courses: int, prerequisites: list[list[int]]) -> list[int]:
    return find_order(num_courses, prerequisites)
