"""Sequence Reconstruction — LeetCode 444."""

from __future__ import annotations

from collections import defaultdict, deque

META = {
    "pattern": "topological-sort",
    "insight": "A topological order is unique exactly when Kahn's queue holds exactly one node at every single step.",
    "time": "O(n + total length of the sequences)",
    "space": "O(n + total length of the sequences)",
    "sections": [
        (
            "What it asks",
            """
This one is premium, so the statement is not public — described in my own
words: you are given `nums`, a permutation of `1 .. n`, and a list of
`sequences`, each a subsequence of that permutation. Decide whether `nums` is
the **only** shortest sequence that contains every one of `sequences` as a
subsequence. Return a boolean.

The reframing that makes it tractable: each `sequences[k]` pins down the
relative order of its consecutive pairs, and nothing else. So the input is a
directed graph, and the question is *"is there exactly one topological order,
and is it `nums`?"*

Two things to confirm before coding: values in `sequences` may fall outside
`1 .. n` (then the answer is `False`), and every value in `1 .. n` must appear
somewhere in `sequences` or it is unconstrained and the order is not unique.
""",
        ),
        (
            "The insight",
            """
Uniqueness of a topological order has a one-line characterisation in Kahn's
algorithm:

> The order is unique iff the ready queue contains **exactly one** node at every
> iteration.

Two nodes ready at once means both could legally come next, so at least two
distinct valid orders exist and the answer is `False` regardless of what `nums`
says. Zero nodes ready before you have emitted all `n` means a cycle.

So you do not compare orders at all — you run Kahn and assert `len(queue) == 1`
each round, then check the single ready node equals the next element of `nums`.
Failing either check short-circuits to `False`.

Equivalently (and this is the O(1)-extra-space answer worth mentioning): `nums`
is the unique reconstruction iff every adjacent pair `nums[i], nums[i+1]`
appears as a *consecutive* pair in some sequence, and every value is covered.
Same fact, phrased as a Hamiltonian path in the DAG: a topological order is
unique exactly when consecutive nodes in it are joined by an edge.

Deduplicating edges matters. `[[1,2],[1,2]]` would otherwise push `indegree[2]`
to 2, only one decrement would fire, and node 2 would never become ready — a
`False` for a perfectly valid input.
""",
        ),
        (
            "Edge cases",
            """
- **A value missing from every sequence.** `nums = [1,2,3]`, `sequences =
  [[1,2]]` → 3 is unconstrained and could go anywhere, so `False`. The
  `len(indegree) != n` guard catches it; forgetting it is the classic bug.
- **Out-of-range values.** A sequence mentioning 4 when `n = 3` makes `nums`
  not a supersequence at all → `False`.
- **A repeated value inside one sequence**, e.g. `[1,1]`, creates the self-loop
  `1 → 1`. Its indegree never reaches 0, the queue starts empty, and the
  `len(queue) != 1` check returns `False` on the first iteration.
- **A cycle across sequences**, `[[1,2],[2,1]]` → the queue empties early,
  `False`.
- **`sequences` containing single-element lists.** They contribute a node but no
  edge. That is exactly how a value gets "covered" without being ordered.
- **Trailing residue.** `return not queue` at the end is not decoration: if
  `nums` is shorter than the node set the loop stops early, and a non-empty
  queue means there was more graph than permutation.
""",
        ),
    ],
}


def sequence_reconstruction(nums: list[int], sequences: list[list[int]]) -> bool:
    n = len(nums)
    adjacency: dict[int, set[int]] = defaultdict(set)
    indegree: dict[int, int] = {}

    for sequence in sequences:
        for value in sequence:
            if not 1 <= value <= n:  # not a subsequence of nums at all
                return False
            indegree.setdefault(value, 0)
        for earlier, later in zip(sequence, sequence[1:], strict=False):
            if later not in adjacency[earlier]:  # dedupe, or indegree over-counts
                adjacency[earlier].add(later)
                indegree[later] += 1

    if len(indegree) != n:  # some value is unconstrained -> not unique
        return False

    queue = deque(value for value, degree in indegree.items() if degree == 0)

    for expected in nums:
        if len(queue) != 1:  # 0 -> cycle, 2+ -> another valid order exists
            return False
        node = queue.popleft()
        if node != expected:
            return False
        for successor in adjacency[node]:
            indegree[successor] -= 1
            if indegree[successor] == 0:
                queue.append(successor)

    return not queue


CASES = [
    (([1, 2, 3], [[1, 2], [1, 3]]), False),
    (([1, 2, 3], [[1, 2]]), False),
    (([1, 2, 3], [[1, 2], [1, 3], [2, 3]]), True),
    (([4, 1, 5, 2, 6, 3], [[5, 2, 6, 3], [4, 1, 5, 2]]), True),
    (([1, 2, 3], [[1, 2], [2, 3], [1, 3], [3, 2]]), False),
    (([1], [[1]]), True),
    (([1], []), False),
    (([2, 1], [[2, 1], [1, 1]]), False),
    (([], []), True),
]


def solve(nums: list[int], sequences: list[list[int]]) -> bool:
    return sequence_reconstruction(nums, sequences)
