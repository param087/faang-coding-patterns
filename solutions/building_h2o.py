"""Building H2O — LeetCode 1117."""

from __future__ import annotations

import threading
from collections.abc import Callable

META = {
    "pattern": "concurrency",
    "symbol": "H2O",
    "insight": "Two semaphores cap the molecule at 2 H and 1 O; a 3-party barrier makes those three leave together as a group.",
    "time": "O(1) per thread",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Hydrogen and oxygen threads each want to output their letter. Output must group
into water molecules: every consecutive run of three letters must contain
exactly two `H` and one `O`. Within a group the order does not matter — `HOH`,
`OHH` and `HHO` are all fine.

Ask two things. **Is the input guaranteed balanced** (yes — exactly `2n` H and
`n` O, which is why nobody is ever left stranded). And **may a thread block
indefinitely** waiting for partners (yes — that is the mechanism, not a bug).
""",
        ),
        (
            "The insight",
            """
Two independent jobs, and it is tempting to solve them with one primitive:

1. **Composition** — never let more than 2 H and 1 O into the same molecule.
   That is a `Semaphore(2)` and a `Semaphore(1)`.
2. **Grouping** — the three that got in must be released *together*, before any
   fourth thread can print. That is a **barrier of 3**.

```python
def hydrogen(self, release):
    self._h_slots.acquire()   # at most 2 in flight
    self._barrier.wait()      # nobody prints until all three are here
    release()
    self._h_slots.release()   # slot reopens only after printing
```

The order of the last two lines is the whole problem. Releasing the semaphore
**after** printing is what stops a thread from the next molecule slipping in
between two prints of this one.
""",
        ),
        (
            "Why a counter cannot replace the barrier",
            """
The plausible-looking alternative is a counter under a lock: count arrivals,
and when it hits 3, reset and let everyone through. It has a real hole — the
threads that were let through have no idea *when* their group finished, so a
fast H can print, release its slot, and a new H can acquire it, reach the
rendezvous and print, all while the first molecule's second H is still on the
scheduler's run queue. Output: `H H H ...` — four letters before the O.

The semaphores alone are not enough either, for the same reason. What saves it
is that a slot only reopens **after** the print, so the next group cannot fill
all three slots — and therefore cannot clear a 3-party barrier — until every
member of the current group has printed. Two H slots plus one O slot means a
barrier of three can only be satisfied by a fully-vacated molecule.

Note `threading.Barrier` is **reusable**: it resets automatically after each
generation, which is exactly what you want here and is worth stating, because
the Java answer (`CyclicBarrier`, not `CountDownLatch`) turns on the same word.
""",
        ),
    ],
}


class H2O:
    def __init__(self) -> None:
        self._h_slots = threading.Semaphore(2)
        self._o_slots = threading.Semaphore(1)
        self._barrier = threading.Barrier(3)  # cyclic: it resets after each molecule

    def hydrogen(self, release_hydrogen: Callable[[], None]) -> None:
        self._h_slots.acquire()
        self._barrier.wait()
        release_hydrogen()
        self._h_slots.release()  # after the print, or the next group leaks in

    def oxygen(self, release_oxygen: Callable[[], None]) -> None:
        self._o_slots.acquire()
        self._barrier.wait()
        release_oxygen()
        self._o_slots.release()


def _run_once(water: str) -> str:
    """Spawn one thread per atom, in the given (deliberately awkward) order."""
    output: list[str] = []
    lock = threading.Lock()
    builder = H2O()

    def emit(letter: str) -> None:
        with lock:  # the harness's own list needs protecting; the class does not
            output.append(letter)

    def emit_h() -> None:
        emit("H")

    def emit_o() -> None:
        emit("O")

    threads = [
        threading.Thread(target=builder.hydrogen, args=(emit_h,), daemon=True)
        if atom == "H"
        else threading.Thread(target=builder.oxygen, args=(emit_o,), daemon=True)
        for atom in water
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=5)
        assert not thread.is_alive(), f"deadlock on {water!r}"
    return "".join(output)


def _is_valid(result: str, water: str) -> bool:
    if sorted(result) != sorted(water):
        return False
    groups = [result[i : i + 3] for i in range(0, len(result), 3)]
    return all(group.count("H") == 2 and group.count("O") == 1 for group in groups)


def check() -> None:
    for water in ("HOH", "OOHHHH", "HHOHHO", "HHHHHHOOO", "OHHOHH"):
        for _ in range(10):
            result = _run_once(water)
            assert _is_valid(result, water), f"{water!r} produced {result!r}"

    # The validator must actually reject the failure mode we care about.
    assert not _is_valid("HHHOOH", "HOHHOH")  # first group has no oxygen
    assert not _is_valid("HHO", "HOH" * 2)  # atoms lost
    assert _is_valid("OHHHOH", "HOHHOH")  # OHH then HOH is fine
