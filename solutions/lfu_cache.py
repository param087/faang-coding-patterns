"""LFU Cache — LeetCode 460."""

from __future__ import annotations

from collections import OrderedDict, defaultdict

META = {
    "pattern": "design",
    "symbol": "LFUCache",
    "insight": "Bucket keys by use count and keep each bucket in LRU order; the minimum count then only ever resets to 1 or rises by one.",
    "time": "O(1) for get and put",
    "space": "O(capacity)",
    "sections": [
        (
            "What it asks",
            """
A fixed-capacity cache evicting the **least frequently used** key, breaking
ties by **least recently used**. Both `get` and `put` must be O(1) — the
problem states it, which is the whole difficulty.

Ask, and the answers matter:

- **Does `get` increment the use count?** Yes. So does a `put` that updates an
  existing key.
- **Does a new key start at count 1?** Yes, counted as its first use — this is
  why `min_freq` is set to 1 after every insert.
- **What breaks a tie?** LRU within the same count. Without this the problem is
  ambiguous, and half the wrong submissions are wrong about exactly this.
- **Can capacity be 0?** Yes, and then nothing is ever stored.
""",
        ),
        (
            "The wrong first answers, with numbers",
            """
**Scan for the minimum on eviction.** A dict of `key → (value, count)`, and on
a full `put` you walk every entry to find the smallest count. Correct, and
O(capacity) per eviction: capacity 10⁴ with 2·10⁵ calls is **2·10⁹**
comparisons. Dead.

**A min-heap keyed by (count, timestamp).** O(log n) per operation, and worse,
`get` has to *update* a key's priority — which a binary heap cannot do without
either a hand-maintained index map or lazy deletion that lets the heap grow to
the number of operations rather than the capacity. It is a defensible fallback
if you are stuck at minute 30; it is not the answer to a question that says
O(1).

**LRU with counts bolted on.** Recency order and frequency order are different
orders. One doubly linked list cannot express both.
""",
        ),
        (
            "The insight: a bucket per count",
            """
Group keys by their use count. Each group holds the keys with that exact count,
**ordered by recency**:

```
counts:  key -> use count
buckets: use count -> ordered collection of keys (oldest first)
min_freq: the smallest count currently populated
```

A use is now a **move between adjacent buckets**: delete the key from
`buckets[c]`, append it to `buckets[c + 1]`. Both are O(1). Eviction is
`buckets[min_freq]`'s oldest key — also O(1), because the bucket is already in
recency order.

In Python an `OrderedDict` *is* that ordered collection: insertion order gives
recency, and `popitem(last=False)` pops the oldest in O(1). In an interview,
say "each bucket is a doubly linked list with a hash map into its nodes — I am
writing `OrderedDict` because that is precisely what it is". You will be asked
to justify it; that sentence is the justification.
""",
        ),
        (
            "Why `min_freq` never needs a search",
            """
This is the pivot of the whole problem, and the part worth saying before you
write a line of code. `min_freq` can only change in two ways:

1. **After an insert** it is 1, because the new key has count 1 and nothing can
   be lower.
2. **After a use** of a key whose count was `min_freq`, *if that bucket is now
   empty*, the new minimum is exactly `min_freq + 1` — the key you just touched
   is sitting there. It cannot skip past that, because the only way out of a
   bucket is one step up.

So `min_freq` is maintained with `+= 1` and never with a scan. If you find
yourself writing `min(buckets)`, you have lost the O(1) guarantee — and that
line is where interviewers stop the clock.

The matching detail: **delete the bucket when it empties.** A left-behind empty
`OrderedDict` makes `min_freq` point at nothing, and the next eviction pops
from an empty container.
""",
        ),
        (
            "The tie-break, and where the code hides it",
            """
Within `buckets[min_freq]`, the victim is the **oldest**, which is the front.
This is invisible in the code — it is one keyword, `last=False` — and it is
half the marks:

```
victim, _ = self.buckets[self.min_freq].popitem(last=False)
```

The other half is that a key re-inserted into `buckets[c + 1]` lands at the
**back**, marking it as the most recent at its new count. Both halves come free
from `OrderedDict`; with a hand-rolled list you must remember which end is
which, and mixing them up produces a cache that passes the sample and fails on
any test with a tie.
""",
        ),
        (
            "Dry run",
            """
Capacity 2.

- `put(1,1)`, `put(2,2)` → `buckets[1] = [1, 2]`, `min_freq = 1`.
- `get(1)` → 1. Key 1 moves to `buckets[2]`. `buckets[1] = [2]`, still
  non-empty, so `min_freq` stays 1.
- `put(3,3)` → full. Evict the front of `buckets[1]` → **key 2**. Insert 3 at
  count 1, `min_freq = 1`.
- `get(2)` → −1. `get(3)` → 3, and now `buckets[1]` **empties**, so
  `min_freq` becomes 2. `buckets[2] = [1, 3]`.
- `put(4,4)` → full. Evict the front of `buckets[2]` → **key 1**, because 1 and
  3 are tied at count 2 and 1 was used longer ago.
- `get(1)` → −1, `get(3)` → 3, `get(4)` → 4.

The last eviction is the case a frequency-only implementation gets wrong: both
candidates have count 2, and only the recency order inside the bucket decides
it.
""",
        ),
        (
            "Follow-ups",
            """
- **"Counts grow without bound over a long run."** They do, and an item that
  was hot at 3 a.m. is unevictable at noon. Real caches **age** the counts —
  halve every count periodically, or use a windowed count. Naming *LFU with
  dynamic ageing* here is the answer they want.
- **Production.** Nobody ships exact LFU. **TinyLFU / W-TinyLFU** (Caffeine,
  and Go's Ristretto) approximates the counts with a count-min sketch plus a
  small LRU window, which costs a few bits per key instead of a bucket
  structure, and beats exact LFU on real traces.
- **Thread safety.** Every operation mutates three structures, so a single lock
  is the honest first answer; striping by `hash(key)` reduces contention but the
  global `min_freq` becomes the shared bottleneck — a real argument for
  sharding the *whole cache* into N independent LFUs.
- **"Do it without `OrderedDict`."** Doubly linked list per bucket plus
  `key → node`; the structure is identical, only longer. See
  [LRU Cache](../lru-cache/) for the node plumbing.
""",
        ),
    ],
}


