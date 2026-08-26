"""Design a Food Rating System — LeetCode 2353."""

from __future__ import annotations

import heapq
from collections import defaultdict

META = {
    "pattern": "ood",
    "symbol": "FoodRatings",
    "insight": "Heaps cannot update a key, so never update one: push the new rating and let the query drop any top that disagrees with the record.",
    "time": "O(log n) to change, amortised O(log n) to query",
    "space": "O(n + changes) — stale heap entries are never swept",
    "sections": [
        (
            "What it asks",
            """
Every food has one cuisine and a rating. Two operations:

- `changeRating(food, newRating)`;
- `highestRated(cuisine)` — the best-rated food of that cuisine, ties broken by
  the **lexicographically smallest name**.

Ask three things. Is a food's cuisine fixed for life? (Yes — that is what lets
you index by cuisine once, in the constructor, and never re-bucket.) Can two
foods share a rating? (Yes, and the tie rule is why the answer is a name rather
than a number.) What is the ratio of changes to queries? (It decides whether
you pay on write or on read.)
""",
        ),
        (
            "The insight",
            """
The tie rule is the whole design. Order entries by the pair `(-rating, name)`
and one comparison delivers both halves of the contract: highest rating first,
and among equal ratings the smaller name first. Nothing downstream has to know
the tie rule exists.

That leaves the update problem. A per-cuisine max-heap inserts in O(log n) but
a binary heap **cannot revise a key in place** — there is no handle to the old
entry. Two honest ways out:

- a balanced BST keyed by `(-rating, name)`: delete the old key, insert the
  new one, O(log n) worst case. This is the natural Java answer (`TreeSet`),
  and in Python it means reaching for `sortedcontainers`, which is not in the
  standard library and may not be installed in the interview editor.
- **lazy deletion**: never remove anything. A change pushes a fresh
  `(-rating, food)` entry and updates the authoritative `rating_of[food]`. A
  query pops from the top while the top's rating disagrees with the record.

Lazy deletion is the one to write. Cost it out loud so it does not sound like
a hack: each change pushes exactly one entry, each entry is popped at most
once, so `m` changes cost O((n + m) log n) **across the whole run** — the
popping is amortised over the changes that caused it, not charged to whichever
query happens to hit it.
""",
        ),
        (
            "Why the staleness test compares ratings, not versions",
            """
The test is `rating_of[food] == -neg`: does this entry claim the rating the
food actually has right now? The instinct is a version counter, and it is
strictly worse here.

Consider a food changed 7 → 9 → 7. The heap now holds `(-7, f)`, `(-9, f)` and
`(-7, f)` again. A version counter marks the first `(-7, f)` stale and pops it;
the rating test keeps it, because it reports the truth. Both give the right
answer, but the rating test needs no extra field and no per-food counter.

The invariant that makes it safe: an entry is accepted only when it states the
food's current rating, so accepting it can never report a value that is not
current. Duplicates linger, but the **top** is always correct.

The remaining edge cases:

- a cuisine with a food whose rating drops below a sibling's — handled, since
  the sibling's entry was already in the heap;
- `highestRated` on a cuisine nobody registered — the constraints promise it
  never happens, so the code returns `""` rather than growing a branch that
  will never run;
- memory: the heap only grows. If changes vastly outnumber foods, sweep on a
  size threshold, or switch to the BST version.
""",
        ),
    ],
}


class FoodRatings:
    """Per-cuisine max-heap keyed by (-rating, name), cleaned lazily on read."""

    def __init__(self, foods: list[str], cuisines: list[str], ratings: list[int]) -> None:
        self.cuisine_of: dict[str, str] = {}
        self.rating_of: dict[str, int] = {}
        self.best: dict[str, list[tuple[int, str]]] = defaultdict(list)

        for food, cuisine, rating in zip(foods, cuisines, ratings, strict=True):
            self.cuisine_of[food] = cuisine
            self.rating_of[food] = rating  # the record; the heap is a cache
            self.best[cuisine].append((-rating, food))

        for heap in self.best.values():
            heapq.heapify(heap)  # O(n) per cuisine, cheaper than n pushes

    def changeRating(self, food: str, newRating: int) -> None:
        self.rating_of[food] = newRating
        # No delete: the old entry stays and is recognised as stale on read.
        heapq.heappush(self.best[self.cuisine_of[food]], (-newRating, food))

    def highestRated(self, cuisine: str) -> str:
        heap = self.best[cuisine]
        while heap:
            negated, food = heap[0]
            if self.rating_of[food] == -negated:
                return food  # (-rating, name) ordering already broke the tie
            heapq.heappop(heap)
        return ""


def check() -> None:
    ratings = FoodRatings(
        ["kimchi", "miso", "sushi", "moussaka", "ramen", "bulgogi"],
        ["korean", "japanese", "japanese", "greek", "japanese", "korean"],
        [9, 12, 8, 15, 14, 7],
    )
    assert ratings.highestRated("korean") == "kimchi"
    assert ratings.highestRated("japanese") == "ramen"

    ratings.changeRating("sushi", 16)
    assert ratings.highestRated("japanese") == "sushi"

    # The tie case: ramen and sushi both at 16, so the smaller name wins.
    ratings.changeRating("ramen", 16)
    assert ratings.highestRated("japanese") == "ramen"

    # A drop must dethrone: kimchi 9 -> 1 hands korean to bulgogi at 7.
    ratings.changeRating("kimchi", 1)
    assert ratings.highestRated("korean") == "bulgogi"

    # Back up again, past bulgogi. The stale (-9) entry must not be believed.
    ratings.changeRating("kimchi", 8)
    assert ratings.highestRated("korean") == "kimchi"

    # A single-food cuisine, and a rating that oscillates back to an old value.
    solo = FoodRatings(["feta"], ["greek"], [7])
    assert solo.highestRated("greek") == "feta"
    solo.changeRating("feta", 9)
    solo.changeRating("feta", 7)
    assert solo.highestRated("greek") == "feta"

    # Ties at construction time, not just after a change.
    tied = FoodRatings(["b", "a", "c"], ["x", "x", "x"], [5, 5, 5])
    assert tied.highestRated("x") == "a"
    tied.changeRating("a", 4)
    assert tied.highestRated("x") == "b"

    assert tied.highestRated("nonexistent") == ""
