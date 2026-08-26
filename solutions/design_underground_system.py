"""Design Underground System — LeetCode 1396."""

from __future__ import annotations

META = {
    "pattern": "design",
    "symbol": "UndergroundSystem",
    "insight": "Never store journeys: keep a running (total, count) per station pair so the average is one division.",
    "time": "O(1) for all three operations",
    "space": "O(passengers in transit + distinct station pairs)",
    "sections": [
        (
            "What it asks",
            """
A turnstile system: `checkIn(id, station, t)`, `checkOut(id, station, t)`, and
`getAverageTime(start, end)` — the mean travel time over all completed journeys
between that ordered pair of stations.

Ask: can a passenger be checked in twice without checking out (no — a customer
is in at most one journey at a time, and that guarantee is what lets the
in-transit map be keyed by id alone), and is `getAverageTime` only called for
pairs that have at least one journey (yes).
""",
        ),
        (
            "The insight",
            """
The wrong first answer is a list of durations per route, averaged on demand.
It is correct and it is O(journeys) per query — with 2·10⁴ operations mostly on
one popular route, a single query walks nearly the whole log.

You never need the individual durations. **Accumulate `(total, count)`** and
divide at query time:

```
totals[(start, end)] += t_out - t_in
counts[(start, end)] += 1
```

Two maps, both O(1):

- `in_transit: id → (station, time)` — one entry per passenger currently
  travelling, deleted on check-out so the map stays the size of the concourse,
  not the size of the day.
- `routes: (start, end) → [total, count]`.

That is the entire question. What is being tested is whether you reach for a
running aggregate instead of hoarding raw events — the same reflex that keeps
a metrics pipeline from storing every sample.
""",
        ),
        (
            "Edge cases worth saying out loud",
            """
- **The key is an ordered pair.** Paddington → Waterloo and Waterloo →
  Paddington are different routes with different averages. Using a
  `frozenset` here is a real bug, not a stylistic choice.
- **A passenger checking in and out at the same station** is a legal journey
  with duration ≥ 0; do not special-case it.
- **Delete the in-transit entry on check-out.** Leaving it is a memory leak in
  a long-running system and it silently breaks the passenger's next journey.
- **Floating point**: keep the total as an **integer** and divide once. Adding
  averages incrementally accumulates drift; one division at the end does not.
- **Ids repeat.** The same passenger travels many times a day, so the in-transit
  map must be safe to reuse after deletion.
""",
        ),
    ],
}


class UndergroundSystem:
    def __init__(self) -> None:
        # id -> (station, check-in time); one entry per passenger in transit.
        self.in_transit: dict[int, tuple[str, int]] = {}
        # (start, end) -> [total duration, journey count]. Ordered pair.
        self.routes: dict[tuple[str, str], list[int]] = {}

    def checkIn(self, id: int, stationName: str, t: int) -> None:
        self.in_transit[id] = (stationName, t)

    def checkOut(self, id: int, stationName: str, t: int) -> None:
        start, started_at = self.in_transit.pop(id)  # pop: no leak, reusable id
        route = self.routes.setdefault((start, stationName), [0, 0])
        route[0] += t - started_at
        route[1] += 1

    def getAverageTime(self, startStation: str, endStation: str) -> float:
        total, count = self.routes[(startStation, endStation)]
        return total / count  # integers until the single division


def check() -> None:
    system = UndergroundSystem()
    system.checkIn(45, "Leyton", 3)
    system.checkIn(32, "Paradise", 8)
    system.checkIn(27, "Leyton", 10)
    system.checkOut(45, "Waterloo", 15)  # 12
    system.checkOut(27, "Waterloo", 20)  # 10
    system.checkOut(32, "Cambridge", 22)  # 14
    assert system.getAverageTime("Paradise", "Cambridge") == 14.0
    assert system.getAverageTime("Leyton", "Waterloo") == 11.0

    system.checkIn(10, "Leyton", 24)
    system.checkOut(10, "Waterloo", 38)  # 14 -> (12 + 10 + 14) / 3
    assert system.getAverageTime("Leyton", "Waterloo") == 12.0

    # Direction matters: the reverse pair is a separate route.
    system.checkIn(45, "Waterloo", 40)
    system.checkOut(45, "Leyton", 60)
    assert system.getAverageTime("Waterloo", "Leyton") == 20.0
    assert system.getAverageTime("Leyton", "Waterloo") == 12.0

    # A repeat traveller: the in-transit slot must be free again.
    assert 45 not in system.in_transit

    # Same station in and out, and a zero-length journey.
    loop = UndergroundSystem()
    loop.checkIn(1, "Angel", 5)
    loop.checkOut(1, "Angel", 5)
    assert loop.getAverageTime("Angel", "Angel") == 0.0

    # Non-integer mean: 3 and 4 average to 3.5, so the total must stay exact.
    fractional = UndergroundSystem()
    for rider, (start, end) in enumerate([(0, 3), (10, 14)]):
        fractional.checkIn(rider, "A", start)
        fractional.checkOut(rider, "B", end)
    assert fractional.getAverageTime("A", "B") == 3.5
