"""Linked List Random Node — LeetCode 382."""

from __future__ import annotations

import random
from collections import Counter
from dataclasses import dataclass

META = {
    "pattern": "randomized",
    "symbol": "Solution",
    "insight": "Walk once and keep the i-th node with probability 1/i; the held value is uniform at every prefix, so you never need the length.",
    "time": "O(n) per pick, O(1) construction",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Return the value of a random node from a singly linked list, each node equally
likely.

The body of the question is trivial; **the follow-up is the question**: the
list is extremely large, its length is unknown, and you cannot store it. That
sentence is the interviewer asking for reservoir sampling by name without
saying it.

Worth clarifying before you write: how many picks per list (one pick on a
huge list is very different from a million picks on a fixed one), whether the
list may be mutated between calls, and whether they want the node or just its
value. Only the last one is cosmetic.
""",
        ),
        (
            "The two easy answers, and the numbers that kill them",
            """
**Materialise it.** Copy the values into an array in the constructor, then
`values[randrange(n)]` per pick. O(1) picks, and genuinely the right answer
when the list fits in memory — say so, do not pretend otherwise. It costs O(n)
memory, which the follow-up has just forbidden.

**Count, then walk.** Two passes: length first, then walk `k` steps. O(1)
memory, but O(n) per pick. With a 10⁴-node list and 10⁴ picks that is 10⁸
pointer chases, and pointer chasing is cache-hostile in a way that array
indexing is not — the constant is worse than the exponent suggests.

Both also need to know n. On a stream — log lines arriving on a socket, rows
from a cursor you may only iterate once — you do not get to ask for the
length, and you do not get a second pass. That is the regime the follow-up is
describing.
""",
        ),
        (
            "The insight: decide as you go",
            """
Reservoir sampling with a reservoir of size 1.

Hold one candidate. At the i-th node (1-based), **replace the candidate with
probability 1/i**. Node 1 is always taken; node 2 displaces it half the time;
node 3 displaces the survivor a third of the time; and so on. Stop whenever
you like.

One pass, one variable, no length required. And crucially it is correct **at
every prefix**, not just at the end — cut the stream off after 17 nodes and
the held value is uniform over those 17. That is what lets it run on data of
unknown or unbounded size.
""",
        ),
        (
            "Why it is uniform",
            """
This is the part the interviewer is waiting for. Fix node i in a list of n.

It ends up held iff it was **taken** at step i and never **displaced**
afterwards:

```
P(taken at i)      = 1/i
P(survives step j) = 1 − 1/j = (j−1)/j     for j = i+1 … n
```

The survival product telescopes — every numerator cancels the previous
denominator:

```
i/(i+1) · (i+1)/(i+2) · … · (n−1)/n = i/n
```

So P(node i) = (1/i)·(i/n) = **1/n**, with no dependence on i. Every node,
front or back, gets the same 1/n.

The same argument generalises to a reservoir of size k, which is the natural
next question.
""",
        ),
        (
            "The detail that decides it",
            """
Write the coin as `random.randrange(seen) == 0` where `seen` is the **1-based**
count of nodes visited so far, incremented *before* the test. Get that order
wrong and node 1 is chosen with `randrange(0)`, which raises.

The float spelling `random.random() < 1 / seen` is equivalent and reads
closer to the proof, but invites `<=`, which hands node 1 a probability of 1
at every step and pins the answer to the last node. Prefer the integer form.

The cost you are accepting: **one RNG call per node**, so O(n) draws per pick.
That is the price of O(1) memory, and it is why the array version wins when
memory is available. If pick rate is the bottleneck and the list is fixed,
build the array once and stop being clever.
""",
        ),
        (
            "Dry run",
            """
List `1 → 2 → 3`.

- Node 1: `randrange(1) == 0` is always true. Held = 1.
- Node 2: taken with probability 1/2. Held = 2 half the time.
- Node 3: taken with probability 1/3.

Totals:

```
P(3) = 1/3
P(2) = 1/2 · 2/3 = 1/3
P(1) =   1 · 1/2 · 2/3 = 1/3
```

The head is *always* taken and still ends at exactly 1/3 — that surprises
people, and it is the whole trick: later nodes are taken rarely but, once
taken, are rarely displaced.
""",
        ),
        (
            "Follow-ups",
            """
- **Sample k nodes without replacement** (Algorithm R). Fill the reservoir
  with the first k. For i > k draw `j = randrange(i)`; if `j < k`, overwrite
  `reservoir[j]`. Same telescoping proof gives k/n each.
- **Weighted reservoir** (A-Res). Give item i the key `u^(1/wᵢ)` with u
  uniform on (0,1) and keep the k largest keys in a min-heap — O(log k) per
  item, and the classic answer to "weighted sampling from a stream".
- **Fewer RNG calls** (Algorithm L). Sample how many items to *skip* rather
  than flipping a coin for each, cutting draws from n to O(k log(n/k)). Worth
  naming if they push on the O(n) draws.
- **[Random Pick Index](../random-pick-index/)** — the same one-slot reservoir,
  restricted to matching entries.
- **Distributed sampling.** Reservoirs merge: each shard keeps its own plus its
  item count, and the combiner picks between them weighted by those counts.
  This is why the technique is worth knowing beyond the interview.
""",
        ),
    ],
}


@dataclass
class ListNode:
    val: int
    next: ListNode | None = None


def from_list(values: list[int]) -> ListNode | None:
    head: ListNode | None = None
    for value in reversed(values):
        head = ListNode(value, head)
    return head


class Solution:
    def __init__(self, head: ListNode | None) -> None:
        self.head = head  # no copy, no count — one pointer is the whole state

    def pick(self) -> int:
        chosen: int | None = None
        seen = 0
        node = self.head
        while node:
            seen += 1  # 1-based, incremented before the coin
            if random.randrange(seen) == 0:  # keep the seen-th node w.p. 1/seen
                chosen = node.val
            node = node.next
        if chosen is None:
            raise ValueError("cannot sample from an empty list")
        return chosen


CASES: list[tuple[tuple, object]] = []


def check() -> None:
    # A single node is deterministic; the head is always taken at step 1.
    single = Solution(from_list([9]))
    assert all(single.pick() == 9 for _ in range(100))

    # Empty list: fail loudly rather than return a sentinel that looks like data.
    raised = False
    try:
        Solution(None).pick()
    except ValueError:
        raised = True
    assert raised

    # Two nodes must split 50/50. Taking the head unconditionally and never
    # replacing it gives 20,000/0 here.
    pair = Counter(Solution(from_list([1, 2])).pick() for _ in range(20_000))
    assert set(pair) == {1, 2}
    assert abs(pair[1] - 10_000) < 500

    # Five distinct nodes, uniform to within 1%. A 1/(i+1) off-by-one skews
    # this towards the tail and shows up here.
    draws = 50_000
    picker = Solution(from_list([10, 20, 30, 40, 50]))
    spread = Counter(picker.pick() for _ in range(draws))
    assert set(spread) == {10, 20, 30, 40, 50}
    for value, count in spread.items():
        assert abs(count - draws / 5) < 550, f"{value} came up {count} times"

    # Duplicate values: the *positions* are sampled, so a value appearing twice
    # must come out twice as often.
    weighted = Counter(Solution(from_list([7, 7, 8, 9])).pick() for _ in range(40_000))
    assert set(weighted) == {7, 8, 9}
    assert abs(weighted[7] - 20_000) < 700
    assert abs(weighted[8] - 10_000) < 550

    # Negatives and zero are values like any other.
    signed = Counter(Solution(from_list([-1, 0])).pick() for _ in range(10_000))
    assert set(signed) == {-1, 0}

    # The list is not consumed or mutated: state is one pointer, so repeated
    # picks see the same nodes.
    head = from_list([3, 4, 5])
    reused = Solution(head)
    for _ in range(500):
        assert reused.pick() in {3, 4, 5}
    assert head is not None
    assert [head.val, head.next.val, head.next.next.val] == [3, 4, 5]  # type: ignore[union-attr]

    # A 2,000-node list still needs no length and no storage.
    long_list = Solution(from_list(list(range(2_000))))
    assert all(0 <= long_list.pick() < 2_000 for _ in range(200))
