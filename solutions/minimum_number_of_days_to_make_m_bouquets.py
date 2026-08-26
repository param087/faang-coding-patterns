"""Minimum Number of Days to Make m Bouquets — LeetCode 1482."""

from __future__ import annotations

META = {
    "pattern": "binary-search-answer",
    "insight": "Flowers never un-bloom, so 'can I make m bouquets by day d' is monotone in d — and answering it is one linear sweep.",
    "time": "O(n log(max bloom day))",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
`bloom_day[i]` is the day flower `i` opens. A bouquet needs `k` **adjacent**
flowers, all already bloomed, and no flower can be in two bouquets. Find the
earliest day you can make `m` bouquets, or `-1`.

Two things to pin down before writing code: *adjacent* means contiguous in the
array (not "adjacent among the bloomed ones"), and the answer is a **day from
the array's range**, not an index. Both are easy to misread under pressure.
""",
        ),
        (
            "The insight",
            """
The array is not sorted and sorting it destroys adjacency, so nothing about
the input structure helps. What helps is that **blooming is irreversible**: a
flower open on day `d` is open on day `d + 1`. So the set of days on which `m`
bouquets are possible is a suffix of the timeline, and you can binary search
its start over `[min(bloom_day), max(bloom_day)]`.

The feasibility check is a single sweep counting runs: walk the array, keep a
counter of consecutive bloomed flowers, and every time it reaches `k`, bank a
bouquet and **reset the counter to zero**. A flower whose bloom day exceeds
`d` also resets it.

Resetting to zero rather than letting the run keep growing is the greedy
choice, and it is optimal: taking the earliest possible `k` in a run of length
`L` still leaves `L − k` for later, and `L // k` bouquets is the most any run
can yield.

Answer the impossible case up front: if `m * k > len(bloom_day)` there are not
enough flowers in existence, return `-1`. Do this **before** the search, since
`m * k` can overflow the intuition of "surely it fits" at m, k ~ 10⁵.
""",
        ),
        (
            "Pitfalls",
            """
- **`m * k > n` check omitted.** The binary search then returns
  `max(bloom_day)`, a plausible-looking wrong answer that passes small tests.
  Compute the product in Python (arbitrary precision), but in C++/Java cast to
  `long` — `10⁵ * 10⁵` overflows a 32-bit int.
- **Counting `run // k` at the end instead of resetting.** Equivalent, but only
  if you also add the partial run after the loop ends. Forgetting the tail is
  the classic bug: `[7,7,7,7,12,7,7]` with `k = 2` needs the trailing pair.
- **Searching `[1, 10⁹]`.** Correct but sloppy; `[min, max]` of the array is
  both tighter and shows you know the answer must be an actual bloom day —
  waiting a day when nothing new opens changes nothing.
- **`k = 1`.** Every bloomed flower is a bouquet; the answer is the `m`-th
  smallest bloom day. Good sanity check against your sweep.
""",
        ),
    ],
}


def min_days(bloom_day: list[int], m: int, k: int) -> int:
    if m * k > len(bloom_day):
        return -1  # not enough flowers exist, no amount of waiting helps

    def feasible(day: int) -> bool:
        bouquets, run = 0, 0
        for bloom in bloom_day:
            if bloom > day:
                run = 0  # not open yet, the adjacent run is broken
                continue
            run += 1
            if run == k:
                bouquets += 1
                run = 0  # these k are spent; start a fresh run
                if bouquets >= m:
                    return True
        return bouquets >= m

    low, high = min(bloom_day), max(bloom_day)
    while low < high:
        mid = (low + high) // 2
        if feasible(mid):
            high = mid
        else:
            low = mid + 1

    return low


CASES = [
    (([1, 10, 3, 10, 2], 3, 1), 3),
    (([1, 10, 3, 10, 2], 3, 2), -1),
    (([7, 7, 7, 7, 12, 7, 7], 2, 3), 12),
    (([1, 10, 2, 9, 3, 8, 4, 7, 5, 6], 4, 2), 9),
    (([1000000000, 1000000000], 1, 1), 1000000000),
    (([5, 5, 5, 5], 2, 2), 5),
    (([1], 1, 1), 1),
]


def solve(bloom_day: list[int], m: int, k: int) -> int:
    return min_days(bloom_day, m, k)
