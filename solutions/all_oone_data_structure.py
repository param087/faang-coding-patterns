"""All O`one Data Structure — LeetCode 432."""

from __future__ import annotations

META = {
    "pattern": "design",
    "symbol": "AllOne",
    "insight": "Keep counts in a sorted doubly linked list of buckets; inc and dec move a key one hop, so the ends are always the min and max.",
    "time": "O(1) for inc, dec, getMaxKey and getMinKey",
    "space": "O(distinct keys)",
    "sections": [
        (
            "What it asks",
            """
A multiset of string keys supporting `inc(key)`, `dec(key)`, `getMaxKey()` and
`getMinKey()` — **all four in O(1)**, not amortised, not log.

Ask: what do the getters return when the structure is empty (the empty string);
is `dec` on a key at count 1 a removal (yes — it must vanish, not sit at zero,
or it will be returned as the minimum forever); and is `dec` on an absent key
guaranteed not to happen (LeetCode guarantees it, but say you would make it a
no-op).

A heap gives O(log n) and cannot decrease a key's priority cheaply. A sorted
map gives O(log n). Both are the wrong answer to a question that names O(1)
four times.
""",
        ),
        (
            "The insight",
            """
Counts move by **exactly one**. That is the entire problem: if a key's count
goes 4 → 5, the bucket it belongs in is either the very next one in sorted
order, or it does not exist yet and belongs immediately after. You never search
for the destination — it is one pointer hop away.

So keep a **doubly linked list of buckets sorted by count**, each bucket holding
the set of keys with exactly that count, plus a map `key → its bucket`:

```
head <-> {count 1: "a","c"} <-> {count 4: "b"} <-> tail
```

- `inc(key)`: look at `bucket.next`. If its count is not `count + 1`, splice a
  new bucket in. Move the key across; if the old bucket is now empty, unlink it.
- `dec(key)`: the mirror image with `bucket.prev`, except that count 1 means
  delete the key outright.
- `getMinKey()` is any key in `head.next`; `getMaxKey()` is any key in
  `tail.prev`. The list is sorted by construction, so the extremes are the ends.

Dummy head and tail sentinels remove every "is this the first/last bucket"
branch, exactly as in [LRU Cache](../lru-cache/) — and here there are four
methods that would otherwise each need them.
""",
        ),
        (
            "The invariants that break it",
            """
Three lines carry the correctness, and each has a failure mode that survives
the sample tests:

- **Unlink an emptied bucket, every time.** Leave one behind and `getMinKey`
  returns a key from an empty set — `next(iter(set()))` raises `StopIteration`,
  and in a generator context that becomes a silent wrong answer rather than a
  crash. Delete it in the same statement that empties it.
- **Remove the key from the old bucket *after* adding it to the new one**, or at
  least never leave the `key → bucket` map pointing at a bucket that no longer
  contains it. Anything in between is a structure that fails only on the second
  `inc` of the same key.
- **`dec` at count 1 deletes the key.** Not "sets it to 0". A zero bucket sits
  at the front of the list forever and `getMinKey` returns a key that is no
  longer in the multiset. This is the single most common wrong submission.

Also: the getters must return `""` on an empty structure, and the structure
becomes empty again after the last `dec` — check that the sentinels still point
at each other, because a stale bucket here is invisible until the next `inc`.
""",
        ),
    ],
}


