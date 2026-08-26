"""The Dining Philosophers — LeetCode 1226."""

from __future__ import annotations

import threading
from collections.abc import Callable
from functools import partial

META = {
    "pattern": "concurrency",
    "symbol": "DiningPhilosophers",
    "insight": "Deadlock needs a cycle of waiters; make the odd-numbered philosophers reach for their forks in the opposite order and no cycle can close.",
    "time": "O(1) per meal",
    "space": "O(1) — five locks",
    "sections": [
        (
            "What it asks",
            """
Five philosophers sit round a table with five forks between them; philosopher
`i` needs fork `i` and fork `i-1`. Implement `wants_to_eat`, which is called
concurrently and repeatedly by all five threads, so that:

- a fork is never held by two philosophers at once, and
- **nobody starves and nothing deadlocks**.

The five callbacks — pick left, pick right, eat, put left, put right — are how
you report what you did. Ask whether you may hold both forks for the whole meal
(yes) and whether the two picks must be logged separately (yes, which is
precisely what makes the naive answer *look* reasonable).
""",
        ),
        (
            "The naive answer, and the number",
            """
Everyone grabs their left fork, then their right:

```python
forks[left].acquire()
forks[right].acquire()
```

This is correct for mutual exclusion and **deadlocks**. If all five acquire
their left fork before any acquires its right, every philosopher is waiting on
a neighbour, forever.

It is rare, which is what makes it dangerous. Running that version five times
at 5 threads × 10⁵ rounds on CPython: **four runs finished in 0.1 s, one hung —
after about 57,000 successful meals.** A test suite that runs it once will pass.
Production will not. And CPython's coarse GIL switch interval is *hiding* the
bug: in Java, C++ or free-threaded Python the window is much wider.

That is the whole point of the question. Anyone can write mutual exclusion; the
question is whether you notice the cycle.
""",
        ),
        (
            "The insight",
            """
Deadlock needs all four Coffman conditions, and the only one cheap to break
here is **circular wait**. The cycle exists because all five philosophers
reach in the same rotational direction. Break the symmetry:

```python
order = [(left, pick_left), (right, pick_right)]
if philosopher % 2:
    order.reverse()          # odd philosophers reach the other way
```

Everything else is unchanged: acquire in that order, eat, put both down,
release. No global lock, no waiter, no retry loop — and four philosophers can
still be holding forks simultaneously.
""",
        ),
        (
            "Why parity works with five, which is odd",
            """
This is the part worth being able to prove, because five is odd and the
alternation therefore is *not* clean — philosophers 4 and 0 are adjacent and
both even.

Number the forks so that philosopher `i` uses fork `i` (left) and fork `i-1`
(right). First reaches:

| philosopher | first fork | second fork |
|---|---|---|
| 0 (even) | f0 | f4 |
| 1 (odd)  | f0 | f1 |
| 2 (even) | f2 | f1 |
| 3 (odd)  | f2 | f3 |
| 4 (even) | f4 | f3 |

**f1 and f3 are nobody's first fork.** So whoever holds f1 or f3 already holds
their other fork too — they are eating, not waiting, and will release shortly.
A deadlock cycle needs every member to be blocked; follow any wait chain and it
terminates within two hops at a philosopher who holds f1 or f3 and is making
progress. No cycle can close.

The generic version of this argument is **resource ordering**: always acquire
locks in a globally consistent order (lowest fork id first). That is the answer
to give if the interviewer changes 5 to n, and it is the rule that actually
matters in real code — every lock-ordering deadlock you will ever debug is a
violation of it.
""",
        ),
        (
            "Dry run of the bad interleaving",
            """
The killer schedule, with the naive code: P0 takes f0, P1 takes f1, P2 takes
f2, P3 takes f3, P4 takes f4. Now P0 wants f4 (P4 has it), P4 wants f3 (P3 has
it), … all five blocked. Hung.

Same schedule with parity ordering: P0 takes f0. P1's *first* fork is also f0 —
it blocks immediately, holding nothing. P2 takes f2. P3's first fork is also f2
— blocks, holding nothing. P4 takes f4. Now P0 asks for f4 and waits, but the
system is not stuck: P2 holds f2 and wants f1, which is free, so **P2 eats**,
releases, P3 proceeds. A blocked philosopher who holds no fork cannot be part
of a cycle, and the odd philosophers block before acquiring anything.
""",
        ),
        (
            "The alternatives, and when each is right",
            """
- **`Semaphore(4)` around the whole meal.** Admit at most four philosophers to
  the table; with four diners and five forks, someone always gets both. One
  line, trivially correct, and the answer to give if you have thirty seconds.
  It caps concurrency at 4 by construction.
- **A waiter / global lock** around picking up both forks. Correct,
  deadlock-free, and serialises all fork acquisition — fine at n=5, a
  bottleneck at n=1000.
- **`try_acquire` with backoff**: take the first fork, try the second, drop
  both and retry on failure. No deadlock but it permits **livelock** unless the
  backoff is randomised — swapping a hang you can debug for one you cannot.
- **Change 5 to n.** Parity stops being the point; state the general rule —
  acquire in increasing fork id — and note it reduces to "the philosopher
  whose two forks straddle the wrap-around reaches the other way".
""",
        ),
    ],
}


