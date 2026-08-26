"""Max Stack — LeetCode 716."""

from __future__ import annotations

from heapq import heappop, heappush

META = {
    "pattern": "design",
    "symbol": "MaxStack",
    "insight": "pop_max deletes from the middle, so the stack has to be a doubly linked list with a heap indexing it — the Min Stack trick cannot do this.",
    "time": "O(log n) push and pop_max, O(1) top, O(log n) amortised peek_max",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
This one is premium, so the statement is not public — in my own words: a stack
with the usual `push`, `pop` and `top`, plus `peek_max` returning the largest
value currently held and `pop_max` **removing** it. When several elements tie
for the maximum, `pop_max` removes the one **closest to the top**.

Ask two things. **What is the required complexity?** Interviewers usually open
with "O(1) except pop_max" and then push for O(log n) everywhere — the two
answers are different structures, so find out which one is being asked for.
And **how are ties broken?** Get it wrong and half the tests fail while the
algorithm looks right.
""",
        ),
        (
            "The insight",
            """
The Min Stack trick — a parallel stack of running maxima — answers `peek_max`
in O(1) and then dies, because `pop_max` removes an element that is **not at
the top** and the running maxima below it are now wrong. Everyone reaches for
it; say why it fails and move on.

The O(n) answer that passes the easy version: pop into a buffer until you find
the max, drop it, push the buffer back. Fine to state, not the target.

For O(log n) you need two capabilities at once — order by *position* and order
by *value* — so use two structures over the same nodes:

- a **doubly linked list** as the stack, because it is the only stack that
  supports removing an interior element in O(1) once you hold the node;
- a **max-heap of `(-value, -serial)`** as an index into it, where `serial` is
  a monotonically increasing push counter.

`pop` and `pop_max` both unlink a node; the heap is not repaired eagerly.
Instead each node has an id in a `live` dict, and the heap top is discarded
while its id is no longer live — **lazy deletion**. Every entry is pushed once
and discarded at most once, so the amortised cost stays O(log n).

`SortedList` of `(value, serial)` is the same idea with less typing if the
interviewer allows a library; the linked list plus heap is the version you can
defend from first principles.
""",
        ),
        (
            "Ties, and what lazy deletion needs",
            """
**The tie-break is the serial.** Packing `(-value, -serial)` makes the heap
prefer, among equal values, the **largest** serial — the most recently pushed,
which is the one nearest the top. Store only the value and `pop_max` on
`[5, 1, 5]` may delete the bottom 5, leaving `top()` at 1 instead of 5.

**Liveness is by identity, not by value.** With duplicates everywhere, "has
this value already been removed?" is unanswerable; "has *this node* already
been removed?" is a dict lookup. Hence the serial as key.

**Purge before reading, not after writing.** `peek_max` must discard dead heap
entries *before* it looks, otherwise it returns the value of an element that
`pop` removed several calls ago. Stale entries are harmless while they sit
there — they only have to be gone at the moment you trust the top.

The subtle one: `pop` leaves a dead entry in the heap, so the heap can grow to
the number of pushes rather than the live size. Bounded and fine here; in a
long-running service you would re-heapify once the dead fraction crosses a
threshold.
""",
        ),
    ],
}


class MaxStack:
    class _Node:
        __slots__ = ("next", "prev", "serial", "value")

        def __init__(self, value: int = 0, serial: int = -1) -> None:
            self.value = value
            self.serial = serial
            self.prev: MaxStack._Node | None = None
            self.next: MaxStack._Node | None = None

    def __init__(self) -> None:
        self.head = self._Node()  # sentinels: no special cases when unlinking
        self.tail = self._Node()  # tail.prev is the top of the stack
        self.head.next = self.tail
        self.tail.prev = self.head
        self.heap: list[tuple[int, int]] = []  # (-value, -serial)
        self.live: dict[int, MaxStack._Node] = {}
        self.next_serial = 0

    def _unlink(self, node: _Node) -> None:
        node.prev.next = node.next
        node.next.prev = node.prev
        del self.live[node.serial]  # the heap entry dies lazily

    def _purge(self) -> None:
        while self.heap and -self.heap[0][1] not in self.live:
            heappop(self.heap)

    def push(self, value: int) -> None:
        node = self._Node(value, self.next_serial)
        self.next_serial += 1
        node.prev = self.tail.prev
        node.next = self.tail
        self.tail.prev.next = node
        self.tail.prev = node
        self.live[node.serial] = node
        # Larger serial wins a tie, i.e. the copy nearest the top.
        heappush(self.heap, (-value, -node.serial))

    def top(self) -> int:
        return self.tail.prev.value

    def pop(self) -> int:
        node = self.tail.prev
        self._unlink(node)
        return node.value

    def peek_max(self) -> int:
        self._purge()  # must be clean before it is read
        return -self.heap[0][0]

    def pop_max(self) -> int:
        self._purge()
        negated_value, negated_serial = heappop(self.heap)
        self._unlink(self.live[-negated_serial])
        return -negated_value


CASES: list[tuple[tuple, object]] = []


def check() -> None:
    stack = MaxStack()
    stack.push(5)
    stack.push(1)
    stack.push(5)
    assert stack.top() == 5
    assert stack.pop_max() == 5  # the top-most 5, not the bottom one
    assert stack.top() == 1  # this is what a value-only heap gets wrong
    assert stack.peek_max() == 5
    assert stack.pop() == 1
    assert stack.top() == 5
    assert stack.pop_max() == 5
    assert not stack.live

    # pop_max reaching into the middle, then the stack order must survive.
    middle = MaxStack()
    for value in (1, 9, 2, 8, 3):
        middle.push(value)
    assert middle.pop_max() == 9
    assert middle.top() == 3
    assert middle.peek_max() == 8
    assert middle.pop() == 3
    assert middle.pop_max() == 8
    assert middle.top() == 2
    assert middle.peek_max() == 2

    # Negatives, and a maximum sitting at the very bottom.
    negatives = MaxStack()
    for value in (-1, -5, -3, -7):
        negatives.push(value)
    assert negatives.peek_max() == -1
    assert negatives.top() == -7
    assert negatives.pop_max() == -1
    assert negatives.peek_max() == -3
    assert negatives.pop() == -7
    assert negatives.top() == -3

    # All equal: pop_max must peel from the top, so top() stays defined.
    ties = MaxStack()
    for _ in range(4):
        ties.push(7)
    for _ in range(4):
        assert ties.peek_max() == 7
        assert ties.pop_max() == 7
    assert not ties.live

    # Plain pop leaves dead heap entries; peek_max must not see them.
    stale = MaxStack()
    stale.push(4)
    stale.push(10)
    stale.push(6)
    assert stale.pop() == 6
    assert stale.pop() == 10  # the maximum leaves via pop, not pop_max
    assert stale.peek_max() == 4
    assert stale.top() == 4

    # Pushing after a pop_max, interleaved.
    reused = MaxStack()
    reused.push(2)
    reused.push(6)
    assert reused.pop_max() == 6
    reused.push(6)
    reused.push(6)
    assert reused.pop() == 6
    assert reused.peek_max() == 6
    assert reused.pop_max() == 6
    assert reused.top() == 2
    assert reused.peek_max() == 2

    # A longer run checked against a list-based reference implementation.
    model: list[int] = []
    fast = MaxStack()
    for value in (3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5):
        fast.push(value)
        model.append(value)
    for _ in range(5):
        peak = max(model)
        assert fast.peek_max() == peak
        assert fast.pop_max() == peak
        del model[len(model) - 1 - model[::-1].index(peak)]  # top-most copy
        assert fast.top() == model[-1]
    assert fast.pop() == model.pop()
    assert fast.peek_max() == max(model)
