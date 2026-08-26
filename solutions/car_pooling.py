"""Car Pooling — LeetCode 1094."""

from __future__ import annotations

META = {
    "pattern": "prefix-sums",
    "insight": "Record +passengers at pickup and −passengers at drop-off; the running prefix of that difference array is occupancy at every stop.",
    "time": "O(n + L), L = 1001 stops",
    "space": "O(L)",
    "sections": [
        (
            "What it asks",
            """
Each trip is `[passengers, from, to]` on a car that only drives forwards.
Return whether every trip fits without the occupancy ever exceeding
`capacity`.

The clarifying question that matters: **does a passenger occupy a seat at
location `to`?** No — they get out there, so a trip ending at 5 and a trip
starting at 5 share no seat. Get this wrong and you reject valid inputs.
""",
        ),
        (
            "The insight",
            """
The naive version simulates: for each of the 1000 locations, sum the
passengers of every trip covering it. `O(n · L)` — at `n = 1000` that is 10⁶,
survivable here but the wrong instinct, because it recomputes an occupancy
that changes at only `2n` points.

Occupancy is a **range update, point query** problem, which is exactly what a
difference array is for. Instead of adding `p` to every location in
`[from, to)`, write it twice:

```
delta[from] += p
delta[to]   -= p
```

Then `sum(delta[0..x])` is the occupancy at `x`, and one left-to-right prefix
scan recovers every value. `n` trips cost `O(n)` to record and `O(L)` to
sweep, and each of the two writes per trip is what turns a range update into
two point updates.

`L` is 1001 because LeetCode bounds locations to `0..1000` — that bound is in
the statement precisely to make the array version viable.
""",
        ),
        (
            "Edge cases and the unbounded variant",
            """
- **Drop-off at `to`, not `to + 1`.** `delta[to] -= p` is the half-open
  convention. `[[2,1,5],[3,5,7]]` with `capacity = 3` is **true**; the `+1`
  version says false.
- **A single trip can bust capacity on its own** — `[[9,0,1]]` with
  `capacity = 4`. There is no "at least two trips overlap" precondition.
- **Empty `trips`** is trivially true, including when `capacity` is 0.
- **Unbounded locations?** Drop the array and sort the `2n` events instead,
  breaking ties so drop-offs are processed before pickups at the same point.
  `O(n log n)`, same sweep, and it is the version to write if the interviewer
  removes the `1000` bound or makes locations floats.
""",
        ),
    ],
}

MAX_LOCATION = 1000


def car_pooling(trips: list[list[int]], capacity: int) -> bool:
    delta = [0] * (MAX_LOCATION + 2)

    for passengers, start, end in trips:
        delta[start] += passengers
        delta[end] -= passengers  # they leave AT `end`, freeing the seat there

    occupancy = 0
    for change in delta:
        occupancy += change
        if occupancy > capacity:
            return False

    return True


CASES = [
    (([[2, 1, 5], [3, 3, 7]], 4), False),
    (([[2, 1, 5], [3, 3, 7]], 5), True),
    (([[2, 1, 5], [3, 5, 7]], 3), True),
    (([[2, 1, 5], [3, 5, 7]], 2), False),
    (([[3, 2, 7], [3, 7, 9], [8, 3, 9]], 11), True),
    (([[9, 0, 1]], 4), False),
    (([[1, 0, 1000]], 1), True),
    (([], 0), True),
]


def solve(trips: list[list[int]], capacity: int) -> bool:
    return car_pooling(trips, capacity)
