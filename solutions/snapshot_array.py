"""Snapshot Array — LeetCode 1146."""

from __future__ import annotations

from bisect import bisect_right

META = {
    "pattern": "design",
    "symbol": "SnapshotArray",
    "insight": "Never copy the array: store a per-index history of (snap_id, value) and binary-search it, so a snap is a single counter increment.",
    "time": "O(1) set and snap, O(log w) get in the writes to that index",
    "space": "O(total writes)",
    "sections": [
        (
            "What it asks",
            """
An array of `length` zeros with `set(index, value)`, `snap()` returning an
increasing snapshot id, and `get(index, snap_id)` returning the value that
index held at that snapshot.

Ask: **is `snap_id` always a snapshot that already happened?** (Yes — you never
query the future.) Are old snapshots ever dropped? Both `length` and the call
count go to 5·10⁴.
""",
        ),
        (
            "The insight",
            """
The literal reading — copy the array on every `snap` — is O(length) per
snapshot. At 5·10⁴ elements and 5·10⁴ snaps that is **2.5·10⁹ cell copies**,
and roughly 20 GB if you keep them all. It is not a small constant-factor
problem; it is the wrong shape.

Invert it. A snapshot is not a copy of the array, it is a **point in time**, so
`snap` only has to increment a counter. The data lives per index: each index
keeps its own append-only list of `(snap_id, value)` pairs, and because
`snap_id` never decreases, that list is already sorted.

`get(index, snap_id)` is then the same query as Time Based Key-Value Store —
binary-search for the last write at or before that id, `bisect_right - 1`.
Total memory is O(number of `set` calls), independent of `length`.
""",
        ),
        (
            "Three ways to get it wrong",
            """
1. **Two writes inside the same snapshot.** `set(0, 1); set(0, 2); snap()`
   must record 2, not two entries under the same id. Overwrite the last pair
   when its id equals the current one — otherwise `bisect_right - 1` lands on
   whichever duplicate the search happens to hit.
2. **An index never written.** Without a sentinel, the history is empty and the
   binary search returns index −1, which in Python silently reads the *last*
   entry. Seed every index with `(-1, 0)` and the case disappears.
3. **`bisect_left` instead of `bisect_right`.** The exact-match snapshot must
   be included, so you need the first id **strictly greater**, minus one.
""",
        ),
    ],
}


class SnapshotArray:
    def __init__(self, length: int) -> None:
        self.snap_id = 0
        # Sentinel (-1, 0): every index reads as 0 before its first write.
        self.history: list[list[tuple[int, int]]] = [[(-1, 0)] for _ in range(length)]

    def set(self, index: int, value: int) -> None:
        record = self.history[index]
        if record[-1][0] == self.snap_id:
            record[-1] = (self.snap_id, value)  # same snapshot: overwrite
        else:
            record.append((self.snap_id, value))

    def snap(self) -> int:
        self.snap_id += 1
        return self.snap_id - 1  # the id of the snapshot just taken

    def get(self, index: int, snap_id: int) -> int:
        record = self.history[index]
        # Last write at or before snap_id; the sentinel keeps this in range.
        position = bisect_right(record, snap_id, key=lambda entry: entry[0]) - 1
        return record[position][1]


CASES: list[tuple[tuple, object]] = []


def check() -> None:
    array = SnapshotArray(3)
    array.set(0, 5)
    assert array.snap() == 0
    array.set(0, 6)
    assert array.get(0, 0) == 5  # the snapshot, not the current value
    assert array.snap() == 1
    assert array.get(0, 1) == 6

    # Two writes inside one snapshot: only the later one survives.
    same_snap = SnapshotArray(1)
    same_snap.set(0, 1)
    same_snap.set(0, 2)
    assert same_snap.snap() == 0
    assert same_snap.get(0, 0) == 2

    # An index that was never written reads as zero at every snapshot.
    untouched = SnapshotArray(2)
    untouched.set(0, 9)
    untouched.snap()
    untouched.snap()
    assert untouched.get(1, 0) == 0
    assert untouched.get(1, 1) == 0

    # A query older than the first write to that index.
    late_write = SnapshotArray(1)
    late_write.snap()  # id 0
    late_write.snap()  # id 1
    late_write.set(0, 4)
    assert late_write.snap() == 2
    assert late_write.get(0, 0) == 0
    assert late_write.get(0, 1) == 0
    assert late_write.get(0, 2) == 4

    # Consecutive snaps with no writes between them share a value.
    quiet = SnapshotArray(1)
    quiet.set(0, 7)
    ids = [quiet.snap() for _ in range(4)]
    assert ids == [0, 1, 2, 3]
    assert [quiet.get(0, i) for i in ids] == [7, 7, 7, 7]

    # Many writes across many snapshots, read back in a scrambled order.
    long_run = SnapshotArray(2)
    for step in range(50):
        long_run.set(step % 2, step)
        long_run.snap()
    assert long_run.get(0, 49) == 48
    assert long_run.get(1, 49) == 49
    assert long_run.get(1, 0) == 0  # index 1 unwritten at snapshot 0
    assert long_run.get(0, 10) == 10
