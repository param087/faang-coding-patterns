"""Remove Nth Node From End of List — LeetCode 19."""

from __future__ import annotations

from dataclasses import dataclass

META = {
    "pattern": "linked-lists",
    "symbol": "remove_nth_from_end",
    "insight": "Open a fixed gap of n + 1 between two pointers and 'nth from the end' becomes 'whatever the trailing pointer is looking at'.",
    "time": "O(n), one pass",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Delete the `n`-th node counting from the end and return the head. `n` is
guaranteed valid — `1 <= n <= length` — so no bounds handling is required, but
say that you checked rather than assuming it.

Ask whether one pass is required. Two passes (count, then walk `length - n`) is
correct and easier to get right; the follow-up asking for one pass is the whole
reason the problem exists.
""",
        ),
        (
            "The insight",
            """
You cannot index backwards in a singly linked list, but you can carry a fixed
distance forward. Advance a lead pointer `n + 1` nodes, then move both until the
lead falls off the end. The gap never changes, so when the lead is `None` the
trailing pointer is `n + 1` nodes from the end — that is, sitting on the node
**before** the one to delete, which is exactly what a singly linked list needs
in order to unlink anything.

The distinction between `n` and `n + 1` is the whole problem. A gap of `n`
leaves you *on* the doomed node with no way back to its predecessor, and the
usual recovery is to start over with a "previous" variable — twice the pointers
and twice the ways to get it wrong.
""",
        ),
        (
            "The dummy head is not decoration",
            """
When `n == length` the node to delete is the head itself, and there is no
predecessor to rewire. Every solution to this problem either has a dummy node in
front of the head or an `if` that special-cases head removal; the dummy is the
one that does not grow a second bug.

Start **both** pointers at the dummy, not at the head. Then advancing the lead
`n + 1` times lands it on `None` exactly when the head is the target, the while
loop never runs, `trail` is still the dummy, and `trail.next = trail.next.next`
drops the head correctly. Return `dummy.next` — with a head deletion that value
is genuinely different from `head`, so returning `head` here returns a list you
just detached.

Test `[1], n = 1` before you say you are done. It is the case that catches a
missing dummy, and it returns the empty list rather than a node.
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


def remove_nth_from_end(head: ListNode | None, n: int) -> ListNode | None:
    dummy = ListNode(0, head)  # so deleting the head is not a special case

    lead: ListNode | None = dummy
    for _ in range(n + 1):  # n + 1, so `trail` stops one node early
        lead = lead.next

    trail = dummy
    while lead:
        lead = lead.next
        trail = trail.next

    trail.next = trail.next.next  # trail is the predecessor of the target
    return dummy.next  # not `head`, which may be the node just removed


CASES = [
    (([1, 2, 3, 4, 5], 2), [1, 2, 3, 5]),
    (([1], 1), []),
    (([1, 2], 1), [1]),
    (([1, 2], 2), [2]),  # head removal
    (([1, 2, 3, 4, 5], 5), [2, 3, 4, 5]),
    (([1, 2, 3, 4, 5], 1), [1, 2, 3, 4]),  # tail removal
    (([7, 7, 7], 2), [7, 7]),
]


def solve(values: list[int], n: int) -> list[int]:
    return to_list(remove_nth_from_end(from_list(values), n))
