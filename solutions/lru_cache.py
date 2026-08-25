"""LRU Cache — LeetCode 146."""

from __future__ import annotations

META = {
    "pattern": "design",
    "symbol": "LRUCache",
    "insight": "A hash map for O(1) lookup plus a doubly linked list for O(1) reordering — neither alone can meet the contract.",
    "time": "O(1) for get and put",
    "space": "O(capacity)",
    "sections": [
        (
            "What it asks",
            """
A fixed-capacity cache with `get(key)` and `put(key, value)`, **both O(1)**.
When full, evict the least recently used entry.

Ask: does `get` count as a use (yes); does updating an existing key count as a
use (yes, and it must not grow the size); what does `get` return on a miss
(−1); can capacity be zero; is it thread-safe.
""",
        ),
        (
            "Name the structures before writing anything",
            """
This is the move that makes the whole question easy:

> "O(1) for both operations rules out anything sorted. I need a hash map for
> lookup and a doubly linked list for recency order."

Say that, draw the two structures with an arrow from a map entry to a list
node, and the interviewer will visibly relax — you have solved it before
touching the keyboard.

**Why neither alone works:** a hash map has no order. A linked list has no
O(1) lookup. Together, the map hands you the node in O(1) and the list lets
you splice it to the front in O(1).
""",
        ),
        (
            "Why doubly linked",
            """
Removing a node from a **singly** linked list requires its predecessor, which
is O(n) to find. If you catch yourself writing a scan, that is the signal you
need the back-pointer.
""",
        ),
        (
            "Sentinels",
            """
The head and tail are dummy nodes that hold no data.

Without them, `_unlink` needs to handle "is this the first node", "is this the
last", and "is this the only one" — three special cases, and they are where
the bugs live. Two extra nodes delete all of them, and every splice becomes
four unconditional pointer assignments.
""",
        ),
        (
            "Dry run",
            """
Capacity 2.

- `put(1,1)`, `put(2,2)` → list is `2, 1` (most recent first).
- `get(1)` → 1, **and 1 moves to the front** → `1, 2`.
- `put(3,3)` → full, evict the tail → evicts **2, not 1**.
- `get(2)` → −1. `get(3)` → 3.

That eviction is the entire point of the question. Run it explicitly.
""",
        ),
        (
            "Follow-ups",
            """
- **"In production?"** `OrderedDict` with `move_to_end`, or a plain dict in
  Python 3.7+. Say you know it exists — then write it out, because writing it
  out is the question.
- **Thread safety** — a lock around the whole structure, or striped locks for
  less contention. See [Concurrency](../../patterns/concurrency/).
- **LFU Cache** — the natural next question, and genuinely harder: it needs a
  frequency→bucket map and an O(1)-maintainable minimum frequency.
""",
        ),
    ],
}


class LRUCache:
    class _Node:
        __slots__ = ("key", "next", "prev", "value")

        def __init__(self, key: int = 0, value: int = 0) -> None:
            self.key = key
            self.value = value
            self.prev: LRUCache._Node | None = None
            self.next: LRUCache._Node | None = None

    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self.map: dict[int, LRUCache._Node] = {}
        # Sentinels: every splice becomes unconditional.
        self.head = self._Node()  # most recent side
        self.tail = self._Node()  # least recent side
        self.head.next = self.tail
        self.tail.prev = self.head

    def _unlink(self, node: _Node) -> None:
        if node.prev:
            node.prev.next = node.next
        if node.next:
            node.next.prev = node.prev

    def _push_front(self, node: _Node) -> None:
        node.prev = self.head
        node.next = self.head.next
        if self.head.next:
            self.head.next.prev = node
        self.head.next = node

    def get(self, key: int) -> int:
        node = self.map.get(key)
        if node is None:
            return -1
        self._unlink(node)
        self._push_front(node)  # touching it makes it most recent
        return node.value

    def put(self, key: int, value: int) -> None:
        if self.capacity <= 0:
            return  # a zero-capacity cache holds nothing

        existing = self.map.get(key)
        if existing:
            existing.value = value
            self._unlink(existing)
            self._push_front(existing)
            return

        if len(self.map) >= self.capacity:
            victim = self.tail.prev
            if victim and victim is not self.head:
                self._unlink(victim)
                del self.map[victim.key]

        node = self._Node(key, value)
        self.map[key] = node
        self._push_front(node)


CASES: list[tuple[tuple, object]] = []


def check() -> None:
    cache = LRUCache(2)
    cache.put(1, 1)
    cache.put(2, 2)
    assert cache.get(1) == 1  # 1 becomes most recent
    cache.put(3, 3)  # evicts 2, not 1
    assert cache.get(2) == -1
    assert cache.get(3) == 3
    cache.put(4, 4)  # evicts 1
    assert cache.get(1) == -1
    assert cache.get(3) == 3
    assert cache.get(4) == 4

    # Updating an existing key counts as a use and must not grow the cache.
    other = LRUCache(2)
    other.put(1, 1)
    other.put(2, 2)
    other.put(1, 10)
    other.put(3, 3)  # 2 is now least recent
    assert other.get(2) == -1
    assert other.get(1) == 10

    single = LRUCache(1)
    single.put(1, 1)
    single.put(2, 2)
    assert single.get(1) == -1
    assert single.get(2) == 2

    empty = LRUCache(0)
    empty.put(1, 1)
    assert empty.get(1) == -1
