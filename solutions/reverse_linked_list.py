"""Reverse Linked List — LeetCode 206."""

from __future__ import annotations

from dataclasses import dataclass

META = {
    "pattern": "linked-lists",
    "symbol": "reverse_list",
    "insight": "Three pointers, one strict order — save the next node before you overwrite the link that finds it.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Reverse a singly linked list and return the new head.

Ask: in place or a new list; iterative or recursive preferred; can the list be
empty.
""",
        ),
        (
            "Why it is asked",
            """
It is the calibration question of the category. The interviewer wants to see
the three-pointer dance written cleanly and without hesitation — fumbling it
colours everything that comes after.

It is also the building block for Reorder List, Palindrome Linked List, and
Reverse Nodes in k-Group, so it is worth having in your fingers rather than
deriving each time.
""",
        ),
        (
            "The order is not negotiable",
            """
`following = current.next` must come **first**. The very next statement
(`current.next = previous`) destroys the only link that could find the rest of
the list.

The loop ends with `current` at `None` and `previous` at the new head, so you
return **`previous`**. Returning `current` is the classic slip and it returns
`None` every time.
""",
        ),
        (
            "Dry run two nodes",
            """
Do this out loud; it takes twenty seconds and catches both bugs.

`1 → 2`. Start `previous = None`, `current = 1`.

- Save `following = 2`; `1.next = None`; `previous = 1`; `current = 2`.
- Save `following = None`; `2.next = 1`; `previous = 2`; `current = None`.
- Loop ends. Return `previous` = **2**, and the list is `2 → 1`. ✓
""",
        ),
        (
            "The recursive version",
            """
Be able to write it, and be able to say why you would not ship it: **O(n)
stack space**, and at n = 10⁵ it exceeds Python's recursion limit.

"Iterative, because the recursive one is O(n) stack and would overflow at the
stated constraint" is a complete answer to "which would you use".
""",
        ),
        (
            "Follow-ups",
            """
- **Reverse Linked List II** — reverse only between positions `m` and `n`.
  Same loop, plus a dummy head and two saved boundary pointers.
- **Reverse Nodes in k-Group** — the Hard version, which is this loop plus a
  look-ahead check and a reconnection step.
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


def to_list(head: ListNode | None) -> list[int]:
    out: list[int] = []
    while head:
        out.append(head.val)
        head = head.next
    return out


def reverse_list(head: ListNode | None) -> ListNode | None:
    previous: ListNode | None = None
    current = head

    while current:
        following = current.next  # save BEFORE overwriting
        current.next = previous
        previous = current
        current = following

    return previous  # not `current`, which is None here


CASES = [
    (([1, 2, 3, 4, 5],), [5, 4, 3, 2, 1]),
    (([1, 2],), [2, 1]),
    (([1],), [1]),
    (([],), []),
]


def solve(values: list[int]) -> list[int]:
    return to_list(reverse_list(from_list(values)))
