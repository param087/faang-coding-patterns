"""Design Circular Queue — LeetCode 622."""

from __future__ import annotations

META = {
    "pattern": "design",
    "symbol": "MyCircularQueue",
    "insight": "Store a head index and a size, not a head and a tail — the size is what tells full apart from empty when the two indices coincide.",
    "time": "O(1) per operation",
    "space": "O(k)",
    "sections": [
        (
            "What it asks",
            """
A fixed-capacity FIFO queue over a pre-allocated buffer: `en_queue`,
`de_queue`, `front`, `rear`, `is_empty`, `is_full`. The two mutators return a
boolean instead of raising, and the two accessors return −1 on an empty queue.

Ask: is the capacity fixed at construction (yes — no resizing, which is the
entire reason for the ring)? Should a full `en_queue` overwrite the oldest
entry (**no** here, but that variant is the one a ring buffer usually means in
production, so say the difference out loud).
""",
        ),
        (
            "The insight",
            """
The array is a ring: index `capacity - 1` is followed by index `0`, which is
one `% capacity` away. That part is easy and it is not what the problem tests.

What it tests is the state you keep. With a `head` and a `tail` pointer,
`head == tail` means both "empty" and "full", and you cannot tell which. The
classic fixes are to waste one slot (a queue of capacity k stored in k+1 cells)
or to carry a boolean flag — both work, both invite off-by-ones.

Keep **`head` and `size`** instead. Every question answers itself:

- empty is `size == 0`, full is `size == capacity`, no ambiguity at all;
- the write position is `(head + size) % capacity`;
- the last element is `(head + size - 1) % capacity`;
- `de_queue` advances `head` and decrements `size` — it never touches the cell,
  because a stale value behind `head` is unreachable by construction.

That is the answer in five lines with no special cases, and being able to say
*why* you chose it over two pointers is the point of the question.
""",
        ),
        (
            "Edge cases",
            """
- **Empty `front`/`rear`** return −1 rather than reading `buffer[head]`, which
  would return whatever stale value the last `de_queue` left behind.
- **`rear` after a wrap** is the modulo expression, not `buffer[tail - 1]`;
  when `head + size` has wrapped past the end, the naive subtraction indexes a
  negative slot that Python happily reads from the wrong end.
- **Capacity 1** — head and the write position are the same cell forever, and
  the `size` formulation handles it with no branch.
- **Capacity 0**, if the constraints allow it: `is_full` is true immediately,
  so `en_queue` returns `False` before any `% 0` can raise. Check that ordering
  deliberately rather than by luck.
- **Interleaved wraps** — fill, drain, fill again several times over. That is
  the sequence that catches an implementation which resets `head` to 0 on
  empty but forgets the write position.
""",
        ),
    ],
}


class MyCircularQueue:
    def __init__(self, k: int) -> None:
        self.capacity = k
        self.buffer = [0] * k
        self.head = 0
        self.size = 0  # the field that disambiguates full from empty

    def is_empty(self) -> bool:
        return self.size == 0

    def is_full(self) -> bool:
        return self.size == self.capacity

    def en_queue(self, value: int) -> bool:
        if self.is_full():  # guards % 0 when capacity is 0
            return False
        self.buffer[(self.head + self.size) % self.capacity] = value
        self.size += 1
        return True

    def de_queue(self) -> bool:
        if self.is_empty():
            return False
        self.head = (self.head + 1) % self.capacity  # the cell is left as is
        self.size -= 1
        return True

    def front(self) -> int:
        return -1 if self.is_empty() else self.buffer[self.head]

    def rear(self) -> int:
        if self.is_empty():
            return -1
        return self.buffer[(self.head + self.size - 1) % self.capacity]


CASES: list[tuple[tuple, object]] = []


def check() -> None:
    queue = MyCircularQueue(3)
    assert queue.is_empty()
    assert queue.front() == -1 and queue.rear() == -1
    assert queue.en_queue(1)
    assert queue.en_queue(2)
    assert queue.en_queue(3)
    assert not queue.en_queue(4)  # full, rejected rather than overwriting
    assert queue.rear() == 3
    assert queue.is_full()
    assert queue.de_queue()
    assert queue.en_queue(4)  # wraps to slot 0
    assert queue.rear() == 4
    assert queue.front() == 2

    # Drain to empty, then refill — head is mid-buffer, so the writes wrap.
    while queue.de_queue():
        pass
    assert queue.is_empty()
    assert not queue.de_queue()
    assert queue.front() == -1
    for value in (7, 8, 9):
        assert queue.en_queue(value)
    assert queue.front() == 7
    assert queue.rear() == 9

    # Capacity 1: head and the write slot are the same cell.
    single = MyCircularQueue(1)
    assert single.en_queue(5)
    assert single.is_full()
    assert not single.en_queue(6)
    assert single.front() == 5 and single.rear() == 5
    assert single.de_queue()
    assert single.is_empty() and single.front() == -1
    assert single.en_queue(6)
    assert single.rear() == 6

    # Capacity 0 must reject without dividing by zero.
    nothing = MyCircularQueue(0)
    assert nothing.is_empty() and nothing.is_full()
    assert not nothing.en_queue(1)
    assert not nothing.de_queue()
    assert nothing.front() == -1 and nothing.rear() == -1

    # FIFO order survives many wraps.
    ring = MyCircularQueue(4)
    drained: list[int] = []
    for value in range(20):
        if not ring.en_queue(value):
            drained.append(ring.front())
            ring.de_queue()
            assert ring.en_queue(value)
    while not ring.is_empty():
        drained.append(ring.front())
        ring.de_queue()
    assert drained == list(range(20))
