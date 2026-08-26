"""Course Schedule IV — LeetCode 1462."""

from __future__ import annotations

from collections import deque

META = {
    "pattern": "topological-sort",
    "insight": "Propagate an ancestor set along Kahn's order: a node inherits every ancestor of every predecessor, plus the predecessors themselves.",
    "time": "O(V·E / 64 + Q) with bitmask sets",
    "space": "O(V² / 64 + E)",
    "sections": [
        (
            "What it asks",
            """
Given `numCourses`, a list of direct prerequisite pairs `[before, after]`, and
a batch of queries `[u, v]`, answer for each query whether `u` is a
prerequisite of `v` — **directly or transitively**. Return one boolean per
query, in order.

Two things to pin down before writing code. First, the pair direction:
`[a, b]` here means "a before b", an edge **a → b** — the opposite convention
to Course Schedule I/II, and getting it backwards produces a plausible wrong
answer. Second, **is a course a prerequisite of itself?** No: `[0, 0]` is
`false`. That falls out for free below, but only if you never seed a node with
its own bit.

The queries arriving as a *batch* is the whole design signal: precompute
reachability once, then answer each query in O(1). `n ≤ 100` and up to 10⁴
queries — a BFS per query would be 10⁴ · 10⁴ edge visits for nothing.
""",
        ),
        (
            "The insight",
            """
Reachability composes along a topological order. Define `ancestors[v]` as the
set of courses that must be taken before `v`. Then for every edge `u → v`:

```
ancestors[v] |= ancestors[u] | {u}
```

That is correct **only if `ancestors[u]` is already complete** when the edge is
relaxed — which is precisely what popping `u` from Kahn's queue guarantees:
every predecessor of `u` has already pushed into it. So one pass over the DAG
computes full transitive closure, and each query is a set membership test.

Store the sets as **Python ints used as bitmasks**. `ancestors[v] |=
ancestors[u] | (1 << u)` is one machine-word-parallel operation per edge
(64 courses at a time), and the query is `ancestors[v] >> u & 1`. With
`n ≤ 100` that is two words — effectively free — and it beats a `set` of ints
by a wide margin on both time and allocation.
""",
        ),
        (
            "Edge cases",
            """
- **Self query `[u, u]`** — false. It stays false because a node is seeded
  empty and only ever receives *predecessors'* bits, never its own. A DFS that
  writes `reach[u].add(u)` as a base case gets this wrong.
- **No prerequisites at all** — every query is false; the queue starts with
  every course and no edge is ever relaxed.
- **A cycle**, if the guarantee is dropped. Kahn stalls: nodes inside the cycle
  never reach indegree zero, so their ancestor sets stay incomplete and answers
  silently degrade. Guard with a popped-count check and decide with the
  interviewer what a cyclic prerequisite graph should even mean.
- **Duplicate edges** — harmless. The indegree counts them and the relaxation
  decrements once per copy, so the bookkeeping stays balanced; the `|=` is
  idempotent.

The alternative worth naming: **Floyd–Warshall** on a boolean matrix, three
nested loops, `reach[i][j] |= reach[i][k] and reach[k][j]`. At `n = 100` that
is 10⁶ operations — perfectly fine here, no topological order needed, and it
survives cycles. It is the answer to give if the graph is *not* guaranteed
acyclic; Kahn plus bitmasks is the answer if it is.
""",
        ),
    ],
}


def check_if_prerequisite(
    num_courses: int,
    prerequisites: list[list[int]],
    queries: list[list[int]],
) -> list[bool]:
    adjacency: list[list[int]] = [[] for _ in range(num_courses)]
    indegree = [0] * num_courses

    # [a, b] means a is a direct prerequisite of b — an edge a -> b.
    for before, after in prerequisites:
        adjacency[before].append(after)
        indegree[after] += 1

    ancestors = [0] * num_courses  # bitmask; no node ever holds its own bit
    queue = deque(course for course in range(num_courses) if indegree[course] == 0)

    while queue:
        course = queue.popleft()  # ancestors[course] is final now
        for dependant in adjacency[course]:
            ancestors[dependant] |= ancestors[course] | (1 << course)
            indegree[dependant] -= 1
            if indegree[dependant] == 0:
                queue.append(dependant)

    return [bool(ancestors[after] >> before & 1) for before, after in queries]


CASES = [
    ((2, [[1, 0]], [[0, 1], [1, 0]]), [False, True]),
    ((2, [], [[1, 0], [0, 1]]), [False, False]),
    ((3, [[1, 2], [1, 0], [2, 0]], [[1, 0], [1, 2]]), [True, True]),
    (
        (5, [[0, 1], [1, 2], [2, 3], [3, 4]], [[0, 4], [4, 0], [0, 0], [2, 4]]),
        [True, False, False, True],  # transitive, reverse, self, mid-chain
    ),
    (
        (4, [[0, 1], [0, 2], [1, 3], [2, 3]], [[0, 3], [1, 2], [2, 1], [3, 0]]),
        [True, False, False, False],  # diamond: siblings are unrelated
    ),
    ((1, [], [[0, 0]]), [False]),
]


def solve(
    num_courses: int,
    prerequisites: list[list[int]],
    queries: list[list[int]],
) -> list[bool]:
    return check_if_prerequisite(num_courses, prerequisites, queries)
