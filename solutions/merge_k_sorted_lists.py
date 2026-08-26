"""Merge k Sorted Lists — LeetCode 23."""

from __future__ import annotations

import heapq
from dataclasses import dataclass

META = {
    "pattern": "linked-lists",
    "symbol": "merge_k_lists",
    "insight": "Only the k current heads can be the next output, so keep exactly those k in a heap instead of rescanning them.",
    "time": "O(N log k) for N nodes across k lists",
    "space": "O(k)",
    "sections": [
        (
            "What it asks",
            """
Merge `k` sorted linked lists into one sorted list. Some of the `k` lists may
be empty, and the array of lists itself may be empty.

Ask for the shape of the input: **many short lists or a few long ones?** With
k = 10⁴ lists of one node each, the heap's `log k` matters; with k = 2 you
should just write the two-pointer merge and stop.
""",
        ),
        (
            "The insight",
            """
At every step the next node of the output can only be one of the `k` current
heads. Rescanning all `k` heads each time is O(N·k) — at N = 10⁴ and k = 10⁴
that is 10⁸ comparisons. A **min-heap of exactly those k heads** turns each
step into `log k`: pop the smallest, append it, push its successor.

The heap never holds more than `k` entries, so the extra space is O(k)
regardless of how long the lists are — you are re-pointing existing nodes, not
allocating new ones.

The other accepted answer is **divide and conquer**: pairwise-merge the lists,
halving `k` each round. Same O(N log k), O(1) extra space, and it is the
better answer if the interviewer bans heaps or asks about space. Both are
worth naming; write whichever you can code cleanly under pressure.
""",
        ),
        (
            "The tie-breaker that stops the TypeError",
            """
Push `(node.val, i, node)` — never `(node.val, node)`.

Python compares tuples element by element. The moment two heads hold the same
value it reaches the third element and tries `node_a < node_b`, and a list
node has no ordering:

```
TypeError: '<' not supported between instances of 'ListNode' and 'ListNode'
```

Duplicate values across lists are the *normal* case here, so this is not a
corner: `[[1,4,5],[1,3,4]]` triggers it on the very first pop. The list index
`i` is unique among live heap entries — each list contributes at most one —
so the comparison always resolves before it reaches the node.
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


def merge_k_lists(lists: list[ListNode | None]) -> ListNode | None:
    # (value, list index, node) — the index breaks value ties before Python
    # ever tries to compare two ListNodes.
    heap: list[tuple[int, int, ListNode]] = []
    for i, node in enumerate(lists):
        if node is not None:
            heapq.heappush(heap, (node.val, i, node))

    dummy = ListNode()
    tail = dummy
    while heap:
        _, i, node = heapq.heappop(heap)
        tail.next = node
        tail = node
        if node.next is not None:
            heapq.heappush(heap, (node.next.val, i, node.next))

    return dummy.next


CASES = [
    (([[1, 4, 5], [1, 3, 4], [2, 6]],), [1, 1, 2, 3, 4, 4, 5, 6]),
    (([[1, 1, 1], [1, 1]],), [1, 1, 1, 1, 1]),
    (([[-5, -1], [-3, 0], []],), [-5, -3, -1, 0]),
    (([[], [1]],), [1]),
    (([[], []],), []),
    (([[]],), []),
    (([],), []),
    (([[2], [1], [3]],), [1, 2, 3]),
]


def solve(lists: list[list[int]]) -> list[int]:
    return to_list(merge_k_lists([from_list(values) for values in lists]))
