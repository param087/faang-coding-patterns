"""Traffic Light Controlled Intersection — LeetCode 1279."""

from __future__ import annotations

import random
import threading
from collections.abc import Callable
from functools import partial

META = {
    "pattern": "concurrency",
    "symbol": "TrafficLight",
    "insight": "The light is just a variable guarded by one mutex — switch it only when the arriving car is on the road that is currently red.",
    "time": "O(1) per car",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
*(Premium, so described in my own words.)* Two roads cross. Cars arrive on
either road, one thread per car, and each announces its id, its road (1 or 2)
and its direction. Only one road may have a green light at a time, only one car
may be crossing at a time, and the light starts green on road 1. You are given
two callbacks — turn the light green for a road, and cross a car — and must
call them so that:

- a car only crosses while **its own** road is green, and
- the light is switched **only when it has to be**.

Ask what "only when it has to be" means precisely: a car arriving on the green
road must cross without any light change. That single sentence is the entire
specification, and it is what rules out a timer or a round-robin.
""",
        ),
        (
            "The insight",
            """
There is no producer/consumer here, no ordering constraint between threads and
nothing to wait for — a car is never *blocked*, only serialised. So the answer
is the smallest primitive that exists:

```python
with self._lock:
    if self._green_road != road_id:
        turn_green()
        self._green_road = road_id
    cross_car()
```

One mutex makes "check the light, maybe switch it, cross" a single atomic step.
Drop the lock and two cars from opposite roads both read the old green value,
one switches the light while the other is mid-crossing, and you have a
collision — the exact failure the problem is modelling.

`direction` is a **decoy**. Both directions on a road share its light, so the
answer never reads it. Say that out loud; noticing which input is irrelevant is
part of the signal.
""",
        ),
        (
            "The pitfall: doing more than the problem asks",
            """
The instinct is that a traffic light needs fairness — otherwise a steady stream
on road 1 starves road 2 forever. That instinct is right about traffic and
wrong about this question. There is nothing to be fair *about*: every car
crosses on arrival, immediately, and no thread ever waits on another thread's
condition. Adding a condition variable, a turn counter or a green-phase timer
gets you a slower, longer, more fragile answer that also **fails the "switch
only when necessary" rule**, because a timer switches with no car waiting.

Where the follow-up genuinely lives:

- **"Now a crossing takes time and cars queue up."** Then you do want batching —
  two condition variables (one per road), drain the green road's queue, switch
  when it empties and the other road is non-empty. And now you need a cap on
  the batch, or road 2 really does starve.
- **"Ten thousand cars a second."** The mutex is the bottleneck and everything
  in it must stay O(1). Any logging inside the critical section is the bug.
- **"Prove it."** Race conditions are probabilistic. Record every `turn_green`
  and `cross_car` into a log **inside** the lock, then replay it afterwards:
  every crossing must find its own road green, and no two `turn_green` calls
  may be adjacent. The test below does exactly that; a single passing run
  proves nothing.
""",
        ),
    ],
}


class TrafficLight:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._green_road = 1  # road 1 starts green

    def car_arrived(
        self,
        car_id: int,
        road_id: int,
        direction: int,  # unused: both directions share a road's light
        turn_green: Callable[[], None],
        cross_car: Callable[[], None],
    ) -> None:
        with self._lock:
            if self._green_road != road_id:
                turn_green()  # only when the arriving car faces a red
                self._green_road = road_id
            cross_car()


def _drive(arrivals: list[tuple[int, int]]) -> list[tuple]:
    """Run one car per thread and return the event log, in real order."""
    light = TrafficLight()
    monitor = threading.Lock()
    log: list[tuple] = []

    def arrive(car_id: int, road_id: int) -> None:
        def turn_green() -> None:
            with monitor:
                log.append(("green", road_id))

        def cross_car() -> None:
            with monitor:
                log.append(("cross", road_id, car_id))

        direction = 1 if road_id == 1 else 3
        light.car_arrived(car_id, road_id, direction, turn_green, cross_car)

    threads = [
        threading.Thread(target=arrive, args=(car_id, road_id), daemon=True)
        for car_id, road_id in arrivals
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=10)
        assert not thread.is_alive(), "a car never crossed"
    return log


def _replay(log: list[tuple], arrivals: list[tuple[int, int]]) -> int:
    """Validate the log and return how many times the light was switched."""
    green = 1
    crossed: list[int] = []
    switches = 0
    previous = ""
    for event in log:
        if event[0] == "green":
            assert event[1] != green, "switched the light to the road already green"
            assert previous != "green", "two switches with no car between them"
            green = event[1]
            switches += 1
        else:
            assert event[1] == green, f"car {event[2]} crossed against a red"
            crossed.append(event[2])
        previous = event[0]
    assert sorted(crossed) == sorted(car_id for car_id, _ in arrivals)
    return switches


def check() -> None:
    rng = random.Random(1279)
    for _ in range(25):
        arrivals = [(car_id, rng.choice((1, 2))) for car_id in range(30)]
        _replay(_drive(arrivals), arrivals)

    # Every car on the already-green road: the light must never be touched.
    only_road_one = [(car_id, 1) for car_id in range(20)]
    assert _replay(_drive(only_road_one), only_road_one) == 0

    # Every car on the red road: exactly one switch, then nothing more.
    only_road_two = [(car_id, 2) for car_id in range(20)]
    assert _replay(_drive(only_road_two), only_road_two) == 1

    # Sequential, so the log is fully determined.
    light = TrafficLight()
    log: list[tuple] = []
    for car_id, road_id in ((1, 1), (2, 2), (3, 2), (4, 1)):
        light.car_arrived(
            car_id,
            road_id,
            1,
            partial(log.append, ("green", road_id)),
            partial(log.append, ("cross", road_id, car_id)),
        )
    assert log == [
        ("cross", 1, 1),
        ("green", 2),
        ("cross", 2, 2),
        ("cross", 2, 3),
        ("green", 1),
        ("cross", 1, 4),
    ]
