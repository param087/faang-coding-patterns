"""Parallel Courses — LeetCode 1136."""

from __future__ import annotations

from collections import deque

META = {
    "pattern": "topological-sort",
    "insight": "Drain Kahn's queue one whole level per iteration — the number of levels is the number of semesters.",
    "time": "O(V + E)",
    "space": "O(V + E)",
    "sections": [
        (
            "What it asks",
            """
Premium, so described in my own words: `n` courses labelled `1 .. n`, and
`relations[i] = [prev, next]` meaning `prev` must be finished in a **strictly
earlier** semester than `next`. Each semester you may take **any number** of
courses whose prerequisites are all already done. Return the minimum number of
semesters needed to take everything, or `-1` if the prerequisites are
contradictory.

The two facts that shape the code: courses are 1-indexed (so size your arrays
`n + 1` or subtract 1 everywhere — pick one and be consistent), and there is no
cap on courses per semester. A cap turns this into a genuinely hard scheduling
problem; without one, greedy is optimal.
""",
        ),
        (
            "The insight",
            """
"Take everything you can, as early as you can" is optimal here, and it is worth
justifying rather than asserting: delaying an available course can never unlock
anything sooner, and taking it early never blocks anything, because capacity is
unlimited. So the earliest semester for a course is `1 + max(earliest semester
of its prerequisites)` — the longest path from a source, in edges.

That is exactly Kahn's algorithm processed **level by level**. Snapshot
`len(queue)` at the top of each round, pop precisely that many, and everything
newly unlocked lands in the next round. Increment the counter once per round.

The answer is the length of the longest chain of prerequisites, i.e. the depth
of the DAG, and framing it that way is what makes the `-1` case obvious: a cycle
has no finite longest path, Kahn stalls, and `studied < n` catches it.

Two implementation notes:

- `for _ in range(len(queue))` evaluates `len` once, before any pops. Writing
  `while queue:` inside the round instead would consume the *next* level too and
  return 1 for everything.
- The alternative — carry a `semester[node]` array and take
  `semester[next] = max(semester[next], semester[node] + 1)` — is equally
  correct and generalises better to weighted "course takes k semesters"
  variants. The level snapshot is shorter when every course takes one semester.
""",
        ),
        (
            "Edge cases",
            """
- **Cycle** anywhere, including a self-relation `[1, 1]` → `-1`. The `studied ==
  n` check is the only cycle detection in the function.
- **No relations at all** → every course is available immediately, answer `1`,
  not `n`. This is the case that catches anyone who wrote a plain topological
  sort and returned its length.
- **A pure chain** `1 → 2 → 3 → 4` → `4`. Each level holds one course.
- **Duplicate relations** `[[1,2],[1,2]]` push `indegree[2]` to 2 and both
  decrements fire, so nothing breaks.
- **Disconnected components** run in parallel: the answer is the *maximum* depth
  across components, which falls out because all their sources share round 1.
- **1-indexing.** Seeding the queue with `range(1, n + 1)` and not `range(n)` —
  index 0 is a phantom node with indegree 0 that would inflate `studied` by one
  and let a cyclic input return a number instead of `-1`.
""",
        ),
    ],
}


def minimum_semesters(n: int, relations: list[list[int]]) -> int:
    adjacency: list[list[int]] = [[] for _ in range(n + 1)]
    indegree = [0] * (n + 1)

    for previous, following in relations:
        adjacency[previous].append(following)
        indegree[following] += 1

    queue = deque(course for course in range(1, n + 1) if indegree[course] == 0)
    semesters = 0
    studied = 0

    while queue:
        semesters += 1
        for _ in range(len(queue)):  # len() snapshot: exactly this semester's courses
            course = queue.popleft()
            studied += 1
            for unlocked in adjacency[course]:
                indegree[unlocked] -= 1
                if indegree[unlocked] == 0:
                    queue.append(unlocked)

    return semesters if studied == n else -1


CASES = [
    ((3, [[1, 3], [2, 3]]), 2),
    ((3, [[1, 2], [2, 3], [3, 1]]), -1),
    ((1, []), 1),
    ((5, []), 1),
    ((4, [[1, 2], [2, 3], [3, 4]]), 4),
    ((6, [[1, 4], [2, 4], [3, 5], [4, 6], [5, 6]]), 3),
    ((2, [[1, 2], [1, 2]]), 2),
    ((2, [[1, 1]]), -1),
    ((0, []), 0),
]


def solve(n: int, relations: list[list[int]]) -> int:
    return minimum_semesters(n, relations)