class LFUCache:
    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self.values: dict[int, int] = {}
        self.counts: dict[int, int] = {}
        # count -> keys with that count, oldest first (OrderedDict == DLL + map).
        self.buckets: defaultdict[int, OrderedDict[int, None]] = defaultdict(OrderedDict)
        self.min_freq = 0

    def _touch(self, key: int) -> None:
        count = self.counts[key]
        bucket = self.buckets[count]
        del bucket[key]
        if not bucket:
            del self.buckets[count]  # never leave an empty bucket behind
            if self.min_freq == count:
                self.min_freq = count + 1  # can only rise by exactly one
        self.counts[key] = count + 1
        self.buckets[count + 1][key] = None  # to the back: most recent at its new count

    def get(self, key: int) -> int:
        if key not in self.values:
            return -1
        self._touch(key)  # a read is a use
        return self.values[key]

    def put(self, key: int, value: int) -> None:
        if self.capacity <= 0:
            return

        if key in self.values:
            self.values[key] = value
            self._touch(key)  # an update is a use, and must not grow the cache
            return

        if len(self.values) >= self.capacity:
            victim, _ = self.buckets[self.min_freq].popitem(last=False)  # LRU tie-break
            if not self.buckets[self.min_freq]:
                del self.buckets[self.min_freq]
            del self.values[victim]
            del self.counts[victim]

        self.values[key] = value
        self.counts[key] = 1
        self.buckets[1][key] = None
        self.min_freq = 1  # a fresh key is always the new minimum


def check() -> None:
    cache = LFUCache(2)
    cache.put(1, 1)
    cache.put(2, 2)
    assert cache.get(1) == 1
    cache.put(3, 3)  # evicts 2: count 1 vs count 2
    assert cache.get(2) == -1
    assert cache.get(3) == 3
    cache.put(4, 4)  # 1 and 3 both at count 2 -> evict 1, the older use
    assert cache.get(1) == -1
    assert cache.get(3) == 3
    assert cache.get(4) == 4

    # Pure LRU tie-break: everything sits at count 1.
    tied = LFUCache(3)
    tied.put(1, 1)
    tied.put(2, 2)
    tied.put(3, 3)
    tied.put(4, 4)  # all tied at 1 -> evict the oldest, key 1
    assert tied.get(1) == -1
    assert [tied.get(2), tied.get(3), tied.get(4)] == [2, 3, 4]

    # A put that updates an existing key counts as a use and must not evict.
    updated = LFUCache(2)
    updated.put(1, 1)
    updated.put(2, 2)
    updated.put(1, 10)  # key 1 now at count 2
    updated.put(3, 3)  # evicts 2
    assert updated.get(2) == -1
    assert updated.get(1) == 10
    assert updated.get(3) == 3

    # A miss must not create state that later corrupts min_freq.
    missing = LFUCache(2)
    assert missing.get(9) == -1
    missing.put(1, 1)
    assert missing.get(9) == -1
    assert missing.get(1) == 1
    missing.put(2, 2)
    missing.put(3, 3)  # evicts 2 (count 1), not 1 (count 2)
    assert missing.get(2) == -1
    assert missing.get(1) == 1

    # Capacity 1: every put replaces.
    single = LFUCache(1)
    single.put(1, 1)
    assert single.get(1) == 1
    single.put(2, 2)
    assert single.get(1) == -1
    assert single.get(2) == 2

    # Capacity 0 stores nothing and must not crash.
    empty = LFUCache(0)
    empty.put(1, 1)
    assert empty.get(1) == -1

    # A long run: the hot key survives a stream of one-shot keys.
    hot = LFUCache(3)
    hot.put(0, 0)
    for round_index in range(50):
        assert hot.get(0) == 0
        hot.put(round_index + 1, round_index + 1)
    assert hot.get(0) == 0
    assert len(hot.values) == 3
    assert all(hot.buckets.values())  # no empty bucket left behind
