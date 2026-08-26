"""Maximum Employees to Be Invited to a Meeting — LeetCode 2127."""

from __future__ import annotations

from collections import deque

META = {
    "pattern": "advanced-graphs",
    "insight": "The table holds either one long cycle, or every mutual pair at once with a chain trailing off each — so take the larger.",
    "time": "O(n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Each employee has exactly one favourite (never themselves). Seat people at
**one round table** so that every seated person sits next to their favourite.
Return the largest number seatable.

"Next to" means adjacent on either side, and that is the hinge of the whole
problem. Restate it as a graph: `n` nodes, each with exactly one outgoing edge —
a **functional graph**, which decomposes into disjoint cycles with trees hanging
off them, nothing else.

A seating is a circular arrangement in which everyone's favourite is one of
their two neighbours. Two structures satisfy that, and they behave completely
differently.
""",
        ),
        (
            "The insight",
            """
**Structure one: a cycle of length ≥ 3.** Seat the cycle in order and everyone
faces their favourite. Nothing else can join — every seat is already taken by
someone whose favourite is the next person along. So one such cycle gives
exactly its own length, and cycles cannot be combined at one table.

**Structure two: a mutual pair, a cycle of length 2.** `a` likes `b`, `b` likes
`a`. Seat them adjacent, and now the two directions of the table are free: to
`a`'s other side you can attach a chain of people each of whom likes the next
one towards `a`, and the same past `b`. Both are satisfied because their
favourite is on the inward side.

And here is the part that decides the problem: **several mutual pairs, each with
its chains, all fit at the same table.** Each pair-plus-chains is a segment
whose two ends have no requirement facing outward, so segments can be laid
end to end around the circle. They **add up**.

So the answer is `max(longest cycle of length ≥ 3, total of every 2-cycle plus
its two longest chains)`. Both branches must be computed; whichever is larger
wins. `favourite = [1,0,3,2,5,4]` — three mutual pairs — answers **6**, and any
solution that returns only the longest cycle answers 2.

Mechanically: peel the trees off with Kahn's algorithm, recording for each node
the longest chain ending at it. Whatever survives with in-degree left over is
exactly the set of cycle nodes; walk each cycle once and classify by length.
Every node is touched a constant number of times → O(n).
""",
        ),
        (
            "Pitfalls",
            """
- **Chains only count for 2-cycles.** Attaching a tail to a longer cycle would
  seat someone whose favourite is already flanked. Adding tails to every cycle
  is the most common wrong answer and it passes the first sample.
- **Longest chain, not chain count.** A node may have several trees feeding it;
  only the deepest path can be seated in a line. Kahn's peel with
  `depth[next] = max(depth[next], depth[node] + 1)` gets this for free — a
  plain node count does not.
- **Do not double-count the pair.** `depth` initialised to 1 already counts the
  node itself, so `depth[a] + depth[b]` covers both seats plus both chains.
- **Take the max, do not add the branches.** A 5-cycle and a mutual pair are
  separate tables; you may only run one meeting.
- **Iterative only.** `n` reaches `10⁵`; Kahn's is a queue, and the cycle walk
  is a `while`, so nothing here recurses.
""",
        ),
    ],
}


def maximum_invitations(favourite: list[int]) -> int:
    n = len(favourite)

    in_degree = [0] * n
    for liked in favourite:
        in_degree[liked] += 1

    # Kahn's peel: strip the trees, keeping the longest chain ending at each node.
    depth = [1] * n
    settled = [False] * n
    queue = deque(node for node in range(n) if in_degree[node] == 0)
    while queue:
        node = queue.popleft()
        settled[node] = True
        liked = favourite[node]
        depth[liked] = max(depth[liked], depth[node] + 1)
        in_degree[liked] -= 1
        if in_degree[liked] == 0:
            queue.append(liked)

    longest_cycle = 0
    mutual_pairs_total = 0
    for node in range(n):
        if settled[node]:
            continue

        length = 0
        walker = node
        while not settled[walker]:  # every survivor lies on a cycle
            settled[walker] = True
            length += 1
            walker = favourite[walker]

        if length == 2:
            mutual_pairs_total += depth[node] + depth[favourite[node]]
        else:
            longest_cycle = max(longest_cycle, length)

    return max(longest_cycle, mutual_pairs_total)


CASES = [
    (([2, 2, 1, 2],), 3),
    (([1, 2, 0],), 3),
    (([3, 0, 1, 4, 1],), 4),
    # Three mutual pairs seat everybody: the branch that "longest cycle" misses.
    (([1, 0, 3, 2, 5, 4],), 6),
    (([1, 0],), 2),
    # One mutual pair with a two-person chain feeding it.
    (([1, 0, 0, 2, 2],), 4),
    # A 5-cycle beats a mutual pair carrying a chain of total 4.
    (([1, 0, 0, 2, 5, 6, 7, 8, 4],), 5),
    # A 3-cycle with a tail: the tail cannot be seated.
    (([2, 0, 1, 0],), 3),
]


def solve(favourite: list[int]) -> int:
    return maximum_invitations(favourite)
