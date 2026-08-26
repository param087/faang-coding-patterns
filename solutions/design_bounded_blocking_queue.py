"""Design Bounded Blocking Queue — LeetCode 1188."""

from __future__ import annotations

import threading
from collections import deque

META = {
    "pattern": "concurrency",
    "symbol": "BoundedBlockingQueue",
    "insight": "One lock, two conditions — not-full and not-empty — so a state change wakes exactly the class of waiter it can help.",
    "time": "O(1) per operation",
    "space": "O(capacity)",
    "sections": [
        (
            "What it asks",
            """
*(Premium, so described in my own words.)* Build a FIFO queue with a fixed
capacity, safe for many producer and consumer threads at once:

- `enqueue(x)` — **blocks** while the queue is full;
- `dequeue()` — **blocks** while the queue is empty, returns the front element;
- `size()` — the current count.

This is `java.util.concurrent.ArrayBlockingQueue` from scratch, and it is asked
because every real system has one in it. Ask whether `size()` needs to be
consistent with anything (no — it is a snapshot, and any caller that acts on it
has already introduced a race) and whether producers must be served in FIFO
order (no; if they say yes, you need a fair lock and should say so).
""",
        ),
        (
            "The wrong first answer",
            """
```python
with self._condition:
    if len(self._items) == self._capacity:   # if
        self._condition.wait()
    self._items.append(element)
```

`if` instead of `while`. A wake-up is a **hint that the state changed**, not a
promise that it changed in your favour. Three things break it:

1. Two producers are parked on a full queue. One consumer dequeues and wakes
   both. Both fall through the `if`, both append — the queue is now at
   `capacity + 1` and the bound you were asked to enforce is gone.
2. Spurious wake-ups are permitted by POSIX and by the Java memory model. The
   `while` is the only defence.
3. A third thread can slip in between the wake and the reacquisition of the
   lock and refill the queue.

`while` around every `wait()` is not a style preference. It is the contract.
""",
        ),
        (
            "The insight",
            """
There are two distinct predicates — *not full* and *not empty* — over one piece
of state. Give them **one lock and two condition variables**:

```python
self._lock = threading.Lock()
self._not_full  = threading.Condition(self._lock)
self._not_empty = threading.Condition(self._lock)
```

Passing the same lock into both is the whole trick: the state stays under a
single mutex, so there is no lock-ordering problem, but the wait queues are
separate. Now `enqueue` waits on `not_full` and signals `not_empty`, and
`dequeue` does the mirror image. A freed slot wakes a producer; an arrived
element wakes a consumer. Nobody is ever woken for news they cannot use.
""",
        ),
        (
            "notify vs notify_all — this is the deciding detail",
            """
With **one** condition covering both predicates you must use `notify_all`, and
here is the exact interleaving that proves it. Capacity 1, two producers, two
consumers, single condition, `notify()`:

1. Queue empty. C1 and C2 both `wait()`.
2. P1 enqueues, `notify()` → wakes C1. Size 1.
3. P2 tries to enqueue, queue is full → `wait()`. Waiters are now `{C2, P2}`.
4. C1 dequeues, size 0, `notify()` → the runtime picks **C2**.
5. C2 rechecks: still empty. Back to `wait()`.

P2's predicate became true at step 4 and nobody ever tells it. P2 and C2 sleep
forever, on a queue that is empty and unlocked. The signal was consumed by a
thread it could not help — the classic **lost wakeup**.

With two condition variables, `notify()` is correct *and* cheaper: waking all
`k` waiters when only one can proceed is the thundering herd, `O(k)` context
switches per operation for `k - 1` threads that immediately go back to sleep.
The version below therefore uses `notify()` on both sides. If you only have one
condition, use `notify_all` — and be able to say why.
""",
        ),
        (
            "Dry run",
            """
Capacity 2. Producer pushes 1…5, consumer starts late.

- `enqueue(1)`, `enqueue(2)` — queue `[1, 2]`, each signals `not_empty` to an
  empty wait set, which is a no-op.
- `enqueue(3)` — full, so the producer parks on `not_full`. **`size()` is 2 and
  stays 2**; that is the observable proof the bound is real.
- Consumer calls `dequeue()` → returns 1, signals `not_full`.
- The producer wakes, rechecks `len == capacity` (now false), appends 3.

The steady state is a queue that hovers at capacity with the producer blocked —
which is exactly the back-pressure this data structure exists to provide. If
your `enqueue` never blocks, you have not built a bounded queue, you have built
an unbounded one with a counter.
""",
        ),
        (
            "Follow-ups",
            """
- **Semaphore version.** `Semaphore(capacity)` for empty slots,
  `Semaphore(0)` for filled ones, plus a small mutex around the deque. Shorter,
  and the two semaphores *are* the two predicates. Acquire the slot semaphore
  **before** the mutex or you deadlock — a full queue's producer would sleep
  holding the lock the consumer needs.
- **`enqueue` with a timeout** — `Condition.wait(timeout)` returns `False` on
  expiry, and the `while` loop must then re-check the deadline rather than
  looping forever; use a monotonic clock.
- **Shutdown.** Real queues need a poison pill or a `closed` flag plus
  `notify_all`, otherwise consumers block on a queue nobody will ever fill
  again. Interviewers who have run a service will ask this.
- **Lock-free.** A single-producer/single-consumer ring buffer needs only two
  atomics and no lock. Beyond SPSC the complexity rarely pays.
""",
        ),
    ],
}


