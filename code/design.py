"""Data-structure design.

The category no popular list has a bucket for, and one of the highest
frequency at SDE-2. The question is never "what algorithm" — it is **which
two structures do I combine to hit the stated complexity contract**.

Almost always: a hash map for O(1) lookup, plus something else that maintains
an order the hash map cannot.
"""

from __future__ import annotations

from bisect import bisect_right
from collections import defaultdict


class LRUCache:
    """get and put in O(1).

    Hash map plus a doubly linked list. The map gives O(1) lookup; the list
    gives O(1) reordering. Neither alone is enough — that pairing *is* the
    answer, and saying so before writing is what the interviewer wants.

    Sentinel head and tail nodes remove every null check from the splice
    operations, which is where the bugs otherwise live.
    """

    class _Node:
        __slots__ = ("key", "value", "prev", "next")

        def __init__(self, key: int = 0, value: int = 0) -> None:
            self.key = key
            self.value = value
            self.prev: LRUCache._Node | None = None
            self.next: LRUCache._Node | None = None

    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self.map: dict[int, LRUCache._Node] = {}
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


class TimeMap:
    """set(key, value, timestamp) and get(key, timestamp) → latest value at or before.

    Timestamps arrive in increasing order, so each key's list is already
    sorted and a binary search answers the query. `bisect_right` minus one is
    the "largest entry not exceeding t" idiom — worth recognising, because
    getting it off by one returns the wrong version.
    """

    def __init__(self) -> None:
        self.store: dict[str, tuple[list[int], list[str]]] = defaultdict(lambda: ([], []))

    def set(self, key: str, value: str, timestamp: int) -> None:
        times, values = self.store[key]
        times.append(timestamp)
        values.append(value)

    def get(self, key: str, timestamp: int) -> str:
        if key not in self.store:
            return ""
        times, values = self.store[key]
        index = bisect_right(times, timestamp) - 1
        return values[index] if index >= 0 else ""


class RandomizedSet:
    """insert, remove and getRandom, all O(1).

    The tension: a hash set gives O(1) membership but no uniform random pick;
    a list gives O(1) random pick but O(n) removal. Combining them works
    because of one trick — to remove an element, **swap it with the last one**
    and pop, so no shifting is needed.
    """

    def __init__(self) -> None:
        self.values: list[int] = []
        self.index: dict[int, int] = {}

    def insert(self, value: int) -> bool:
        if value in self.index:
            return False
        self.index[value] = len(self.values)
        self.values.append(value)
        return True

    def remove(self, value: int) -> bool:
        position = self.index.get(value)
        if position is None:
            return False
        last = self.values[-1]
        self.values[position] = last
        self.index[last] = position
        self.values.pop()
        del self.index[value]
        return True

    def get_random(self, seed: int) -> int:
        """Deterministic here so the tests are reproducible; use `random.choice`."""
        return self.values[seed % len(self.values)]


CASES: list[tuple[tuple, object]] = []


def check() -> None:
    cache = LRUCache(2)
    cache.put(1, 1)
    cache.put(2, 2)
    assert cache.get(1) == 1  # 1 is now most recent
    cache.put(3, 3)  # evicts 2, not 1
    assert cache.get(2) == -1
    assert cache.get(3) == 3
    cache.put(4, 4)  # evicts 1
    assert cache.get(1) == -1
    assert cache.get(4) == 4

    single = LRUCache(1)
    single.put(1, 1)
    single.put(2, 2)
    assert single.get(1) == -1
    assert single.get(2) == 2

    times = TimeMap()
    times.set("foo", "bar", 1)
    assert times.get("foo", 1) == "bar"
    assert times.get("foo", 3) == "bar"  # latest at or before 3
    times.set("foo", "bar2", 4)
    assert times.get("foo", 4) == "bar2"
    assert times.get("foo", 5) == "bar2"
    assert times.get("foo", 0) == ""  # nothing set that early
    assert times.get("missing", 1) == ""

    randomized = RandomizedSet()
    assert randomized.insert(1) is True
    assert randomized.insert(1) is False
    assert randomized.remove(2) is False
    assert randomized.insert(2) is True
    assert randomized.remove(1) is True
    assert randomized.get_random(0) == 2
    assert randomized.insert(1) is True
    assert sorted(randomized.values) == [1, 2]
