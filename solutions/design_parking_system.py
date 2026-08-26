"""Design Parking System — LeetCode 1603."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

META = {
    "pattern": "ood",
    "symbol": "ParkingLot",
    "insight": "Build only what the stated API needs — then grow the model out loud when the interviewer adds a requirement.",
    "time": "O(1) per operation",
    "space": "O(cars parked)",
    "sections": [
        (
            "What it asks",
            """
A parking system with fixed counts of big, medium and small spaces.
`addCar(type)` returns whether the car could park.

Ask: **may a small car occupy a larger space?** In the LeetCode version, no —
but *ask*, because the general version is the more interesting design and
interviewers often want it. Also: do I need to track which car is where, or
only counts? Can the same car park twice?
""",
        ),
        (
            "The minimal answer",
            """
Three counters and a decrement. That is genuinely all the stated API needs,
and delivering it in two minutes **buys you the rest of the round for the
follow-ups** — which is the whole strategy for OOD in a coding round.

The failure mode here is not under-engineering. It is building a class
hierarchy nobody asked for and running out of clock with nothing working.
""",
        ),
        (
            "Then grow it, out loud",
            """
> "If a small car could take a larger space, I'd want a fits-in ordering and a
> tightest-fit policy — and then `leave` needs to know which size was actually
> used, so I'd add a plate→size map."

Growing the design **in response to a stated requirement** is exactly what is
being watched for. The implementation below is that grown version, because it
is the one worth reading.
""",
        ),
        (
            "The design decisions worth narrating",
            """
- **Tightest fit.** Preferring the smallest space that fits leaves large
  spaces for large vehicles. An interviewer will probe this — it is a greedy
  choice and it is correct here because a larger vehicle can never use a
  smaller space.
- **Why the plate→size map exists.** Without it, `leave` cannot restore the
  right counter. The requirement created the field, not the other way round.
- **Idempotency.** Parking the same car twice returns `False` rather than
  double-counting. Say that you thought about it.

Deliberately **not** modelled: floors, pricing, tickets, timestamps. They were
not in the API.
""",
        ),
        (
            "Follow-ups they reach for",
            """
- Multiple floors, and finding the *nearest* free space.
- Pricing by duration — which introduces a clock, and therefore testability
  concerns.
- Concurrency: many gates admitting cars at once. That is a lock around the
  counters, or per-size locks. See
  [Concurrency](../../patterns/concurrency/).
""",
        ),
    ],
}


class Size(Enum):
    """Ordered so a small car can be checked against a larger space."""

    SMALL = 1
    MEDIUM = 2
    LARGE = 3


@dataclass(frozen=True)
class Vehicle:
    plate: str
    size: Size


@dataclass
class ParkingLot:
    capacity: dict[Size, int]
    occupied: dict[str, Size] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.free = dict(self.capacity)

    def _fits(self, size: Size) -> list[Size]:
        """Spaces this vehicle can use, smallest first — tightest fit wins."""
        return [space for space in Size if space.value >= size.value]

    def park(self, vehicle: Vehicle) -> bool:
        if vehicle.plate in self.occupied:
            return False  # idempotent: already parked
        for space in self._fits(vehicle.size):
            if self.free.get(space, 0) > 0:
                self.free[space] -= 1
                # Remember the size used, or `leave` cannot restore it.
                self.occupied[vehicle.plate] = space
                return True
        return False

    def leave(self, plate: str) -> bool:
        space = self.occupied.pop(plate, None)
        if space is None:
            return False
        self.free[space] += 1
        return True

    def available(self, size: Size) -> int:
        return self.free.get(size, 0)


CASES: list[tuple[tuple, object]] = []


def check() -> None:
    lot = ParkingLot({Size.SMALL: 1, Size.MEDIUM: 1, Size.LARGE: 1})

    assert lot.park(Vehicle("AAA", Size.SMALL)) is True
    assert lot.available(Size.SMALL) == 0
    # A second small car takes the medium space — the tightest remaining fit.
    assert lot.park(Vehicle("BBB", Size.SMALL)) is True
    assert lot.available(Size.MEDIUM) == 0
    assert lot.park(Vehicle("BBB", Size.SMALL)) is False  # already parked
    assert lot.park(Vehicle("CCC", Size.LARGE)) is True
    assert lot.park(Vehicle("DDD", Size.SMALL)) is False  # full

    assert lot.leave("AAA") is True
    assert lot.leave("AAA") is False  # idempotent
    assert lot.available(Size.SMALL) == 1
    assert lot.park(Vehicle("DDD", Size.SMALL)) is True

    # A large vehicle can never use a smaller space.
    tight = ParkingLot({Size.SMALL: 5, Size.MEDIUM: 0, Size.LARGE: 0})
    assert tight.park(Vehicle("BIG", Size.LARGE)) is False
    assert tight.park(Vehicle("WEE", Size.SMALL)) is True