class BoundedBlockingQueue:
    def __init__(self, capacity: int) -> None:
        self._capacity = capacity
        self._items: deque[int] = deque()
        # One lock, two wait queues: same state, two different predicates.
        self._lock = threading.Lock()
        self._not_full = threading.Condition(self._lock)
        self._not_empty = threading.Condition(self._lock)

    def enqueue(self, element: int) -> None:
        with self._not_full:
            while len(self._items) == self._capacity:
                self._not_full.wait()  # while, never if
            self._items.append(element)
            self._not_empty.notify()  # exactly one consumer can use this

    def dequeue(self) -> int:
        with self._not_empty:
            while not self._items:
                self._not_empty.wait()
            element = self._items.popleft()
            self._not_full.notify()
            return element

    def size(self) -> int:
        with self._lock:
            return len(self._items)


def _fifo(capacity: int, count: int) -> list[int]:
    """One producer, one consumer: order must be preserved exactly."""
    bbq = BoundedBlockingQueue(capacity)
    taken: list[int] = []

    def produce() -> None:
        for value in range(1, count + 1):
            bbq.enqueue(value)

    def consume() -> None:
        for _ in range(count):
            taken.append(bbq.dequeue())

    # Consumer first: dequeue must block on an empty queue, not fail.
    threads = [
        threading.Thread(target=consume, daemon=True),
        threading.Thread(target=produce, daemon=True),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=10)
        assert not thread.is_alive(), "blocked forever"
    return taken


def _many(capacity: int, producers: int, consumers: int, per_thread: int) -> list[int]:
    total = producers * per_thread
    assert total % consumers == 0
    bbq = BoundedBlockingQueue(capacity)
    taken: list[int] = []
    monitor = threading.Lock()

    def produce(offset: int) -> None:
        for value in range(offset, offset + per_thread):
            bbq.enqueue(value)

    def consume() -> None:
        for _ in range(total // consumers):
            value = bbq.dequeue()
            with monitor:
                taken.append(value)

    threads = [
        threading.Thread(target=produce, args=(p * per_thread,), daemon=True)
        for p in range(producers)
    ]
    threads += [threading.Thread(target=consume, daemon=True) for _ in range(consumers)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=10)
        assert not thread.is_alive(), "lost wakeup: a thread never returned"
    return sorted(taken)


def check() -> None:
    assert _fifo(capacity=2, count=10) == list(range(1, 11))
    assert _fifo(capacity=1, count=5) == [1, 2, 3, 4, 5]
    assert _fifo(capacity=50, count=1) == [1]

    # Capacity 1 with two producers and two consumers is the exact shape that
    # deadlocks a single-condition + notify() implementation.
    for _ in range(20):
        assert _many(capacity=1, producers=2, consumers=2, per_thread=10) == list(range(20))
    assert _many(capacity=3, producers=4, consumers=2, per_thread=25) == list(range(100))

    # The bound is real: a producer of 6 items into a capacity of 2 must park.
    bbq = BoundedBlockingQueue(2)
    started = threading.Event()

    def flood() -> None:
        started.set()
        for value in range(6):
            bbq.enqueue(value)

    producer = threading.Thread(target=flood, daemon=True)
    producer.start()
    started.wait(timeout=5)
    for _ in range(4):  # drain one at a time, checking the cap each time
        assert bbq.size() <= 2, bbq.size()
        assert bbq.dequeue() in range(6)
    assert bbq.dequeue() == 4
    assert bbq.dequeue() == 5
    producer.join(timeout=5)
    assert not producer.is_alive()
    assert bbq.size() == 0