class AllOne:
    class _Bucket:
        __slots__ = ("count", "keys", "next", "prev")

        def __init__(self, count: int = 0) -> None:
            self.count = count
            self.keys: set[str] = set()
            self.prev: AllOne._Bucket = self
            self.next: AllOne._Bucket = self

    def __init__(self) -> None:
        # Sentinels: head is the low end, tail the high end. No edge branches.
        self.head = self._Bucket()
        self.tail = self._Bucket()
        self.head.next = self.tail
        self.tail.prev = self.head
        self.at: dict[str, AllOne._Bucket] = {}

    def _insert_after(self, node: _Bucket, count: int) -> _Bucket:
        fresh = self._Bucket(count)
        fresh.prev, fresh.next = node, node.next
        node.next.prev = fresh
        node.next = fresh
        return fresh

    @staticmethod
    def _unlink(bucket: _Bucket) -> None:
        bucket.prev.next = bucket.next
        bucket.next.prev = bucket.prev

    def inc(self, key: str) -> None:
        current = self.at.get(key)
        anchor = self.head if current is None else current
        target_count = 1 if current is None else current.count + 1

        following = anchor.next
        if following is self.tail or following.count != target_count:
            following = self._insert_after(anchor, target_count)  # one hop, never a search
        following.keys.add(key)
        self.at[key] = following

        if current is not None:
            current.keys.discard(key)
            if not current.keys:
                self._unlink(current)  # never leave an empty bucket

    def dec(self, key: str) -> None:
        current = self.at.get(key)
        if current is None:
            return  # a no-op, not a crash

        if current.count == 1:
            del self.at[key]  # count 0 means gone, not a zero bucket
        else:
            preceding = current.prev
            if preceding is self.head or preceding.count != current.count - 1:
                preceding = self._insert_after(current.prev, current.count - 1)
            preceding.keys.add(key)
            self.at[key] = preceding

        current.keys.discard(key)
        if not current.keys:
            self._unlink(current)

    def getMaxKey(self) -> str:
        highest = self.tail.prev
        return "" if highest is self.head else next(iter(highest.keys))

    def getMinKey(self) -> str:
        lowest = self.head.next
        return "" if lowest is self.tail else next(iter(lowest.keys))


def check() -> None:
    store = AllOne()
    assert store.getMaxKey() == ""  # empty structure
    assert store.getMinKey() == ""

    store.inc("hello")
    store.inc("hello")
    assert store.getMaxKey() == "hello"
    assert store.getMinKey() == "hello"
    store.inc("leet")
    assert store.getMaxKey() == "hello"
    assert store.getMinKey() == "leet"

    # dec at count 1 removes the key entirely; no zero bucket may linger.
    store.dec("leet")
    assert store.getMinKey() == "hello"
    assert store.getMaxKey() == "hello"
    assert "leet" not in store.at

    # Emptying the structure must restore the sentinels.
    store.dec("hello")
    store.dec("hello")
    assert store.getMinKey() == ""
    assert store.getMaxKey() == ""
    assert store.head.next is store.tail
    assert store.tail.prev is store.head
    assert store.at == {}

    # dec on an absent key is a no-op.
    store.dec("ghost")
    assert store.getMinKey() == ""

    # A gap in the counts: buckets must be spliced in, not assumed adjacent.
    gaps = AllOne()
    for _ in range(5):
        gaps.inc("a")
    gaps.inc("b")
    assert (gaps.getMinKey(), gaps.getMaxKey()) == ("b", "a")
    for _ in range(3):
        gaps.inc("b")  # b: 4, a: 5 -> min is b, max is a
    assert (gaps.getMinKey(), gaps.getMaxKey()) == ("b", "a")
    gaps.inc("b")  # both at 5, one shared bucket
    assert gaps.getMinKey() in {"a", "b"}
    assert gaps.getMaxKey() in {"a", "b"}
    assert gaps.head.next is gaps.tail.prev  # exactly one live bucket

    # Walking a key up and back down leaves no debris.
    walk = AllOne()
    for _ in range(20):
        walk.inc("x")
    for _ in range(20):
        walk.dec("x")
    assert walk.getMinKey() == ""
    assert walk.head.next is walk.tail

    # Three keys at distinct counts, then a full teardown of the middle one.
    trio = AllOne()
    for key, times in (("low", 1), ("mid", 2), ("high", 3)):
        for _ in range(times):
            trio.inc(key)
    assert (trio.getMinKey(), trio.getMaxKey()) == ("low", "high")
    trio.dec("mid")
    trio.dec("mid")
    assert "mid" not in trio.at
    assert (trio.getMinKey(), trio.getMaxKey()) == ("low", "high")
    trio.dec("high")
    trio.dec("high")  # high drops to 1, joining low
    assert trio.getMaxKey() in {"low", "high"}
    assert trio.head.next is trio.tail.prev
