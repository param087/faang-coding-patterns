"""Object-oriented design, sized for a coding round.

Not the 45-minute LLD interview — this is the 20-minute version where you must
produce *working code*, not a class diagram. Two rules keep it on track:

1. **Model the nouns, then the verbs.** Enumerate entities and their
   relationships out loud before typing.
2. **Build only what the stated API needs.** A parking lot does not need a
   billing subsystem unless they asked for one. Over-modelling is the most
   common way to run out of time.

Where a real design conversation is wanted — trade-offs, extensibility,
patterns — see the companion HLD/LLD handbook.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Size(Enum):
    """Vehicle and space sizes, ordered so a small car fits a large space."""

    SMALL = 1
    MEDIUM = 2
    LARGE = 3


@dataclass(frozen=True)
class Vehicle:
    plate: str
    size: Size


@dataclass
class ParkingLot:
    """Design Parking System, extended just far enough to be interesting.

    The design decision worth narrating: one counter per size is enough when
    the only questions are "park" and "leave". A `dict[str, Size]` is added
    because releasing a space requires knowing which size the car occupied —
    without it, `leave` cannot restore the right counter.

    Deliberately *not* modelled: floors, pricing, ticketing. They were not in
    the API.
    """

    capacity: dict[Size, int]
    occupied: dict[str, Size] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.free = dict(self.capacity)

    def _fits(self, size: Size) -> list[Size]:
        """Spaces a vehicle of this size can use, smallest first.

        Preferring the tightest fit leaves large spaces for large vehicles,
        which is the greedy choice an interviewer will probe.
        """
        return [space for space in Size if space.value >= size.value]

    def park(self, vehicle: Vehicle) -> bool:
        if vehicle.plate in self.occupied:
            return False  # already parked; idempotency matters
        for space in self._fits(vehicle.size):
            if self.free.get(space, 0) > 0:
                self.free[space] -= 1
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


class TicTacToe:
    """Design Tic-Tac-Toe, n x n, with O(1) `move`.

    The naive `move` scans the board: O(n) per call, O(n^2) for a full game.
    Keeping running tallies per row, column and the two diagonals makes each
    move O(1) — a win is a tally reaching ±n.

    Encoding player 1 as +1 and player 2 as −1 means one set of counters
    instead of two, which is the trick that makes the code short.
    """

    def __init__(self, n: int) -> None:
        self.n = n
        self.rows = [0] * n
        self.cols = [0] * n
        self.diagonal = 0
        self.anti_diagonal = 0

    def move(self, row: int, col: int, player: int) -> int:
        """Returns the winning player, or 0 if nobody has won yet."""
        delta = 1 if player == 1 else -1

        self.rows[row] += delta
        self.cols[col] += delta
        if row == col:
            self.diagonal += delta
        if row + col == self.n - 1:
            self.anti_diagonal += delta

        if self.n in {
            abs(self.rows[row]),
            abs(self.cols[col]),
            abs(self.diagonal),
            abs(self.anti_diagonal),
        }:
            return player
        return 0


class UndergroundSystem:
    """Design Underground System — average travel time between two stations.

    The modelling decision: store a **running sum and count** per route rather
    than a list of every journey. Both give the same average; the list grows
    without bound and the pair does not. Interviewers ask what happens at
    scale, and this is the answer.
    """

    def __init__(self) -> None:
        self._in_transit: dict[int, tuple[str, int]] = {}
        self._routes: dict[tuple[str, str], tuple[int, int]] = {}  # (total, count)

    def check_in(self, card_id: int, station: str, time: int) -> None:
        self._in_transit[card_id] = (station, time)

    def check_out(self, card_id: int, station: str, time: int) -> None:
        start_station, start_time = self._in_transit.pop(card_id)
        route = (start_station, station)
        total, count = self._routes.get(route, (0, 0))
        self._routes[route] = (total + time - start_time, count + 1)

    def average(self, start: str, end: str) -> float:
        total, count = self._routes.get((start, end), (0, 0))
        return total / count if count else 0.0


CASES: list[tuple[tuple, object]] = []


def check() -> None:
    lot = ParkingLot({Size.SMALL: 1, Size.MEDIUM: 1, Size.LARGE: 1})
    assert lot.park(Vehicle("AAA", Size.SMALL)) is True
    assert lot.available(Size.SMALL) == 0
    # A second small car takes the medium space — tightest fit that remains.
    assert lot.park(Vehicle("BBB", Size.SMALL)) is True
    assert lot.available(Size.MEDIUM) == 0
    assert lot.park(Vehicle("BBB", Size.SMALL)) is False  # already parked
    assert lot.park(Vehicle("CCC", Size.LARGE)) is True
    assert lot.park(Vehicle("DDD", Size.SMALL)) is False  # full
    assert lot.leave("AAA") is True
    assert lot.leave("AAA") is False
    assert lot.park(Vehicle("DDD", Size.SMALL)) is True

    game = TicTacToe(3)
    assert game.move(0, 0, 1) == 0
    assert game.move(0, 2, 2) == 0
    assert game.move(2, 2, 1) == 0
    assert game.move(1, 1, 2) == 0
    assert game.move(2, 0, 1) == 0
    assert game.move(1, 0, 2) == 0
    assert game.move(2, 1, 1) == 1  # bottom row complete

    diagonal_game = TicTacToe(2)
    assert diagonal_game.move(0, 0, 1) == 0
    assert diagonal_game.move(1, 1, 1) == 1

    metro = UndergroundSystem()
    metro.check_in(45, "Leyton", 3)
    metro.check_out(45, "Waterloo", 15)
    metro.check_in(27, "Leyton", 10)
    metro.check_out(27, "Waterloo", 20)
    assert metro.average("Leyton", "Waterloo") == 11.0
    assert metro.average("Waterloo", "Leyton") == 0.0
