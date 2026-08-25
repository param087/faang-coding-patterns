"""Linked list templates.

Three habits prevent nearly every bug here: use a dummy head so the first node
is not a special case, save `node.next` before you overwrite it, and draw the
pointers for a two-element list before claiming the code works.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Node:
    """Minimal singly-linked node."""

    val: int
    next: Node | None = None


def from_list(values: list[int]) -> Node | None:
    """Build a list from a Python list, for testing."""
    head: Node | None = None
    for value in reversed(values):
        head = Node(value, head)
    return head


def to_list(head: Node | None) -> list[int]:
    """Read a list back out, for testing."""
    out: list[int] = []
    while head:
        out.append(head.val)
        head = head.next
    return out


def reverse(head: Node | None) -> Node | None:
    """Reverse in place, iteratively.

    Three pointers and a strict order: save the next node *first*, because
    the very next statement destroys the link you would need to find it.
    """
    previous: Node | None = None
    current = head

    while current:
        following = current.next  # save before overwriting
        current.next = previous
        previous = current
        current = following

    return previous


def middle(head: Node | None) -> Node | None:
    """Middle node; the second of the two for even length.

    Fast and slow pointers. Whether you get the first or second middle on an
    even-length list depends on the loop condition — `fast and fast.next`
    gives the second, `fast.next and fast.next.next` gives the first. Ask
    which the problem wants.
    """
    slow = fast = head
    while fast and fast.next:
        slow = slow.next if slow else None
        fast = fast.next.next
    return slow


def merge_two(a: Node | None, b: Node | None) -> Node | None:
    """Merge two sorted lists.

    The dummy head is the point: without it the first node needs a special
    case, and that special case is where the bug lives.
    """
    dummy = Node(0)
    tail = dummy

    while a and b:
        if a.val <= b.val:
            tail.next, a = a, a.next
        else:
            tail.next, b = b, b.next
        tail = tail.next

    tail.next = a or b  # at most one is non-empty
    return dummy.next


def reverse_k_group(head: Node | None, k: int) -> Node | None:
    """Reverse every consecutive group of k nodes; leave any remainder alone.

    The Hard of the family, and it is really three easy things: count ahead
    to check a full group exists, reverse exactly k nodes, then reconnect.
    The `group_prev` pointer is what survives across iterations.
    """
    dummy = Node(0, head)
    group_prev = dummy

    while True:
        # Does a full group of k remain?
        node = group_prev
        for _ in range(k):
            node = node.next if node else None
            if not node:
                return dummy.next
        group_next = node.next

        # Reverse exactly k nodes, ending pointed at group_next.
        previous, current = group_next, group_prev.next
        for _ in range(k):
            if not current:
                break
            following = current.next
            current.next = previous
            previous = current
            current = following

        # group_prev.next is still the old head, which is now the group's tail.
        new_group_prev = group_prev.next
        group_prev.next = previous
        group_prev = new_group_prev if new_group_prev else group_prev


CASES = [
    (([1, 2, 3, 4, 5],), [5, 4, 3, 2, 1]),
    (([1, 2],), [2, 1]),
    (([1],), [1]),
    (([],), []),
]


def solve(values: list[int]) -> list[int]:
    return to_list(reverse(from_list(values)))


def check() -> None:
    for args, expected in CASES:
        assert solve(*args) == expected

    node = middle(from_list([1, 2, 3, 4, 5]))
    assert node is not None and node.val == 3
    node = middle(from_list([1, 2, 3, 4]))
    assert node is not None and node.val == 3  # second middle
    assert middle(None) is None

    assert to_list(merge_two(from_list([1, 2, 4]), from_list([1, 3, 4]))) == [1, 1, 2, 3, 4, 4]
    assert to_list(merge_two(None, from_list([0]))) == [0]
    assert to_list(merge_two(None, None)) == []

    assert to_list(reverse_k_group(from_list([1, 2, 3, 4, 5]), 2)) == [2, 1, 4, 3, 5]
    assert to_list(reverse_k_group(from_list([1, 2, 3, 4, 5]), 3)) == [3, 2, 1, 4, 5]
    assert to_list(reverse_k_group(from_list([1, 2, 3]), 1)) == [1, 2, 3]
    assert to_list(reverse_k_group(from_list([1, 2]), 3)) == [1, 2]  # remainder untouched
