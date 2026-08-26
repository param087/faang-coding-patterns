"""Maximum Frequency Stack — LeetCode 895."""

from __future__ import annotations

import random
from collections import Counter, defaultdict

META = {
    "pattern": "stack",
    "symbol": "FreqStack",
    "insight": "One stack per frequency level, and a value stays in every level it climbed through — so a pop uncovers the previous answer for free.",
    "time": "O(1) per push and pop",
    "space": "O(n) — each push adds exactly one entry",
    "sections": [
        (
            "What it asks",
            """
Design a stack where `pop()` removes the **most frequent** value, and breaks
ties in favour of the value closest to the top.

The tie-break is the whole problem — without it a plain `Counter` and a max
would do. Ask what the call mix looks like and whether values are bounded; the
answer below is O(1) regardless, which is worth stating before you write it.
""",
        ),
        (
            "The insight",
            """
The reflex answer is a max-heap keyed on `(frequency, sequence_number)`. It
works and it is O(log n), but it needs a lazy-deletion or decrease-key story,
because popping a value changes its frequency and the heap holds a stale copy.
Say this, then improve on it.

The improvement: **frequency only ever moves by one**, up on push and down on
pop. So keep one stack per frequency level, `groups[f]`, and when a value
reaches count `f`, push it onto `groups[f]` — leaving its earlier copies sitting
in `groups[1] … groups[f - 1]`.

Those copies are not garbage. They are the record of what the answer *was*
before this value overtook everything, so a pop from level `f` restores that
earlier state automatically. No re-sorting, no invalidation, no heap.

`groups[max_freq]` is a stack, so the last value to reach that frequency comes
out first — the tie-break is a consequence of the structure rather than a
comparator. Every operation is O(1); a push adds one entry, so space is O(n) in
the number of pushes.
""",
        ),
        (
            "The max_freq bookkeeping",
            """
`max_freq` is a plain integer, and the reason that is safe is worth saying out
loud: **each pop removes exactly one value from `groups[max_freq]`**, so when
that level empties, the correct new maximum is `max_freq - 1`, never anything
lower. A level can never be skipped, because reaching frequency `f` requires
passing through `f - 1` and leaving a copy behind.

Two things to keep straight:

- decrement `max_freq` only when the level actually empties, not on every pop —
  `push(5); push(5); push(7); pop()` must still see `max_freq == 2`;
- `freqs[value]` must be decremented too, or a re-pushed value jumps to the
  wrong level.

Dry run `push 5, 7, 5, 7, 4, 5`. Levels: `1: [5, 7, 4]`, `2: [5, 7]`,
`3: [5]`. Pops give **5** (level 3 empties, `max_freq` → 2), then **7** — the
tie between 5 and 7 at frequency 2 goes to 7 because it is on top of level 2 —
then **5** (level 2 empties), then **4** from level 1.

`pop()` on an empty stack is undefined in the problem; raising beats returning a
sentinel, and mentioning it costs nothing.
""",
        ),
    ],
}


class FreqStack:
    """One stack per frequency level; a value lives in every level it reached."""

    def __init__(self) -> None:
        self.freqs: Counter[int] = Counter()
        self.groups: dict[int, list[int]] = defaultdict(list)
        self.max_freq = 0

    def push(self, value: int) -> None:
        freq = self.freqs[value] + 1
        self.freqs[value] = freq
        self.groups[freq].append(value)  # earlier copies stay where they are
        self.max_freq = max(self.max_freq, freq)

    def pop(self) -> int:
        if self.max_freq == 0:
            raise IndexError("pop from an empty FreqStack")

        top = self.groups[self.max_freq]
        value = top.pop()  # a stack, so ties go to the most recent arrival
        self.freqs[value] -= 1
        if not top:
            # Frequencies move one step at a time, so this is always correct.
            self.max_freq -= 1
        return value


class _ReferenceFreqStack:
    """Obvious O(n) version, used only to cross-check the fast one."""

    def __init__(self) -> None:
        self.items: list[int] = []

    def push(self, value: int) -> None:
        self.items.append(value)

    def pop(self) -> int:
        counts = Counter(self.items)
        best = max(counts.values())
        for index in range(len(self.items) - 1, -1, -1):
            if counts[self.items[index]] == best:
                return self.items.pop(index)
        raise IndexError("pop from an empty FreqStack")


CASES: list[tuple[tuple, object]] = []


def check() -> None:
    stack = FreqStack()
    for value in (5, 7, 5, 7, 4, 5):
        stack.push(value)
    assert stack.pop() == 5  # frequency 3
    assert stack.pop() == 7  # tie at 2, 7 is nearer the top
    assert stack.pop() == 5
    assert stack.pop() == 4

    # Interleaving pushes after pops must not corrupt max_freq.
    stack.push(4)
    stack.push(4)
    assert stack.pop() == 4
    assert stack.pop() == 4
    assert stack.pop() == 7  # only 5 and 7 remain, one copy each, 7 on top
    assert stack.pop() == 5
    try:
        stack.pop()
    except IndexError:
        pass
    else:
        raise AssertionError("popping an empty FreqStack must raise")

    # Single element, and a value re-entering after dropping to zero.
    single = FreqStack()
    single.push(-3)
    assert single.pop() == -3
    single.push(-3)
    single.push(0)
    single.push(-3)
    assert single.pop() == -3  # negatives and zero are ordinary values

    # Every value distinct: pure LIFO, no frequency ever exceeds 1.
    lifo = FreqStack()
    for value in range(6):
        lifo.push(value)
    assert [lifo.pop() for _ in range(6)] == [5, 4, 3, 2, 1, 0]

    # Randomised cross-check against the obvious implementation.
    rng = random.Random(895)
    for _ in range(40):
        fast, slow = FreqStack(), _ReferenceFreqStack()
        live = 0
        for _ in range(60):
            if live and rng.random() < 0.4:
                assert fast.pop() == slow.pop()
                live -= 1
            else:
                value = rng.randrange(-2, 4)
                fast.push(value)
                slow.push(value)
                live += 1
        while live:
            assert fast.pop() == slow.pop()
            live -= 1
