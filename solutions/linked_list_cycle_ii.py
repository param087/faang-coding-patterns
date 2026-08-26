"""Linked List Cycle II — LeetCode 142."""

from __future__ import annotations

from dataclasses import dataclass

META = {
    "pattern": "linked-lists",
    "symbol": "detect_cycle",
    "insight": "After the pointers meet, the distance from the head to the cycle entry equals the distance from the meeting point to it.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Return the node where the cycle begins, or `None` if the list has no cycle.
You may not modify the list, and the follow-up asks for O(1) memory.

The hash-set answer — walk, storing every node visited, return the first
repeat — is O(n) time and correct, and takes fifteen seconds to write. Say it,
then say "but the O(1)-space version is Floyd's, and the second phase is the
part worth showing". Skipping straight to Floyd's without acknowledging the
set reads as memorisation.
""",
        ),
        (
            "The insight",
            """
Phase one is Linked List Cycle: advance `slow` one and `fast` two until they
land on the same node. Phase two is the part this problem exists for.

Let `L` be the distance from the head to the cycle entry, `a` the distance
from the entry to the meeting point, and `C` the cycle length. When they meet,
`slow` has walked `L + a` and `fast` exactly twice that:

```
2(L + a) = L + a + nC   →   L + a = nC   →   L = nC - a
```

`nC - a` is "walk from the meeting point back round to the entry, possibly
lapping the cycle `n - 1` times". So a pointer restarted at the **head** and a
pointer left at the **meeting point**, both stepping one at a time, arrive at
the entry together. That is the whole trick: two single-speed pointers,
converging on the answer.

There is no third phase and no cycle-length measurement — those are the
signature of someone reconstructing the algorithm rather than knowing it.
""",
        ),
        (
            "Compare with `is`, never with `==`",
            """
`slow == fast` is not "the same node", it is "equal values", and duplicate
values in a list are ordinary. Worse, with a dataclass node, `==` compares
fields — including `next` — so on a cyclic list Python follows the loop
recursively and dies with `RecursionError` rather than giving a wrong answer.

Two more details that decide the submission:

- Guard `fast and fast.next` **before** the double step, otherwise an
  acyclic list raises `AttributeError` on `None.next`.
- Start both pointers at the head. Some write-ups start `fast = head.next` to
  match Cycle I; the phase-two arithmetic above assumes both start at the
  head, and the offset version returns a node one hop early.
""",
        ),
    ],
}


@dataclass
class ListNode:
    val: int = 0
    next: ListNode | None = None


def detect_cycle(head: ListNode | None) -> ListNode | None:
    slow, fast = head, head

    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:  # identity, not equality
            finder = head
            while finder is not slow:
                finder = finder.next
                slow = slow.next
            return finder

    return None


def build_with_cycle(values: list[int], pos: int) -> ListNode | None:
    """Link the tail back to index `pos`; pos < 0 leaves the list acyclic."""
    nodes = [ListNode(value) for value in values]
    for i in range(len(nodes) - 1):
        nodes[i].next = nodes[i + 1]
    if nodes and 0 <= pos < len(nodes):
        nodes[-1].next = nodes[pos]
    return nodes[0] if nodes else None


CASES = [
    (([3, 2, 0, -4], 1), 1),
    (([1, 2], 0), 0),
    (([1, 2, 3, 4, 5], 4), 4),
    (([1, 1, 1, 1], 2), 2),
    (([1], 0), 0),
    (([1], -1), -1),
    (([1, 2, 3], -1), -1),
    (([], -1), -1),
]


def solve(values: list[int], pos: int) -> int:
    head = build_with_cycle(values, pos)
    entry = detect_cycle(head)
    if entry is None:
        return -1

    index, node = 0, head
    while node is not entry:
        node = node.next
        index += 1
    return index
