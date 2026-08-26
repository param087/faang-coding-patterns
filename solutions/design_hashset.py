"""Design HashSet — LeetCode 705."""

from __future__ import annotations

META = {
    "pattern": "design",
    "symbol": "MyHashSet",
    "insight": "Keys are integers bounded by 10⁶, so the honest answer is chaining — and the sharp one is a 125 KB bitset.",
    "time": "O(1) expected per operation",
    "space": "O(buckets + n) chained, or a flat 125 KB bitset",
    "sections": [
        (
            "What it asks",
            """
Implement `add`, `remove` and `contains` on integer keys without the built-in
set. Adding twice is idempotent; removing something absent is a no-op.

Ask for the key range. Here it is 0 ≤ key ≤ 10⁶ — bounded, which unlocks the
second answer below and is the only reason it is legal.
""",
        ),
        (
            "The insight",
            """
A set is a map with the value thrown away, so the shape is identical: hash to a
bucket, then resolve collisions. Chaining with a **prime** bucket count (769)
is the version to write, because deletion is a list removal rather than an open
addressing tombstone.

The interesting part is the bound. With keys in `[0, 10⁶]` a **bitset** is
exact and enormous only in theory: 10⁶ bits is 125 000 bytes — 125 KB, one
`bytearray`, no hashing, no collisions, and `contains` is two shifts and a mask.

```
index, offset = key >> 3, key & 7
bits[index] & (1 << offset)
```

Offer both: "chaining is the general answer; given the stated bound a 125 KB
bitset is strictly better and has no worst case." That contrast is the whole
question at this difficulty.
""",
        ),
        (
            "Follow-ups",
            """
- **"What if the load factor climbs?"** Resize: allocate `2·B + 1` buckets and
  rehash every key. Amortised O(1), but note the **rehash cannot be skipped** —
  bucket index depends on `B`, so entries must move.
- **"Why not `key % 1024`?"** A power-of-two modulus keeps only the low bits.
  Keys that are all multiples of 1024 collide into one bucket and every
  operation degrades to O(n).
- **Open addressing** is faster in cache terms but deletion needs tombstones,
  and tombstones accumulate until you rehash. Say that and move on.
- **Non-integer keys** need a real hash (FNV-1a, or Python's `hash`) plus
  `__eq__` on the stored key — hash equality is not key equality.
""",
        ),
    ],
}


class MyHashSet:
    # Prime bucket count: a power of two would discard the key's high bits.
    _BUCKETS = 769

    def __init__(self) -> None:
        self.buckets: list[list[int]] = [[] for _ in range(self._BUCKETS)]

    def _bucket(self, key: int) -> list[int]:
        return self.buckets[key % self._BUCKETS]

    def add(self, key: int) -> None:
        bucket = self._bucket(key)
        if key not in bucket:  # idempotent: a second add must not duplicate
            bucket.append(key)

    def remove(self, key: int) -> None:
        bucket = self._bucket(key)
        if key in bucket:
            bucket.remove(key)  # absent key is a no-op

    def contains(self, key: int) -> bool:
        return key in self._bucket(key)


class BitsetHashSet:
    """The bounded-key answer: 10**6 + 1 bits = ~125 KB, no collisions at all."""

    def __init__(self, limit: int = 10**6) -> None:
        self.bits = bytearray((limit >> 3) + 1)

    def add(self, key: int) -> None:
        self.bits[key >> 3] |= 1 << (key & 7)

    def remove(self, key: int) -> None:
        self.bits[key >> 3] &= ~(1 << (key & 7))

    def contains(self, key: int) -> bool:
        return bool(self.bits[key >> 3] & (1 << (key & 7)))


def check() -> None:
    for factory in (MyHashSet, BitsetHashSet):
        hash_set = factory()
        hash_set.add(1)
        hash_set.add(2)
        assert hash_set.contains(1)
        assert not hash_set.contains(3)
        hash_set.add(2)  # idempotent
        assert hash_set.contains(2)
        hash_set.remove(2)
        assert not hash_set.contains(2)
        hash_set.remove(2)  # removing twice is a no-op
        assert not hash_set.contains(2)
        assert hash_set.contains(1)

        # Boundary keys from the stated constraints.
        hash_set.add(0)
        hash_set.add(1_000_000)
        assert hash_set.contains(0)
        assert hash_set.contains(1_000_000)
        hash_set.remove(0)
        assert not hash_set.contains(0)
        assert hash_set.contains(1_000_000)

        assert not factory().contains(1)

    # Deliberate collisions in the chained version: same bucket, distinct keys.
    collide = MyHashSet()
    keys = [11 + step * MyHashSet._BUCKETS for step in range(3)]
    for key in keys:
        collide.add(key)
    assert all(collide.contains(key) for key in keys)
    collide.remove(keys[1])  # remove from the middle of the chain
    assert collide.contains(keys[0])
    assert not collide.contains(keys[1])
    assert collide.contains(keys[2])
