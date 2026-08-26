"""Design Movie Rental System — LeetCode 1912."""

from __future__ import annotations

import heapq
from collections import defaultdict

META = {
    "pattern": "ood",
    "symbol": "MovieRentingSystem",
    "insight": "Two ordered views of the same entries — unrented per movie, rented globally — and rent or drop only writes to the view it moves into.",
    "time": "O(log n) to rent or drop, amortised O(log n) for a five-item query",
    "space": "O(n + operations) — lazily deleted entries linger",
    "sections": [
        (
            "What it asks",
            """
Shops each stock at most one copy of a movie at a fixed price. Four operations:

- `search(movie)` — the five cheapest shops with that movie **unrented**;
- `rent(shop, movie)` / `drop(shop, movie)`;
- `report()` — the five cheapest **rented** `[shop, movie]` pairs.

Both queries order by price, then by shop, then (for `report`) by movie.

Ask whether prices ever change — they do not, which is why an entry's sort key
is immortal and lazy deletion is safe. Ask whether a shop can hold two copies of
one film: no, so `(shop, movie)` is a primary key and a plain dict of prices is
the source of truth.

The "five" is the tell. It is a fixed constant, so a query is a peek at the
front of an ordering, not a sort of everything.
""",
        ),
        (
            "The insight",
            """
An entry lives in exactly one of two states, and each state needs its own
ordering:

- unrented, ordered **within its movie** by `(price, shop)`;
- rented, ordered **globally** by `(price, shop, movie)`.

Renting is a move between the two. The textbook structure is a balanced BST per
movie plus one global — `TreeSet` in Java, `SortedList` from
`sortedcontainers` in Python — with an O(log n) erase on each side. The catch is
that `sortedcontainers` is not in the standard library and may not exist in the
interview editor, so know the version you can build from `heapq`.

Heaps insert in O(log n) but cannot erase an interior element, so **do not
erase**. `rent` pushes into the rented heap and leaves the stale copy sitting
in the movie's heap; `drop` pushes back into the movie's heap and abandons the
copy in the rented heap. Truth lives in a `rented` set of `(shop, movie)` keys,
and a query discards any entry the set contradicts as it peeks.

The cost argument, which is the part worth saying: each `rent` and each `drop`
pushes one entry, every entry is discarded at most once, so the discarding is
paid for by the operation that created it. A query pops at most five *keepable*
entries plus its share of the amortised rubbish, then pushes the five back.
""",
        ),
        (
            "The duplicate that lazy deletion creates",
            """
The bug that survives the first round of testing: `rent` then `drop` leaves
**two** identical entries in the movie's heap — the original, never removed, and
the one `drop` pushed back. A `search` that only filters on "is it rented?"
then returns the same shop twice and the caller's list of five is short by one.

So a query needs two filters, not one:

1. discard entries whose state contradicts the `rented` set — permanently, they
   are rubbish;
2. discard entries for a key already collected in *this* query — also
   permanently, because at least one copy is being kept.

Filter 2 both fixes the answer and stops the heap growing without bound. It is
safe because the copies are identical: the invariant is "at least one copy of
every unrented entry exists in its movie heap", and keeping one while dropping
the rest preserves it exactly.

Other things worth defending:

- `report` returns pairs, so the entry must carry the movie id; `search` is
  already scoped to a movie and does not need it. Different key widths for the
  two heaps is deliberate, not sloppy.
- `search` on a movie no shop stocks returns `[]` — the `defaultdict` makes that
  fall out rather than needing a branch.
- Renting something already rented, or dropping something not rented, is
  excluded by the constraints; in production both should be idempotent, since
  the double-drop is exactly what corrupts the counts.
""",
        ),
    ],
}


