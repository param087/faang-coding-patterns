"""Queue Reconstruction by Height — LeetCode 406."""

from __future__ import annotations

META = {
    "pattern": "sorting",
    "insight": "Seat the tallest first and everyone shorter becomes invisible to them, so k stops being a count and becomes an insert index.",
    "time": "O(n²) — n insertions into a list",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Each person is `[h, k]`: height `h`, and `k` people of height **at least** `h`
standing in front of them. The input is shuffled; rebuild the queue that
satisfies every pair at once.

Ask about two things:

- **Heights repeat.** They do, and equal heights count each other — that `>=`
  rather than `>` is what forces a tie-break rule and is where most wrong
  answers start.
- **Is the input guaranteed consistent?** On LeetCode yes, and the resulting
  queue is unique, so you are reconstructing rather than searching.

Sorting by height alone gets you nothing: `k` is defined relative to a queue you
have not built yet. The trick is choosing an order in which `k` stops moving.
""",
        ),
        (
            "The insight",
            """
Process people from **tallest to shortest**. Then, at the moment you place
someone, every person already in the line is at least as tall as they are — so
"people at least as tall in front of me" equals "people in front of me", and `k`
is literally the index to insert at.

The part that makes it work is what happens *afterwards*. Everyone inserted
later is strictly shorter, so they do not contribute to anyone's count no matter
where they land. Each person's `k` is correct the instant it is placed and stays
correct forever. That monotone property is the answer; the code is three lines.

**Ties must go ascending by `k`.** Equal heights *do* see each other, so among a
group of the same height the one with the smaller `k` has to be seated first —
`[5,0]` before `[5,2]`. Sort by `(-h, k)` and insert at `k`:

```python
for h, k in sorted(people, key=lambda p: (-p[0], p[1])):
    queue.insert(k, [h, k])
```

Reverse the tie order and you insert `[5,2]` first at index 2 of a list that is
too short, silently appending it and corrupting the count for `[5,0]`.
""",
        ),
        (
            "The cost of `insert`, and the O(n log n) follow-up",
            """
`list.insert` is O(n): it shifts every element to the right of the insertion
point. So this is **O(n²)** despite looking linear. With `n <= 2000` that is at
most 4·10⁶ pointer moves in C — genuinely fast, and the right answer to write.
Say the bound anyway; being wrong about the complexity of your own code is worse
than the complexity.

The follow-up when they push: go the other way. Sort **shortest first**, ties by
`k` descending, and place each person into the `(k + 1)`-th still-empty slot —
every taller person is placed later and will land somewhere else, so the empty
slots ahead are exactly the ones taller people will fill. Finding the
`(k + 1)`-th empty slot is a "k-th zero" query over a prefix-sum structure: a
Fenwick tree with binary search does it in O(log n), giving **O(n log n)**
overall. That is real work for a constant-factor win at n = 2000, which is why
it stays a follow-up.

One purity trap in the simple version: the pairs you insert are the caller's
inner lists. Nothing here mutates them, but if you later "fix up" a value in
place you have quietly rewritten the input.
""",
        ),
    ],
}


def reconstruct_queue(people: list[list[int]]) -> list[list[int]]:
    queue: list[list[int]] = []

    # Tallest first; among equal heights, smallest k first — they see each other.
    for height, in_front in sorted(people, key=lambda person: (-person[0], person[1])):
        queue.insert(in_front, [height, in_front])

    return queue


CASES = [
    (
        ([[7, 0], [4, 4], [7, 1], [5, 0], [6, 1], [5, 2]],),
        [[5, 0], [7, 0], [5, 2], [6, 1], [4, 4], [7, 1]],
    ),
    (
        ([[6, 0], [5, 0], [4, 0], [3, 2], [2, 2], [1, 4]],),
        [[4, 0], [5, 0], [2, 2], [3, 2], [1, 4], [6, 0]],
    ),
    # Two heights, two of each: the case that fails if ties sort by k descending.
    (([[5, 0], [5, 1], [4, 0], [4, 1]],), [[4, 0], [4, 1], [5, 0], [5, 1]]),
    # Every height identical, so k is just the final position.
    (([[3, 2], [3, 0], [3, 1]],), [[3, 0], [3, 1], [3, 2]]),
    (([[2, 0], [1, 1]],), [[2, 0], [1, 1]]),
    (([[1, 0]],), [[1, 0]]),
    (([],), []),
]


def solve(people: list[list[int]]) -> list[list[int]]:
    # Fresh inner lists so the cases survive repeated runs.
    return [list(person) for person in reconstruct_queue(people)]


def check() -> None:
    for args, expected in CASES:
        assert solve(*args) == expected, args

    # The reconstruction must satisfy every person's own count, not just match.
    for args, _ in CASES:
        queue = solve(*args)
        for index, (height, in_front) in enumerate(queue):
            taller = sum(1 for other, _k in queue[:index] if other >= height)
            assert taller == in_front, (queue, index)

    original = [[7, 0], [4, 4], [7, 1]]
    solve(original)
    assert original == [[7, 0], [4, 4], [7, 1]]
