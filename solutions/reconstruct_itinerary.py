"""Reconstruct Itinerary — LeetCode 332."""

from __future__ import annotations

from collections import defaultdict

META = {
    "pattern": "advanced-graphs",
    "insight": "Hierholzer: walk greedily until stuck, and the airport you get stuck at is the last one on the route, not a mistake to undo.",
    "time": "O(e log e) — the sort dominates",
    "space": "O(e)",
    "sections": [
        (
            "What it asks",
            """
Tickets `[from, to]`, all of which must be used **exactly once**, starting at
`JFK`. Return the itinerary; if several are valid, the one that is smallest as
a list of airport codes read left to right.

The two things to establish first:

- **A ticket is not an airport pair, it is a ticket.** Duplicates are allowed
  and both must be flown. Anything set-based is wrong immediately.
- **A valid itinerary is guaranteed to exist.** That is the whole problem: you
  are being handed an **Eulerian path** — use every *edge* once, not every
  vertex — and told it exists. You never have to detect infeasibility.

"Smallest lexicographically" only breaks ties, so the algorithm must produce a
valid path first and be greedy second.
""",
        ),
        (
            "Brute force, and why it is a trap",
            """
Backtracking: at each airport try each unused outgoing ticket in alphabetical
order, and the first complete itinerary you finish is the answer. With `k`
tickets out of one airport that is up to `k!` orderings — **10 tickets out of
JFK alone is 3.6 million** branches before you have left the city, and LeetCode
allows 300 tickets.

It passes the judge, which is why so many people carry it into an interview. It
is still the wrong answer, because a linear algorithm exists and the question is
plainly asking for it.
""",
        ),
        (
            "Why plain greedy fails",
            """
The obvious fix — always take the alphabetically smallest unused ticket, no
backtracking — is wrong, and this is the counterexample to have ready:

```
[["JFK","KUL"], ["JFK","NRT"], ["NRT","JFK"]]
```

Greedy flies `JFK → KUL` because `KUL < NRT`, and now sits in Kuala Lumpur with
two unused tickets. The correct itinerary is `JFK → NRT → JFK → KUL`.

`KUL` has no outgoing ticket, so it *must* be the final airport. Getting stuck
there is not an error — it is information.
""",
        ),
        (
            "The insight: Hierholzer, post-order",
            """
Walk greedily and never undo anything. When you reach an airport with no unused
outgoing tickets, that airport is **finished**: append it to the output and step
back to the previous airport, which may still have tickets left and will start a
side-loop from there. Reverse the output at the end.

Why it works: the input is guaranteed Eulerian, and in an Eulerian graph the
only vertex where you can strand yourself is the required endpoint (every other
vertex has matching in- and out-degree, so any entry has a matching exit). Every
detour you failed to take is a **closed loop** hanging off the path, and popping
back and walking it splices that loop into the route at exactly the right place.

The lexicographic requirement is then free: keep each airport's destinations
sorted, always take the smallest remaining one. Below, the list is built in
*descending* order so `pop()` off the end takes the alphabetically smallest in
O(1).

Every ticket is pushed and popped once → **O(e)** after the O(e log e) sort.
""",
        ),
        (
            "Dry run",
            """
`[["JFK","KUL"], ["JFK","NRT"], ["NRT","JFK"]]`, so `JFK → [NRT, KUL]`
(descending; `pop()` yields `KUL` first) and `NRT → [JFK]`.

- Descend: `JFK`, pop `KUL`. `KUL` has nothing → **route = [KUL]**, step back.
- `JFK` still has `NRT` → descend to `NRT`, which has `JFK` → descend to `JFK`,
  now empty → route = `[KUL, JFK]`.
- Unwind: `NRT`, then the first `JFK` → route = `[KUL, JFK, NRT, JFK]`.
- Reverse → `JFK, NRT, JFK, KUL`. ✅

`KUL` was appended first and therefore lands last. That single fact is the
algorithm.
""",
        ),
        (
            "Follow-ups",
            """
- **"What if no valid itinerary exists?"** Then verify Eulerian conditions
  first: at most one vertex with `out − in = 1` (the start), at most one with
  `in − out = 1`, all others balanced, and all edges in one connected component.
  That is *Valid Arrangement of Pairs* (LC 2097), where the start is computed
  rather than given as `JFK`.
- **Undirected version** (LC 2097's cousin, or "Eulerian circuit on an
  undirected graph"): every vertex needs even degree, and you must mark edges
  used rather than delete from one side only.
- **Recursion depth.** The recursive Hierholzer is three lines shorter and dies
  at 300 tickets in some judges; the explicit stack below is the version to
  write when the edge count is large.
- **Chinese Postman** if edges may be reused to fix an odd-degree graph — worth
  naming, not worth deriving in 40 minutes.
""",
        ),
    ],
}


def find_itinerary(tickets: list[list[str]]) -> list[str]:
    # Descending, so pop() takes the alphabetically smallest destination.
    departures: defaultdict[str, list[str]] = defaultdict(list)
    for source, destination in sorted(tickets, reverse=True):
        departures[source].append(destination)

    route: list[str] = []
    stack = ["JFK"]

    while stack:
        while departures[stack[-1]]:
            stack.append(departures[stack[-1]].pop())
        route.append(stack.pop())  # stuck here, so this airport is finished

    route.reverse()
    return route


CASES = [
    (
        ([["MUC", "LHR"], ["JFK", "MUC"], ["SFO", "SJC"], ["LHR", "SFO"]],),
        ["JFK", "MUC", "LHR", "SFO", "SJC"],
    ),
    (
        ([["JFK", "SFO"], ["JFK", "ATL"], ["SFO", "ATL"], ["ATL", "JFK"], ["ATL", "SFO"]],),
        ["JFK", "ATL", "JFK", "SFO", "ATL", "SFO"],
    ),
    # The case that kills greedy-without-backtracking.
    (([["JFK", "KUL"], ["JFK", "NRT"], ["NRT", "JFK"]],), ["JFK", "NRT", "JFK", "KUL"]),
    # Two loops off JFK plus a dead end: the dead end must be flown last.
    (
        ([["JFK", "AAA"], ["AAA", "JFK"], ["JFK", "BBB"], ["JFK", "CCC"], ["CCC", "JFK"]],),
        ["JFK", "AAA", "JFK", "CCC", "JFK", "BBB"],
    ),
    # Duplicate tickets: a set-based graph flies this route once and stops.
    (
        ([["JFK", "ATL"], ["ATL", "JFK"], ["JFK", "ATL"], ["ATL", "JFK"]],),
        ["JFK", "ATL", "JFK", "ATL", "JFK"],
    ),
    (([["JFK", "ATL"]],), ["JFK", "ATL"]),
]


def solve(tickets: list[list[str]]) -> list[str]:
    return find_itinerary(tickets)