class MovieRentingSystem:
    """Lazy-deletion heaps: one per movie for stock, one global for rentals."""

    def __init__(self, n: int, entries: list[list[int]]) -> None:
        self.price: dict[tuple[int, int], int] = {}
        self.available: dict[int, list[tuple[int, int]]] = defaultdict(list)
        self.rented_heap: list[tuple[int, int, int]] = []
        self.rented: set[tuple[int, int]] = set()

        for shop, movie, price in entries:
            self.price[(shop, movie)] = price
            self.available[movie].append((price, shop))

        for heap in self.available.values():
            heapq.heapify(heap)

    def search(self, movie: int) -> list[int]:
        heap = self.available[movie]
        kept: list[tuple[int, int]] = []
        seen: set[int] = set()

        while heap and len(kept) < 5:
            price, shop = heapq.heappop(heap)
            if (shop, movie) in self.rented or shop in seen:
                continue  # stale, or a duplicate left behind by rent + drop
            seen.add(shop)
            kept.append((price, shop))

        for entry in kept:
            heapq.heappush(heap, entry)
        return [shop for _, shop in kept]

    def rent(self, shop: int, movie: int) -> None:
        self.rented.add((shop, movie))
        # The copy in self.available[movie] stays; search will discard it.
        heapq.heappush(self.rented_heap, (self.price[(shop, movie)], shop, movie))

    def drop(self, shop: int, movie: int) -> None:
        self.rented.discard((shop, movie))
        heapq.heappush(self.available[movie], (self.price[(shop, movie)], shop))

    def report(self) -> list[list[int]]:
        kept: list[tuple[int, int, int]] = []
        seen: set[tuple[int, int]] = set()

        while self.rented_heap and len(kept) < 5:
            price, shop, movie = heapq.heappop(self.rented_heap)
            if (shop, movie) not in self.rented or (shop, movie) in seen:
                continue
            seen.add((shop, movie))
            kept.append((price, shop, movie))

        for entry in kept:
            heapq.heappush(self.rented_heap, entry)
        return [[shop, movie] for _, shop, movie in kept]


def check() -> None:
    system = MovieRentingSystem(
        3, [[0, 1, 5], [0, 2, 6], [0, 3, 7], [1, 1, 4], [1, 2, 7], [2, 1, 5]]
    )
    # Movie 1: shop 1 at 4, then shops 0 and 2 tied at 5 — lower shop id first.
    assert system.search(1) == [1, 0, 2]

    system.rent(0, 1)
    system.rent(1, 2)
    assert system.report() == [[0, 1], [1, 2]]  # priced 5 and 7
    assert system.search(1) == [1, 2]  # shop 0's copy is out

    system.drop(1, 2)
    assert system.search(2) == [0, 1]
    assert system.report() == [[0, 1]]

    # rent -> drop -> rent leaves duplicate entries; neither query may repeat.
    system.rent(1, 2)
    system.drop(1, 2)
    system.rent(1, 2)
    system.drop(1, 2)
    assert system.search(2) == [0, 1]
    system.rent(0, 2)
    assert system.report() == [[0, 1], [0, 2]]
    system.drop(0, 1)
    assert system.search(1) == [1, 0, 2]
    assert system.report() == [[0, 2]]

    # A movie nobody stocks, and a shop that stocks nothing.
    assert system.search(99) == []

    # More than five candidates: the query truncates, and ties break by shop.
    wide = MovieRentingSystem(7, [[shop, 1, 10] for shop in range(7)])
    assert wide.search(1) == [0, 1, 2, 3, 4]  # truncated at five
    wide.rent(0, 1)
    wide.rent(3, 1)
    assert wide.search(1) == [1, 2, 4, 5, 6]
    assert wide.report() == [[0, 1], [3, 1]]

    # Everything rented, then everything returned.
    small = MovieRentingSystem(2, [[0, 1, 3], [1, 1, 2]])
    small.rent(0, 1)
    small.rent(1, 1)
    assert small.search(1) == []
    assert small.report() == [[1, 1], [0, 1]]  # 2 before 3
    small.drop(0, 1)
    small.drop(1, 1)
    assert small.report() == []
    assert small.search(1) == [1, 0]
