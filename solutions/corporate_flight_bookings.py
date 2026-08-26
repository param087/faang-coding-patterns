"""Corporate Flight Bookings — LeetCode 1109."""

from __future__ import annotations

META = {
    "pattern": "prefix-sums",
    "insight": "A range update is two point updates on the difference array; one prefix-sum pass at the end materialises every total.",
    "time": "O(n + b) for n flights and b bookings",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Each booking `[first, last, seats]` reserves `seats` on **every** flight from
`first` to `last` inclusive, flights being numbered `1 .. n`. Return the total
seats reserved on each flight.

Ask: **are the flight labels 1-indexed?** They are, and the array you return is
0-indexed, so there is exactly one conversion and it is the only thing that can
go wrong. Confirm ranges may overlap arbitrarily (they may) and that `seats` is
positive (it is, though nothing in the algorithm cares).
""",
        ),
        (
            "The insight",
            """
Applying each booking directly is O(n) per booking: 2 × 10⁴ bookings over
2 × 10⁴ flights is **4 × 10⁸** increments. Fine in C, not in Python, and it is
the wrong shape anyway.

Invert the relationship between the array and its prefix sum. If `answer` is
the prefix sum of some array `diff`, then adding `s` to `answer[i..j]` means
adding `s` to `diff[i]` — which lifts everything from `i` onward — and
subtracting `s` at `diff[j + 1]` to cancel that lift past the range.

```
diff[first - 1] += seats
diff[last]      -= seats        # already the index one past the range
```

Each booking becomes **two writes**, whatever its width. One prefix-sum pass at
the end turns `diff` back into the answer. This is the difference array, and it
is the mirror image of the rest of the pattern: prefix sums make range
*queries* O(1); difference arrays make range *updates* O(1).

The trade is that reads are only correct once, after the final pass. If you need
interleaved updates and queries, this collapses and you want a Fenwick tree
over the difference array instead.
""",
        ),
        (
            "The off-by-one, which is the only real risk",
            """
The `-1` on `first` and the *absence* of one on `last` look asymmetric and
inconsistent. They are not: `first - 1` converts a 1-indexed flight to a
0-indexed slot, and `last` is *already* `(last - 1) + 1`, the slot one past the
end of the range. The two corrections cancel. Write that reasoning in a comment
rather than fiddling with signs until the sample passes.

The consequence: when `last == n`, the decrement lands at index `n`, one past
the answer array. Either size `diff` as `n + 1` and drop the tail — which is
what the code below does, because it needs no branch — or guard with
`if last < n`. Any booking covering the final flight exposes this, so
`[[1, 3, 5]]` with `n = 3` belongs in your test list. It is also the case an
interviewer will hand you.
""",
        ),
    ],
}


def corp_flight_bookings(bookings: list[list[int]], n: int) -> list[int]:
    # One extra slot so a booking ending at flight n has somewhere to cancel.
    diff = [0] * (n + 1)

    for first, last, seats in bookings:
        diff[first - 1] += seats  # 1-indexed flight -> 0-indexed slot
        diff[last] -= seats  # (last - 1) + 1: one past the range

    running = 0
    answer = []
    for i in range(n):
        running += diff[i]
        answer.append(running)

    return answer


CASES = [
    (([[1, 2, 10], [2, 3, 20], [2, 5, 25]], 5), [10, 55, 45, 25, 25]),
    (([[1, 2, 10], [2, 2, 15]], 2), [10, 25]),
    (([[1, 3, 5]], 3), [5, 5, 5]),
    (([[3, 3, 7]], 3), [0, 0, 7]),
    (([[2, 4, 3], [1, 5, 2]], 5), [2, 5, 5, 5, 2]),
    (([[1, 1, 1], [1, 1, 2], [1, 1, 3]], 1), [6]),
    (([], 3), [0, 0, 0]),
]


def solve(bookings: list[list[int]], n: int) -> list[int]:
    return corp_flight_bookings(bookings, n)  # reads bookings, never writes them
