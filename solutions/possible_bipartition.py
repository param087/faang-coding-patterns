"""Possible Bipartition — LeetCode 886."""

from __future__ import annotations

from collections import deque

META = {
    "pattern": "advanced-graphs",
    "insight": "Two groups means two colours, so the question is only whether the dislike graph contains an odd cycle.",
    "time": "O(n + e)",
    "space": "O(n + e)",
    "sections": [
        (
            "What it asks",
            """
`n` people, numbered 1..n, and a list of mutually-disliking pairs. Split
everyone into **two** groups so that no disliking pair shares a group. Return
whether that is possible.

The clarifying question worth asking: **must both groups be non-empty, and must
the split be balanced?** Neither — which is what makes this pure feasibility
rather than an optimisation. If someone dislikes nobody they can go anywhere.

Restated: colour the "dislike" graph with two colours. That is a bipartiteness
test, and a graph is bipartite exactly when it has **no odd-length cycle**.
""",
        ),
        (
            "The insight",
            """
Once you pick a colour for one person, every neighbour is forced, and every
neighbour of a neighbour is forced, all the way out. So there is no search
here — no backtracking, no trying both assignments. A single BFS or DFS per
component either propagates cleanly or hits a contradiction, and the
contradiction is always the same shape: an edge whose two ends already carry
the same colour.

That edge closes a cycle of even length in the BFS tree plus one, i.e. an odd
cycle. `[[1,2],[2,3],[1,3]]` is the smallest instance and the one to reach for
when an interviewer asks why two colours can fail.

Union-find is the other accepted answer: union each person with the *enemies*
of their enemies, and fail if a person ever lands in the same set as someone
they dislike. It is a fine variation to mention, but colouring is shorter to
write and it hands you the actual groups for free, which the follow-up usually
wants.
""",
        ),
        (
            "Edge cases",
            """
- **The graph is not connected.** This is the single most common bug: colouring
  from person 1 only and returning `True`. You must loop over every uncoloured
  person as a fresh BFS root. `n = 6` with dislikes `[[1,2],[2,3],[1,3]]` and
  `[[4,5]]` is impossible, and a one-root solution says it is fine.
- **Isolated people.** Never enter a queue as a neighbour, so the outer loop
  has to reach them; harmless, but the loop must not crash on an empty
  adjacency list.
- **Use 0 as "uncoloured" and ±1 as the colours.** With a boolean visited array
  plus a boolean colour array you carry two arrays and two bugs; one integer
  array where `colour[v] = -colour[u]` collapses it.
- **Even cycles are fine.** A 6-cycle of dislikes is bipartite. Anyone who
  answers "any cycle fails" has not tested this.
- **Duplicate or self pairs.** LeetCode excludes them; a self-dislike would be
  an instant `False`, and it costs one line to say so.
""",
        ),
    ],
}


def possible_bipartition(n: int, dislikes: list[list[int]]) -> bool:
    adjacency: list[list[int]] = [[] for _ in range(n + 1)]
    for a, b in dislikes:
        adjacency[a].append(b)
        adjacency[b].append(a)

    colour = [0] * (n + 1)  # 0 = unassigned, +1 / -1 = the two groups

    for start in range(1, n + 1):
        if colour[start]:
            continue  # already settled by an earlier component

        colour[start] = 1
        queue = deque([start])
        while queue:
            person = queue.popleft()
            for enemy in adjacency[person]:
                if colour[enemy] == colour[person]:
                    return False  # an odd cycle closes here
                if not colour[enemy]:
                    colour[enemy] = -colour[person]
                    queue.append(enemy)

    return True


CASES = [
    ((4, [[1, 2], [1, 3], [2, 4]]), True),
    # Triangle: the smallest odd cycle.
    ((3, [[1, 2], [1, 3], [2, 3]]), False),
    # Odd cycle of length 5.
    ((5, [[1, 2], [2, 3], [3, 4], [4, 5], [1, 5]]), False),
    # Even cycle of length 6 — bipartite, so "any cycle fails" is wrong.
    ((6, [[1, 2], [2, 3], [3, 4], [4, 5], [5, 6], [1, 6]]), True),
    # The bad component is not the one containing person 1.
    ((6, [[1, 2], [3, 4], [4, 5], [5, 3]]), False),
    # Disconnected and fine, including person 5 who dislikes nobody.
    ((5, [[1, 2], [3, 4]]), True),
    ((1, []), True),
    ((4, []), True),
]


def solve(n: int, dislikes: list[list[int]]) -> bool:
    return possible_bipartition(n, dislikes)
