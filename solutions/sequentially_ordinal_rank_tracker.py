"""Sequentially Ordinal Rank Tracker — LeetCode 2102."""

from __future__ import annotations

from heapq import heappop, heappush

META = {
    "pattern": "ordered-set",
    "symbol": "SORTracker",
    "insight": "Split the ranking at the number of queries answered: a worst-first heap holds that prefix, a best-first heap holds the rest.",
    "time": "O(log n) per add and per get",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
`add(name, score)` records a location. The **i-th** call to `get()` returns the
i-th best location among everything added so far, where better means higher
score and, on a tie, the lexicographically smaller name. Adds and gets
interleave arbitrarily, up to 4·10⁴ operations.

Ask: is `get()` guaranteed to have enough locations? (Yes — LeetCode guarantees
at least `i` have been added.) And the important one: **can the same name come
back from two different `get()` calls?** Yes, and that is the whole problem —
see below.

A `SortedList` of `(-score, name)` with plain index access, `data[i]`, is a
five-line answer at O(log n) per operation. Say it, note that
`sortedcontainers` is not standard library, then build it out of two heaps.
""",
        ),
        (
            "The insight",
            """
After `k` calls to `get()`, the only thing that matters about the past is
**which `k` locations are the best**; their internal order is settled and will
never be asked for again. So keep the ranking cut in two at position `k`:

- `seen` — those `k` best locations, in a **worst-first** heap, so its top is
  the boundary.
- `rest` — everything else, in a **best-first** heap, so its top is the answer
  to the next `get()`.

`get()` pops `rest` and pushes into `seen`: the prefix grows by one, which is
exactly what "the next ordinal" means.

`add()` pushes into `seen` unconditionally and then evicts `seen`'s worst back
into `rest`, restoring `|seen| == k`. If the new location does not belong in
the top `k` it is the thing evicted, so one code path handles both cases
without a comparison.

The ordering has an asymmetry worth pointing out: `(-score, name)` is a tuple
that a min-heap pops best-first for free, but the mirror image does not exist —
worst-first needs the score reversed and the name **not** reversed, and no
tuple of the two expresses that. Hence a four-line comparison wrapper for the
`seen` side. Reaching for `(score, -name)` is the reflex to catch; strings do
not negate.
""",
        ),
        (
            "The pitfall: get() is not pop()",
            """
The tempting answer is one max-heap that pops the best remaining location per
`get()`. It is wrong, because the i-th `get()` asks for the i-th best of the
set **as it stands now**, and a later `add()` can insert above a name that has
already been returned.

Concretely, with `add` calls interleaved:

```
add(bradford, 2); add(branford, 3)
get() -> branford            ranking: branford, bradford
add(alps, 2)
get() -> alps                ranking: branford, alps, bradford
add(orland, 2)
get() -> bradford            ranking: branford, alps, bradford, orland
add(orlando, 3)
get() -> ?                   ranking: branford, orlando, alps, bradford, orland
```

`orlando` slots in at rank 2, pushing everything down, so the 4th best is now
**`bradford` — returned again**. The pop-and-forget heap answers `orlando`,
because it has thrown away the fact that ranks 1–3 were spent on names that
have since been outranked.

The two-heap split gets this right for free: `orlando` is better than `seen`'s
worst, so it lands in the prefix and `bradford` is the one pushed back out into
`rest`, ready to be returned a second time.
""",
        ),
    ],
}


class SORTracker:
    class _Worst:
        """Order locations worst-first: lower score, then later name."""

        __slots__ = ("name", "score")

        def __init__(self, score: int, name: str) -> None:
            self.score = score
            self.name = name

        def __lt__(self, other: SORTracker._Worst) -> bool:
            if self.score != other.score:
                return self.score < other.score
            return self.name > other.name  # reversed on name only

    def __init__(self) -> None:
        self.seen: list[SORTracker._Worst] = []  # the `returned` best, worst on top
        self.rest: list[tuple[int, str]] = []  # (-score, name): best on top
        self.returned = 0

    def add(self, name: str, score: int) -> None:
        heappush(self.seen, self._Worst(score, name))
        if len(self.seen) > self.returned:
            worst = heappop(self.seen)  # possibly the one just pushed
            heappush(self.rest, (-worst.score, worst.name))

    def get(self) -> str:
        negated, name = heappop(self.rest)
        heappush(self.seen, self._Worst(-negated, name))
        self.returned += 1
        return name


CASES: list[tuple[tuple, object]] = []


def check() -> None:
    # The interleaving that breaks a single pop-and-forget heap.
    tracker = SORTracker()
    tracker.add("bradford", 2)
    tracker.add("branford", 3)
    assert tracker.get() == "branford"
    tracker.add("alps", 2)
    assert tracker.get() == "alps"
    tracker.add("orland", 2)
    assert tracker.get() == "bradford"
    tracker.add("orlando", 3)
    assert tracker.get() == "bradford"  # returned a second time, by design
    assert tracker.get() == "orland"

    # Ties resolve to the lexicographically smaller name, not insertion order.
    ties = SORTracker()
    for name in ("zeta", "beta", "alpha"):
        ties.add(name, 7)
    assert [ties.get() for _ in range(3)] == ["alpha", "beta", "zeta"]

    # Score dominates the name.
    scores = SORTracker()
    scores.add("aaa", 1)
    scores.add("zzz", 2)
    assert scores.get() == "zzz"
    assert scores.get() == "aaa"

    # Adding everything first, then draining, must give the full ranking.
    batch = SORTracker()
    for name, score in (("d", 1), ("b", 3), ("c", 3), ("a", 2)):
        batch.add(name, score)
    assert [batch.get() for _ in range(4)] == ["b", "c", "a", "d"]

    # A single location, and an add that lands strictly below the boundary.
    single = SORTracker()
    single.add("solo", 5)
    assert single.get() == "solo"
    single.add("worse", 1)
    assert single.get() == "worse"

    # Cross-check the invariant against a brute-force ranking on a mixed stream.
    reference: list[tuple[int, str]] = []
    model = SORTracker()
    queries = 0
    stream = [
        ("add", "m", 4),
        ("add", "n", 4),
        ("get", "", 0),
        ("add", "a", 9),
        ("add", "z", 1),
        ("get", "", 0),
        ("get", "", 0),
        ("add", "b", 9),
        ("get", "", 0),
        ("get", "", 0),
        ("add", "c", 0),
        ("get", "", 0),
    ]
    for operation, name, score in stream:
        if operation == "add":
            reference.append((-score, name))
            model.add(name, score)
        else:
            queries += 1
            assert model.get() == sorted(reference)[queries - 1][1]
