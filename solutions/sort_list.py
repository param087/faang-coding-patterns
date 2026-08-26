"""Sort List — LeetCode 148."""

from __future__ import annotations

from dataclasses import dataclass

META = {
    "pattern": "linked-lists",
    "symbol": "sort_list",
    "insight": "Merge sort is the only classic sort that never needs random access, which is exactly what a linked list cannot give you.",
    "time": "O(n log n)",
    "space": "O(log n) recursion stack — O(1) if you write it bottom-up",
    "sections": [
        (
            "What it asks",
            """
Sort a singly linked list in ascending order and return the new head. The
expected bound is stated: **O(n log n) time, O(1) extra space**.

Ask whether "O(1) space" includes the recursion stack. Most interviewers
accept top-down merge sort at O(log n) stack depth, but the honest answer is
to name the bottom-up version and let them choose.
""",
        ),
        (
            "The insight",
            """
Quicksort needs random access to partition well; heapsort needs indexing.
**Merge sort needs neither** — it only ever walks forward and splices, which
is all a singly linked list offers. That is why it is the answer here and not
merely one option among several.

The other half of the insight is that merging linked lists is *cheaper* than
merging arrays: no scratch buffer, just pointer reassignment, so the O(n)
auxiliary array that array merge sort needs disappears.

Three moves:

1. **Split** at the midpoint with slow/fast pointers, and **cut** the first
   half by setting `slow.next = None`.
2. **Recurse** on both halves.
3. **Merge** with a dummy head, taking `left` on ties so the sort stays
   stable.

Dropping the cut in step 1 is the classic failure: both halves still see the
whole list, and you sort the same nodes over and over.
""",
        ),
        (
            "The split that must strictly shrink",
            """
Start `fast` at `head.next`, not at `head`.

Trace a two-node list `1 → 2` with `slow = fast = head`: the loop condition
`fast and fast.next` holds, so `slow` moves to `2` and `fast` to `None`. Now
`mid = slow.next` is `None`, the right half is empty, the left half is still
the entire list — and the recursion calls itself on the same input forever
until it dies with `RecursionError`.

Seeding `fast = head.next` makes `slow` stop on `1`, splitting 1/1. The rule
for any divide-and-conquer on a list: **prove the two-element case splits
1/1**, because that is the smallest input that still recurses, and every
infinite loop in this problem lives there.
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


def sort_list(head: ListNode | None) -> ListNode | None:
    if head is None or head.next is None:
        return head

    # Split. fast starts one ahead so a two-node list splits 1/1, not 2/0.
    slow, fast = head, head.next
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    right = slow.next
    slow.next = None  # cut, or both halves still see the whole list

    left = sort_list(head)
    right = sort_list(right)

    # Merge, taking the left node on ties so the sort is stable.
    dummy = ListNode()
    tail = dummy
    while left and right:
        if left.val <= right.val:
            tail.next, left = left, left.next
        else:
            tail.next, right = right, right.next
        tail = tail.next
    tail.next = left or right

    return dummy.next


CASES = [
    (([4, 2, 1, 3],), [1, 2, 3, 4]),
    (([-1, 5, 3, 4, 0],), [-1, 0, 3, 4, 5]),
    (([5, 4, 3, 2, 1],), [1, 2, 3, 4, 5]),
    (([3, 3, 1, 1, 2],), [1, 1, 2, 3, 3]),
    (([2, 1],), [1, 2]),
    (([1, 2],), [1, 2]),
    (([9],), [9]),
    (([],), []),
]


def solve(values: list[int]) -> list[int]:
    return to_list(sort_list(from_list(values)))