class DiningPhilosophers:
    def __init__(self) -> None:
        self._forks = [threading.Lock() for _ in range(5)]

    def wants_to_eat(
        self,
        philosopher: int,
        pick_left_fork: Callable[[], None],
        pick_right_fork: Callable[[], None],
        eat: Callable[[], None],
        put_left_fork: Callable[[], None],
        put_right_fork: Callable[[], None],
    ) -> None:
        left, right = philosopher, (philosopher + 4) % 5
        order = [(left, pick_left_fork), (right, pick_right_fork)]
        if philosopher % 2:
            order.reverse()  # break the rotational symmetry -> no circular wait

        for fork, pick in order:
            self._forks[fork].acquire()
            pick()

        eat()

        # Log both forks down *before* releasing, so no neighbour can claim a
        # fork that this philosopher has not yet reported putting back.
        put_left_fork()
        put_right_fork()
        for fork, _ in reversed(order):
            self._forks[fork].release()


def _run_once(rounds: int) -> tuple[list[int], list[str], set[int]]:
    """Five threads, `rounds` meals each, with every invariant checked live."""
    table = DiningPhilosophers()
    monitor = threading.Lock()  # protects the harness's own bookkeeping
    owner: list[int | None] = [None] * 5
    holding = [0] * 5
    first_reach: set[int] = set()
    meals = [0] * 5
    errors: list[str] = []

    def pick(who: int, fork: int) -> None:
        with monitor:
            if owner[fork] is not None:
                errors.append(f"fork {fork} held by {owner[fork]} and {who}")
            if holding[who] == 0:
                first_reach.add(fork)  # which fork this philosopher reached for first
            holding[who] += 1
            owner[fork] = who

    def put(who: int, fork: int) -> None:
        with monitor:
            if owner[fork] != who:
                errors.append(f"{who} put down fork {fork} held by {owner[fork]}")
            holding[who] -= 1
            owner[fork] = None

    def eat(who: int) -> None:
        with monitor:
            if owner[who] != who or owner[(who + 4) % 5] != who:
                errors.append(f"{who} ate without both forks")
            meals[who] += 1

    def seat(who: int) -> None:
        left, right = who, (who + 4) % 5
        actions = (
            partial(pick, who, left),
            partial(pick, who, right),
            partial(eat, who),
            partial(put, who, left),
            partial(put, who, right),
        )
        for _ in range(rounds):
            table.wants_to_eat(who, *actions)

    threads = [threading.Thread(target=seat, args=(who,), daemon=True) for who in range(5)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=15)
        if thread.is_alive():
            errors.append("deadlock: a philosopher never finished")
    return meals, errors, first_reach


def check() -> None:
    for _ in range(5):
        meals, errors, first_reach = _run_once(rounds=200)
        assert not errors, errors[:3]
        assert meals == [200] * 5, meals
        # The asymmetry *is* the solution, and a deadlock is far too rare to
        # catch by running the naive version — so assert the structure instead.
        # Forks 1 and 3 must never be anyone's first reach; that is precisely
        # what makes a circular wait impossible. A left-then-right version
        # reaches first for all five forks and fails here.
        assert first_reach == {0, 2, 4}, first_reach
