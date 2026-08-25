"""Concurrency and multithreading.

Asked far more often than candidates prepare for, and the bar is low: know
when to use a `Lock`, a `Semaphore`, a `Condition` and a `Barrier`, and be
able to say why a busy-wait is wrong.

The rule that answers most of these: **a lock protects state; a semaphore
counts permits; a condition lets a thread sleep until a predicate holds.**
Spinning on a boolean is never the right answer — it burns a core and gives
no ordering guarantee.
"""

from __future__ import annotations

import threading
from collections.abc import Callable


class Foo:
    """Print in Order — force three concurrent calls into a fixed sequence.

    Two semaphores, each starting at zero, act as one-shot gates. `second`
    blocks until `first` releases it. Semaphores rather than locks because a
    `Lock` in Python may only be released by its owner in well-behaved code,
    while a semaphore is explicitly a signal between threads.
    """

    def __init__(self) -> None:
        self._second_gate = threading.Semaphore(0)
        self._third_gate = threading.Semaphore(0)

    def first(self, print_first: Callable[[], None]) -> None:
        print_first()
        self._second_gate.release()

    def second(self, print_second: Callable[[], None]) -> None:
        self._second_gate.acquire()
        print_second()
        self._third_gate.release()

    def third(self, print_third: Callable[[], None]) -> None:
        self._third_gate.acquire()
        print_third()


class FooBar:
    """Print FooBar alternately n times, from two threads.

    Strict alternation needs two gates facing each other: each thread releases
    the other and then waits to be released itself. One shared lock is not
    enough — either thread could reacquire it immediately and print twice.
    """

    def __init__(self, n: int) -> None:
        self.n = n
        self._foo_turn = threading.Semaphore(1)  # foo goes first
        self._bar_turn = threading.Semaphore(0)

    def foo(self, print_foo: Callable[[], None]) -> None:
        for _ in range(self.n):
            self._foo_turn.acquire()
            print_foo()
            self._bar_turn.release()

    def bar(self, print_bar: Callable[[], None]) -> None:
        for _ in range(self.n):
            self._bar_turn.acquire()
            print_bar()
            self._foo_turn.release()


class BoundedBlockingQueue:
    """A fixed-capacity queue that blocks producers when full and consumers
    when empty.

    The classic. One lock guards the deque; two conditions let threads sleep
    until the queue is not full / not empty. `wait_for` re-checks the
    predicate on wake, which handles spurious wakeups and the case where
    another thread won the race — writing `if` instead of a loop is the bug
    this question is really testing.
    """

    def __init__(self, capacity: int) -> None:
        from collections import deque

        self.capacity = capacity
        self._queue: deque[int] = deque()
        self._lock = threading.Lock()
        self._not_full = threading.Condition(self._lock)
        self._not_empty = threading.Condition(self._lock)

    def enqueue(self, element: int) -> None:
        with self._not_full:
            self._not_full.wait_for(lambda: len(self._queue) < self.capacity)
            self._queue.append(element)
            self._not_empty.notify()

    def dequeue(self) -> int:
        with self._not_empty:
            self._not_empty.wait_for(lambda: len(self._queue) > 0)
            value = self._queue.popleft()
            self._not_full.notify()
            return value

    def size(self) -> int:
        with self._lock:
            return len(self._queue)


class H2O:
    """Building H2O — release molecules only in groups of two H and one O.

    A `Barrier(3)` is the clean answer: threads gather until three have
    arrived, then all proceed. Semaphores alone let a thread rush ahead and
    form HHH. The barrier is what encodes "nobody leaves until the group is
    complete".
    """

    def __init__(self) -> None:
        self._hydrogen_slots = threading.Semaphore(2)
        self._oxygen_slots = threading.Semaphore(1)
        self._barrier = threading.Barrier(3)

    def hydrogen(self, release_hydrogen: Callable[[], None]) -> None:
        self._hydrogen_slots.acquire()
        self._barrier.wait()
        release_hydrogen()
        self._hydrogen_slots.release()

    def oxygen(self, release_oxygen: Callable[[], None]) -> None:
        self._oxygen_slots.acquire()
        self._barrier.wait()
        release_oxygen()
        self._oxygen_slots.release()


CASES: list[tuple[tuple, object]] = []


def check() -> None:
    # Print in Order: start the threads in the wrong order on purpose.
    output: list[str] = []
    foo = Foo()
    threads = [
        threading.Thread(target=foo.third, args=(lambda: output.append("third"),)),
        threading.Thread(target=foo.second, args=(lambda: output.append("second"),)),
        threading.Thread(target=foo.first, args=(lambda: output.append("first"),)),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert output == ["first", "second", "third"]

    # FooBar alternation.
    sequence: list[str] = []
    foobar = FooBar(5)
    a = threading.Thread(target=foobar.foo, args=(lambda: sequence.append("foo"),))
    b = threading.Thread(target=foobar.bar, args=(lambda: sequence.append("bar"),))
    a.start()
    b.start()
    a.join()
    b.join()
    assert sequence == ["foo", "bar"] * 5

    # Bounded queue: a producer that outruns the capacity must block.
    queue = BoundedBlockingQueue(2)
    consumed: list[int] = []

    def produce() -> None:
        for i in range(5):
            queue.enqueue(i)

    def consume() -> None:
        for _ in range(5):
            consumed.append(queue.dequeue())

    producer = threading.Thread(target=produce)
    consumer = threading.Thread(target=consume)
    producer.start()
    consumer.start()
    producer.join(timeout=5)
    consumer.join(timeout=5)
    assert consumed == [0, 1, 2, 3, 4]
    assert queue.size() == 0

    # H2O: two molecules' worth of atoms must come out as 4 H and 2 O.
    atoms: list[str] = []
    atoms_lock = threading.Lock()

    def record(symbol: str) -> Callable[[], None]:
        def emit() -> None:
            with atoms_lock:
                atoms.append(symbol)

        return emit

    water = H2O()
    workers = [threading.Thread(target=water.hydrogen, args=(record("H"),)) for _ in range(4)]
    workers += [threading.Thread(target=water.oxygen, args=(record("O"),)) for _ in range(2)]
    for worker in workers:
        worker.start()
    for worker in workers:
        worker.join(timeout=5)
    assert atoms.count("H") == 4
    assert atoms.count("O") == 2
    # Every group of three must be exactly HHO in some order.
    for group in (atoms[:3], atoms[3:]):
        assert sorted(group) == ["H", "H", "O"]
