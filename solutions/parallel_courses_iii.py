"""Parallel Courses III — LeetCode 2050."""

from __future__ import annotations

from collections import deque

META = {
    "pattern": "topological-sort",
    "insight": "A course finishes at its own duration plus the latest of its prerequisites' finishes — longest path in a DAG, relaxed in Kahn order.",
    "time": "O(V + E)",
    "space": "O(V + E)",
    "sections": [
        (
            "What it asks",
            """
`n` courses, each with a duration in `time`, and `relations[i] = [prev, next]`
meaning `prev` must finish before `next` starts. Unlimited courses may run
**in parallel**. Return the minimum months to finish everything.

The clarifying question that matters: **is there any cap on concurrency?**
There is not — and that single fact is what turns a scheduling problem into a
one-pass DAG relaxation. If an interviewer caps it at `k` workers, the problem
becomes NP-hard job-shop scheduling and you switch to a greedy heuristic; say
so, it scores.

Also confirm the graph is acyclic. LeetCode guarantees it; Kahn tells you
anyway if the emitted count falls short of `n`.
""",
        ),
        (
            "The insight",
            """
Because everything runnable runs at once, a course starts the instant its
**slowest** prerequisite finishes. So

```
finish[v] = time[v] + max(finish[u] for u -> v)      (0 if v has no prereqs)
```

and the answer is `max(finish)`. That recurrence is only valid once every
predecessor of `v` is already final — which is exactly what a topological
order guarantees. Run Kahn's algorithm and relax each edge as you pop its
source: by the time `v` reaches indegree zero, every `u -> v` has already
pushed its value into `finish[v]`.

No heap, no repeated relaxation, no visited set. One pass, O(V + E).
""",
        ),
        (
            "Not the sum, and not the edge count",
            """
Two wrong first answers, both common:

- **`sum(time)`** — that is the serial schedule. With `n = 3`, no relations,
  `time = [3, 1, 2]`, the sum says 6 and the answer is **3**: they all run at
  once.
- **"find the path with the most courses"** — longest *by edge count* is not
  longest *by weight*. Take `n = 4`, relations `[[1,4],[2,3],[3,4]]`,
  `time = [10,1,1,1]`. The three-node chain 2→3→4 totals 3 months; the
  single-edge path 1→4 totals **11**. The answer is 11, from the shorter path.

The third trap is initialising `finish[v] = time[v]` only when you first touch
`v`, then overwriting rather than taking a `max` — that keeps the *last*
prerequisite seen instead of the latest-finishing one. Use `max`, always.
""",
        ),
    ],
}


def minimum_time(n: int, relations: list[list[int]], time: list[int]) -> int:
    adjacency: list[list[int]] = [[] for _ in range(n + 1)]  # 1-indexed courses
    indegree = [0] * (n + 1)

    for previous, following in relations:
        adjacency[previous].append(following)
        indegree[following] += 1

    # finish[v] is final only once every predecessor has been popped.
    finish = [0] * (n + 1)
    queue: deque[int] = deque()
    for course in range(1, n + 1):
        if indegree[course] == 0:
            finish[course] = time[course - 1]
            queue.append(course)

    while queue:
        course = queue.popleft()
        for dependant in adjacency[course]:
            # Relax: the dependant cannot start before this prerequisite ends.
            finish[dependant] = max(finish[dependant], finish[course] + time[dependant - 1])
            indegree[dependant] -= 1
            if indegree[dependant] == 0:
                queue.append(dependant)

    return max(finish)


CASES = [
    ((3, [[1, 3], [2, 3]], [3, 2, 5]), 8),
    ((5, [[1, 5], [2, 5], [3, 5], [3, 4], [4, 5]], [1, 2, 3, 4, 5]), 12),
    ((1, [], [7]), 7),
    ((3, [], [3, 1, 2]), 3),  # fully parallel — breaks sum(time)
    ((4, [[1, 2], [2, 3], [3, 4]], [1, 1, 1, 1]), 4),  # pure chain — breaks max(time)
    ((4, [[1, 4], [2, 3], [3, 4]], [10, 1, 1, 1]), 11),  # breaks longest-by-edge-count
    ((4, [[1, 2], [1, 3], [2, 4], [3, 4]], [1, 5, 2, 1]), 7),  # diamond, uneven branches
]


def solve(n: int, relations: list[list[int]], time: list[int]) -> int:
    return minimum_time(n, relations, time)
