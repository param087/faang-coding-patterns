"""Find the Celebrity — LeetCode 277."""

from __future__ import annotations

from collections.abc import Callable

META = {
    "pattern": "advanced-graphs",
    "insight": "Every knows(a, b) call eliminates somebody for good, so n-1 calls leave exactly one candidate to verify.",
    "time": "O(n) — at most 3(n − 1) API calls",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
*This one is premium, so the statement is paraphrased rather than quoted.*

There are `n` people at a party. A **celebrity** is someone whom everybody else
knows and who knows nobody else. At most one such person can exist. You cannot
see the guest list; you can only ask an oracle `knows(a, b)` — "does a know b?"
— which costs one call. Return the celebrity's index, or `-1`.

This is a directed graph you are only allowed to probe one edge at a time. The
celebrity is the vertex with in-degree `n − 1` and out-degree `0`. Reading the
whole adjacency matrix is `n²` calls; the interview is about beating that.

Ask whether `knows(i, i)` is meaningful — it is not, and the loop should never
ask it.
""",
        ),
        (
            "The insight",
            """
A single call is worth more than it looks, because **each answer eliminates
someone permanently**:

- `knows(a, b)` is **true** → `a` knows someone else, so `a` is not the
  celebrity.
- `knows(a, b)` is **false** → `b` is not known by everyone, so `b` is not the
  celebrity.

Either way exactly one person dies. So sweep once: hold a `candidate`, ask
about each new person `i`, and move the candidate to `i` when the candidate
knows `i`. After `n − 1` calls, `n − 1` people have been eliminated and one
person remains.

That survivor is only a candidate. The sweep proves "nobody else can be the
celebrity"; it does not prove this one *is*. The eliminations before the
candidate changed hands say nothing about the new candidate's own edges, so
**verify** with a second pass: the candidate must know nobody and be known by
everybody. Two more calls per person, `3(n − 1)` in total, and a linear-time
answer to a problem that looks quadratic.

Skipping the verification pass is the single most common failure here — it
returns a person on `[[1,1,0,0],[0,1,0,0],[0,1,1,0],[0,0,0,1]]`, where the
sweep settles on 1 and person 3 has never heard of them.
""",
        ),
        (
            "Follow-ups",
            """
- **"Fewer calls?"** The known bound is `3n − ⌊log₂ n⌋ − 3`. Cache what the
  sweep already learned: when the candidate changes at step `i`, you know the
  old candidate knew `i`, which is half of `i`'s verification; a tournament that
  records the outcomes shaves the logarithmic term. Worth naming, not worth
  coding unless asked.
- **"Prove at most one celebrity exists."** If `x` and `y` both qualify, `x`
  knows nobody, yet `y` must be known by everybody including `x`. Contradiction.
  Interviewers like that this takes one line.
- **"What if the celebrity may not exist?"** Already handled — that is exactly
  what the verification pass is for, and it is why you cannot return early.
- **Related shape:** given the full matrix instead of an oracle, the same sweep
  is *Find the Town Judge* (LC 997) and degree counting solves it in one pass.
""",
        ),
    ],
}


def find_celebrity(n: int, knows: Callable[[int, int], bool]) -> int:
    candidate = 0
    for person in range(1, n):
        if knows(candidate, person):
            candidate = person  # the old candidate knows someone: eliminated

    # The sweep only narrows. Confirm the survivor really qualifies.
    for person in range(n):
        if person == candidate:
            continue
        if knows(candidate, person) or not knows(person, candidate):
            return -1

    return candidate


class _Oracle:
    """Wraps a matrix as the `knows` API and counts how often it is asked."""

    def __init__(self, matrix: list[list[int]]) -> None:
        self.matrix = matrix
        self.calls = 0

    def __call__(self, a: int, b: int) -> bool:
        self.calls += 1
        return bool(self.matrix[a][b])


CASES = [
    (([[1, 1, 0], [0, 1, 0], [1, 1, 1]],), 1),
    # A cycle of acquaintance: nobody qualifies.
    (([[1, 0, 1], [1, 1, 0], [0, 1, 1]],), -1),
    (([[1]],), 0),
    (([[1, 0], [1, 1]],), 0),
    (([[1, 1], [0, 1]],), 1),
    # Mutual, so both are eliminated.
    (([[1, 1], [1, 1]],), -1),
    # Nobody knows anybody: the sweep never moves and verification must reject.
    (([[1, 0, 0], [0, 1, 0], [0, 0, 1]],), -1),
    # The sweep settles on 1, but person 3 does not know them.
    (([[1, 1, 0, 0], [0, 1, 0, 0], [0, 1, 1, 0], [0, 0, 0, 1]],), -1),
]


def solve(matrix: list[list[int]]) -> int:
    return find_celebrity(len(matrix), _Oracle(matrix))


def check() -> None:
    for args, expected in CASES:
        assert solve(*args) == expected, args

    # The point of the problem: linear in API calls, never n².
    for (matrix,), _expected in CASES:
        oracle = _Oracle(matrix)
        find_celebrity(len(matrix), oracle)
        assert oracle.calls <= 3 * (len(matrix) - 1), (matrix, oracle.calls)

    # Brute force over the definition, as a cross-check of every expected value.
    for (matrix,), expected in CASES:
        n = len(matrix)
        answer = -1
        for person in range(n):
            others = [i for i in range(n) if i != person]
            if all(not matrix[person][i] and matrix[i][person] for i in others):
                answer = person
        assert answer == expected, (matrix, answer, expected)
