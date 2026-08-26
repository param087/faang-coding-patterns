"""Middle of the Linked List — LeetCode 876."""

from __future__ import annotations

from dataclasses import dataclass

META = {
    "pattern": "linked-lists",
    "symbol": "middle_node",
    "insight": "Which of the two middles you land on is decided entirely by the fast pointer's stop condition, not by the algorithm.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Return the middle node — and for an even-length list, the **second** of the two
middles.

That last clause is the entire question. Ask it if the statement does not say,
because the two answers differ by one token in the loop condition and every
list-splitting problem downstream (Reorder List, Sort List, Palindrome Linked
List) needs the *first* middle instead.
""",
        ),
        (
            "The insight",
            """
Two passes — count the length, then walk `n // 2` nodes — is a perfectly correct
O(n) answer and nobody will fail you for it. The one-pass version exists because
it generalises: the same slow/fast skeleton finds cycles (LeetCode 141), the
cycle entry (142), and the `k`-th node from the end.

When `fast` has moved `2i` nodes, `slow` has moved `i`. Stop when `fast` cannot
move twice more, and `slow` is sitting at the halfway mark. No length, no second
traversal.
""",
        ),
        (
            "Second middle versus first middle",
            """
```python
while fast and fast.next:                  # -> SECOND middle (this problem)
while fast.next and fast.next.next:        # -> FIRST middle (splitting)
```

For `[1, 2, 3, 4]` the first form returns `3`, the second returns `2`. Both are
"the middle"; only one is the answer to a given question.

The distinction is not pedantry. When you split a list for merge sort or Reorder
List you need `slow` on the **last node of the first half**, so that
`slow.next = None` severs it cleanly. Use the `fast and fast.next` form there and
a two-node list splits into two-and-zero, which recurses forever.

The second form dereferences `fast.next` immediately, so it needs `head` to be
non-null before the loop. This problem's form does not — an empty list returns
`None` with no special case.
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


def middle_node(head: ListNode | None) -> ListNode | None:
    slow = fast = head

    while fast and fast.next:  # second middle when the length is even
        slow = slow.next
        fast = fast.next.next

    return slow


CASES = [
    (([1, 2, 3, 4, 5],), [3, 4, 5]),
    (([1, 2, 3, 4, 5, 6],), [4, 5, 6]),  # the second middle, not the first
    (([1, 2],), [2]),
    (([1],), [1]),
    (([],), []),
    (([1, 2, 3, 4],), [3, 4]),
    (([-1, -2, -3],), [-2, -3]),
]


def solve(values: list[int]) -> list[int]:
    """Return the list from the middle onwards, which pins down *which* node."""
    return to_list(middle_node(from_list(values)))
