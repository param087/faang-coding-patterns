"""Linked List Cycle — LeetCode 141."""

from __future__ import annotations

from dataclasses import dataclass

META = {
    "pattern": "linked-lists",
    "symbol": "has_cycle",
    "insight": "Once both pointers are inside a loop the gap between them shrinks by exactly one per step, so a collision is forced.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Return whether the list contains a cycle. `pos` in the test harness is a
description of the input, not an argument you get — you only ever receive the
head.

Ask whether O(1) space is required. If it is not, the honest answer is a set of
visited nodes: eight lines, obviously correct, O(n) memory. Say that first, then
say you can do it in O(1), then write Floyd's.
""",
        ),
        (
            "The insight",
            """
Run one pointer at one node per step and another at two. If the list ends, the
fast one falls off and there is no cycle. If it does not end, both pointers
eventually enter the loop, and from that moment the fast pointer gains exactly
**one** position per step on the slow one.

A gap that shrinks by one every step and lives on a cycle of length `L` cannot
be skipped over — it hits zero within `L` steps. That is the whole proof, and it
is the thing to say out loud, because "they meet eventually" is hand-waving and
"the gap closes by one per step so it cannot jump past zero" is not.

Note the consequence: the meeting point is **not** the start of the cycle. That
matters in the sequel (LeetCode 142), where you reset one pointer to the head
and walk both at speed one to find the entry node.
""",
        ),
        (
            "The two ways it breaks",
            """
- **The loop condition must be `while fast and fast.next`.** Both, in that
  order. `fast.next.next` needs `fast.next` to exist, and Python's `and` short
  circuits so the order is doing real work. Testing only `fast` raises
  `AttributeError` on every even-length acyclic list.
- **Compare identity, not values.** `slow is fast`, never `slow == fast`. On
  `[1, 1, 1, 1]` with no cycle, value comparison reports a cycle on the first
  step — a case in `CASES` below precisely because it is the one that separates
  a correct solution from one that passes the samples.

Both pointers starting at `head` is fine: the loop body advances before it
compares, so the initial `slow is fast` is never tested. Starting `fast` at
`head.next` also works but then needs its own null guard, which is why it is not
worth it.
""",
        ),
    ],
}


@dataclass(eq=False, repr=False)  # a cycle makes generated __eq__/__repr__ recurse forever
class ListNode:
    val: int
    next: ListNode | None = None


def from_list(values: list[int], pos: int = -1) -> ListNode | None:
    """Build a list; if `pos` >= 0, link the tail back to index `pos`."""
    head: ListNode | None = None
    for value in reversed(values):
        head = ListNode(value, head)
    if head is None or pos < 0:
        return head

    tail = head
    while tail.next:
        tail = tail.next
    entry = head
    for _ in range(pos):
        assert entry.next is not None
        entry = entry.next
    tail.next = entry
    return head


def has_cycle(head: ListNode | None) -> bool:
    slow = fast = head

    while fast and fast.next:  # both checks, in this order
        slow = slow.next  # slow trails fast, so it cannot be None here
        fast = fast.next.next
        if slow is fast:  # identity, not ==
            return True

    return False


CASES = [
    (([3, 2, 0, -4], 1), True),
    (([1, 2], 0), True),
    (([1], 0), True),  # a node pointing at itself
    (([1], -1), False),
    (([], -1), False),
    (([1, 2, 3, 4, 5], -1), False),
    (([1, 1, 1, 1], -1), False),  # kills `slow == fast`
    (([3, 2, 0, -4], 3), True),  # cycle of length one at the tail
]


def solve(values: list[int], pos: int) -> bool:
    return has_cycle(from_list(values, pos))
