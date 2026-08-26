"""Design an Ordered Stream — LeetCode 1656."""

from __future__ import annotations

META = {
    "pattern": "ood",
    "symbol": "OrderedStream",
    "insight": "One pointer that only ever moves forward: each insert either stalls behind a hole or drains everything the hole was blocking.",
    "time": "O(1) amortised per insert — the pointer crosses each slot once",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
A stream of `n` `(id, value)` pairs arrives out of order, ids `1..n`, each id
exactly once. `insert(id, value)` returns the longest run of consecutive values
that is now ready to emit, starting from the first id not yet emitted — often
empty, occasionally a large block.

Ask what the caller guarantees, because it collapses the problem: ids are
unique, in range, and every id eventually arrives. Without uniqueness you would
need an overwrite policy; without the range you would need a hash map instead of
an array; without the completeness promise you would need a timeout for holes
that never fill.

The rest of the interest is in the word "Easy". The trap is treating this as a
sorting or heap problem when a pointer suffices.
""",
        ),
        (
            "The insight",
            """
The output boundary only ever moves **forward**. Once ids `1..p-1` have been
emitted they are gone for good, so a single integer `ptr` — the smallest id
never emitted — is the entire state beyond the buffer itself.

An insert writes into its slot, then advances `ptr` while the slot under it is
filled. Two regimes fall out with no special-casing:

- the arriving id is **greater** than `ptr`: the slot under `ptr` is still
  empty, the loop runs zero times, and the caller gets `[]`;
- the arriving id **is** `ptr`: the loop runs until it hits the next hole,
  handing back everything that had piled up behind this one.

The `while` loop looks like it could be O(n) per call. It cannot: `ptr` only
increases and stops at `n + 1`, so across all `n` inserts the loop body runs
exactly `n` times total. **O(1) amortised**, O(n) for the whole stream — say
this, because "there's a loop inside insert" is the interviewer's first probe.

A min-heap of pending ids also works and is the answer people reach for first.
It is O(log n) per insert and needs a "is the top exactly `ptr`?" test anyway,
so it pays for an ordering the id numbers already gave you for free.
""",
        ),
        (
            "Edge cases",
            """
- **One-based ids.** Size the buffer `n + 1` and ignore index 0 rather than
  subtracting 1 at three call sites; that subtraction is where the off-by-one
  bug lives.
- **The final insert.** Arrivals in reverse order mean `n - 1` empty returns
  and then one call that returns the entire stream. That is correct, and it is
  the case to walk through out loud — worst-case *per call* is O(n) even though
  the amortised cost is O(1).
- **`None` as the empty marker.** Values are non-empty strings here, so `None`
  is unambiguous. If values could be `None`, use a separate filled-flag array;
  a falsy test (`if self.values[ptr]`) would stall forever on an empty string.
- **n = 1.** The single insert returns the whole stream, and `ptr` lands past
  the end — the bound check in the `while` condition is what stops it.
- **Concurrency**, if asked: `insert` is a read-modify-write on shared state, so
  a lock around it, or a per-slot atomic write plus a CAS loop on `ptr`.
""",
        ),
    ],
}


class OrderedStream:
    """A buffer plus the smallest id not yet emitted."""

    def __init__(self, n: int) -> None:
        self.values: list[str | None] = [None] * (n + 1)  # index 0 unused: ids are 1-based
        self.ptr = 1

    def insert(self, idKey: int, value: str) -> list[str]:
        self.values[idKey] = value

        chunk: list[str] = []
        # Drains only what this arrival unblocked; ptr never moves backwards.
        while self.ptr < len(self.values) and self.values[self.ptr] is not None:
            chunk.append(self.values[self.ptr])
            self.ptr += 1
        return chunk


def check() -> None:
    stream = OrderedStream(5)
    assert stream.insert(3, "ccccc") == []
    assert stream.insert(1, "aaaaa") == ["aaaaa"]
    assert stream.insert(2, "bbbbb") == ["bbbbb", "ccccc"]
    assert stream.insert(5, "eeeee") == []
    assert stream.insert(4, "ddddd") == ["ddddd", "eeeee"]
    assert stream.ptr == 6  # exhausted, pointer parked one past the last id

    # Worst case per call: everything arrives backwards, one giant final chunk.
    reverse = OrderedStream(4)
    assert reverse.insert(4, "d") == []
    assert reverse.insert(3, "c") == []
    assert reverse.insert(2, "b") == []
    assert reverse.insert(1, "a") == ["a", "b", "c", "d"]

    # Already in order: every call emits exactly one value.
    forward = OrderedStream(3)
    assert forward.insert(1, "a") == ["a"]
    assert forward.insert(2, "b") == ["b"]
    assert forward.insert(3, "c") == ["c"]

    # n = 1, and the pointer must stop at the end rather than run off it.
    single = OrderedStream(1)
    assert single.insert(1, "only") == ["only"]

    # A hole in the middle stalls everything behind it until it is filled.
    holed = OrderedStream(4)
    assert holed.insert(1, "a") == ["a"]
    assert holed.insert(3, "c") == []
    assert holed.insert(4, "d") == []
    assert holed.insert(2, "b") == ["b", "c", "d"]
