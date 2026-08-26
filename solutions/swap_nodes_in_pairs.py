"""Swap Nodes in Pairs — LeetCode 24."""

from __future__ import annotations

from dataclasses import dataclass

META = {
    "pattern": "linked-lists",
    "symbol": "swap_pairs",
    "insight": "A dummy head turns the head swap into an ordinary swap, so one loop body handles every pair including the first.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Swap every two adjacent nodes and return the new head. An odd final node stays
where it is. The nodes themselves must move — **values may not be swapped**.

That constraint is the entire problem, so confirm it out loud rather than
assuming it. It is also the honest engineering position: in real code a node
carries a payload and other references point at it, so relocating a value
silently corrupts anyone holding the node.
""",
        ),
        (
            "The insight",
            """
Every swap needs the node *before* the pair, because that node's `next` has to
be redirected to the pair's second node. For the very first pair there is no
such node — which is why an implementation without a dummy head ends up with a
special case before the loop and an off-by-one inside it.

Allocate `dummy → head` and the first pair stops being special. Then the loop
is uniform: while there are two more nodes after `prev`, swap them and advance
`prev` by two.

The condition `prev.next and prev.next.next` is doing double duty — it is both
the loop guard and the odd-length handler. A trailing single node fails the
second half of the test and is left untouched, which is exactly what the
problem wants.
""",
        ),
        (
            "The order of the three rewrites",
            """
With `first = prev.next` and `second = first.next`:

```python
first.next = second.next   # 1. first now points past the pair
second.next = first        # 2. second leads
prev.next = second         # 3. the boundary catches up
```

Swap (1) and (2) and it breaks outright: `second.next = first` first, so step
1 then reads `second.next` and links `first` **to itself**. Self-cycle, and
the traversal never terminates — no exception, just a hang.

Naming `first` and `second` up front is what buys the freedom in the rest of
the ordering. Written without locals, chasing `prev.next.next.next` through
three levels, every line depends on fields the previous line moved and the
whole thing is unreviewable.

Then advance `prev = first`, not `prev = second`. After the swap `first` is
the *trailing* node of the pair, and that is the boundary for the next one.
""",
        ),
    ],
}


@dataclass
class ListNode:
    val: int = 0
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


def swap_pairs(head: ListNode | None) -> ListNode | None:
    dummy = ListNode(0, head)
    prev = dummy

    # The guard is also the odd-length handler: a lone trailing node fails it.
    while prev.next and prev.next.next:
        first = prev.next
        second = first.next

        first.next = second.next
        second.next = first
        prev.next = second

        prev = first  # first is the pair's trailing node now

    return dummy.next


CASES = [
    (([1, 2, 3, 4],), [2, 1, 4, 3]),
    (([1, 2, 3],), [2, 1, 3]),
    (([1, 2, 3, 4, 5, 6],), [2, 1, 4, 3, 6, 5]),
    (([1, 2],), [2, 1]),
    (([1],), [1]),
    (([],), []),
    (([1, 1, 2, 3],), [1, 1, 3, 2]),
]


def solve(values: list[int]) -> list[int]:
    return to_list(swap_pairs(from_list(values)))
