"""Design HashMap — LeetCode 706."""

from __future__ import annotations

META = {
    "pattern": "design",
    "symbol": "MyHashMap",
    "insight": "A hash map is an array of buckets plus a collision policy; pick the policy out loud and the code writes itself.",
    "time": "O(1) expected per operation, O(n / buckets) worst case",
    "space": "O(buckets + n)",
    "sections": [
        (
            "What it asks",
            """
Implement `put`, `get` and `remove` on integer keys without using the language's
built-in map. `get` returns −1 when the key is absent.

Ask two things before writing: **are keys bounded** (LeetCode says
0 ≤ key ≤ 10⁶, which makes a flat 10⁶-slot array legal but a poor answer to a
question about hashing), and **must it resize** (say you would in production,
then fix the bucket count so the interviewer sees the collision logic).
""",
        ),
        (
            "The insight",
            """
Every hash map is the same three decisions:

1. **A hash** — `key % B` is fine here because the keys are already integers.
2. **A bucket count** — use a **prime** such as 769. Powers of two throw away
   the high bits of the key, so strided keys (all multiples of 100, say) pile
   into a handful of buckets.
3. **A collision policy** — separate chaining (a list per bucket) or open
   addressing (probe the next slot). Chaining is the one to write under time
   pressure: deletion is a list removal, not a tombstone.

With 769 buckets and 10⁴ keys the average chain is 13 entries, so a linear scan
of a bucket is genuinely cheap. Say that number — it is the justification for
not building a tree per bucket.
""",
        ),
        (
            "The three bugs graders look for",
            """
- **`put` on an existing key must overwrite, not append.** Scan the bucket
  first. A chain holding both `(5, 1)` and `(5, 2)` makes `get(5)` depend on
  insertion order and makes `remove` leave a ghost behind.
- **`remove` on an absent key must be a no-op**, not an exception.
- **A stored value of −1 is indistinguishable from a miss** under this API.
  LeetCode bounds values at ≥ 0 so it never bites, but naming it shows you read
  the contract — the fix is a sentinel object or a `(found, value)` pair.

Chains hold `[key, value]` lists rather than tuples so `put` can overwrite in
place without rebuilding the entry.
""",
        ),
    ],
}


class MyHashMap:
    # Prime: `key % 769` keeps strided keys (multiples of 10, 100, …) spread out.
    _BUCKETS = 769

    def __init__(self) -> None:
        self.buckets: list[list[list[int]]] = [[] for _ in range(self._BUCKETS)]

    def _bucket(self, key: int) -> list[list[int]]:
        return self.buckets[key % self._BUCKETS]

    def put(self, key: int, value: int) -> None:
        bucket = self._bucket(key)
        for entry in bucket:
            if entry[0] == key:
                entry[1] = value  # overwrite; appending would duplicate the key
                return
        bucket.append([key, value])

    def get(self, key: int) -> int:
        for entry in self._bucket(key):
            if entry[0] == key:
                return entry[1]
        return -1

    def remove(self, key: int) -> None:
        bucket = self._bucket(key)
        for index, entry in enumerate(bucket):
            if entry[0] == key:
                bucket.pop(index)
                return  # absent key is a no-op, not an error


def check() -> None:
    hash_map = MyHashMap()
    hash_map.put(1, 1)
    hash_map.put(2, 2)
    assert hash_map.get(1) == 1
    assert hash_map.get(3) == -1  # miss
    hash_map.put(2, 1)  # overwrite, must not append
    assert hash_map.get(2) == 1
    hash_map.remove(2)
    assert hash_map.get(2) == -1
    hash_map.remove(2)  # removing twice is a no-op
    assert hash_map.get(2) == -1

    # Deliberate collisions: these three keys share a bucket.
    collide = MyHashMap()
    for step in range(3):
        collide.put(7 + step * MyHashMap._BUCKETS, step)
    assert [collide.get(7 + s * MyHashMap._BUCKETS) for s in range(3)] == [0, 1, 2]
    collide.remove(7 + MyHashMap._BUCKETS)  # remove the middle of the chain
    assert collide.get(7) == 0
    assert collide.get(7 + MyHashMap._BUCKETS) == -1
    assert collide.get(7 + 2 * MyHashMap._BUCKETS) == 2

    # Boundary keys from the stated constraints.
    edges = MyHashMap()
    edges.put(0, 100)
    edges.put(1_000_000, 200)
    assert edges.get(0) == 100
    assert edges.get(1_000_000) == 200

    # Nothing survives a fresh instance.
    assert MyHashMap().get(1) == -1
