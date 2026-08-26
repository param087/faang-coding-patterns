"""Maximum Number of Accepted Invitations — LeetCode 1820."""

from __future__ import annotations

META = {
    "pattern": "advanced-graphs",
    "insight": "Greedy pairing stalls; let a blocked boy bump an already-matched one along an augmenting path and it never stalls.",
    "time": "O(m²·n) — one DFS per boy, each touching at most m·n edges",
    "space": "O(m + n)",
    "sections": [
        (
            "What it asks",
            """
This one is premium, so the statement is not public — described here in my own
words. You are given an `m × n` 0/1 grid: `grid[i][j] == 1` means boy `i` is
willing to invite girl `j`. Every boy sends at most one invitation and every
girl accepts at most one. Return the largest number of invitations that can be
accepted at once.

Strip the story and it is **maximum bipartite matching**, stated in adjacency
matrix form. Say that sentence in the interview — the whole question is whether
you recognise it, and the constraints (`m, n ≤ 200`) tell you an O(V·E)
algorithm is expected rather than anything clever.

Worth asking: can a boy invite the same girl twice (no, the grid is 0/1)? Is
the answer the count or the actual pairing (count — but the code produces the
pairing anyway, so offer it).
""",
        ),
        (
            "The insight",
            """
The tempting answer is greedy: walk the boys in order, give each the first free
girl he likes. It is wrong, and the counterexample is two rows:

```
1 1
1 0
```

Greedy gives boy 0 girl 0, then boy 1 is stuck — **1 invitation**. The right
answer is 2: boy 0 takes girl 1 and leaves girl 0 for boy 1. Greedy has no way
back once it has committed.

**Kuhn's algorithm** supplies the way back. When boy `b` finds every girl he
likes already taken, he does not give up — he asks each of those girls' current
partners to move elsewhere, recursively. If that recursion bottoms out at a
free girl, the whole chain shifts by one and the matching grows by exactly one.
That chain is an **augmenting path**: it alternates unmatched/matched edges and
ends free at both ends.

The theorem underneath (Berge): a matching is maximum **iff** no augmenting
path exists. So run one DFS per boy; every DFS either grows the matching by one
or proves this boy can never be matched, and neither outcome is ever revisited.
The number of successful DFS calls is the answer.

Store the matching girl-side (`match_of_girl[g] = b`). That is what makes the
recursive "who currently has you, and can he move?" step a single lookup.
""",
        ),
        (
            "The two bugs that sink it",
            """
**1. `seen` is scoped to one DFS, not to the whole run.** It must be created
fresh for each boy and shared across the whole recursion for that boy. Hoist it
outside the loop and later boys are forbidden from touching girls that earlier
augmenting paths merely *considered*, and you silently under-count. Create it
per recursive call instead and the DFS can loop forever between two girls who
keep passing the request back and forth.

**2. Marking the girl before the recursive call.** `seen.add(girl)` has to
happen *before* recursing into `try_assign(match_of_girl[girl], seen)`,
otherwise that subtree can walk straight back into the girl you came from. And
do **not** un-mark on failure: within a single DFS, a girl who could not yield
once will not yield the second time either, and un-marking turns O(m·n) per
boy into exponential backtracking.

Complexity, since it always gets asked: at most `m` DFS calls, each visiting
every edge at most once → **O(m²·n)**. At `m = n = 200` that is 8·10⁶ — well
inside limits, which is the signal that Kuhn's is the intended answer and
Hopcroft–Karp's O(E·√V) is over-engineering here.
""",
        ),
    ],
}


def maximum_invitations(grid: list[list[int]]) -> int:
    boys = len(grid)
    girls = len(grid[0]) if boys else 0
    match_of_girl: list[int] = [-1] * girls  # girl -> boy, or -1 if free

    def try_assign(boy: int, seen: set[int]) -> bool:
        for girl in range(girls):
            if not grid[boy][girl] or girl in seen:
                continue
            seen.add(girl)  # before recursing, or the path walks back here
            # Free girl, or her current partner can be pushed somewhere else.
            if match_of_girl[girl] == -1 or try_assign(match_of_girl[girl], seen):
                match_of_girl[girl] = boy
                return True
        return False

    # One augmenting-path search per boy; each success grows the matching by 1.
    return sum(try_assign(boy, set()) for boy in range(boys))


CASES = [
    (([[1, 1, 1], [1, 0, 1], [0, 0, 1]],), 3),
    (([[1, 0, 1, 0], [1, 0, 0, 0], [0, 0, 1, 0], [1, 1, 1, 0]],), 3),
    # Greedy in row order answers 1 here; the augmenting path finds 2.
    (([[1, 1], [1, 0]],), 2),
    # A four-long augmenting chain: every boy has to shift one girl along.
    (([[1, 1, 0, 0], [1, 0, 0, 0], [0, 1, 1, 0], [0, 0, 1, 1]],), 4),
    (([[1, 1], [1, 1], [1, 1]],), 2),
    (([[0, 0], [0, 0]],), 0),
    (([[1]],), 1),
    (([],), 0),
]


def solve(grid: list[list[int]]) -> int:
    return maximum_invitations([row[:] for row in grid])
