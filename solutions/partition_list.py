"""Partition List — LeetCode 86."""

from __future__ import annotations

from dataclasses import dataclass

META = {
    "pattern": "linked-lists",
    "symbol": "partition",
    "insight": "Build two lists instead of moving nodes within one; relative order survives for free and there is no swapping to get wrong.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Rearrange the list so every node with value `< x` comes before every node with
value `>= x`, **preserving the relative order within each group**.

That stability clause rules out the tempting in-place answers. Quicksort's
Lomuto partition on an array is not stable, and neither is any scheme that
swaps a small node forward past nodes it should stay behind. Confirm the
requirement — an unstable answer looks right on `[1,4,3,2,5,2]` and is wrong
on half of everything else.
""",
        ),
        (
            "The insight",
            """
Stop trying to rearrange one list. Walk once and **deal each node into one of
two lists**, each with its own dummy head and tail pointer: `less` for
`val < x`, `greater` for the rest. Append at the tail, so within each list the
original order is untouched — stability is not something you preserve, it is
something you never disturb.

Then join: `less_tail.next = greater_dummy.next` and return
`less_dummy.next`. One pass, no node allocation, O(1) extra space.

Note that `x` need not appear in the list, and nodes equal to `x` go to the
`greater` side. The comparison is `< x` on one side and everything else on the
other — a single `if`, no three-way split.
""",
        ),
        (
            "The line everyone forgets",
            """
`greater_tail.next = None` before joining. This is the bug that separates a
working submission from an infinite loop.

Every node kept the `next` it arrived with. If the original list ended with a
node that went to the `greater` side, its `next` is already `None` and you are
lucky. If it ended on the `less` side, the last `greater` node still points
back into the middle of the list — and after the join that region is behind
it.

`[2, 1]` with `x = 2` is the smallest case that shows it. `2` goes to
`greater`, `1` to `less`. Without the null, `2.next` is still `1`, and the
join makes `1.next = 2`: the returned list is `1 → 2 → 1 → 2 → …`. The test
harness does not fail, it hangs.

Trailing pointers are the recurring hazard in this whole category. Whenever
you split a list into pieces, terminate every piece before you reassemble
them.
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


def partition(head: ListNode | None, x: int) -> ListNode | None:
    less_dummy = ListNode()
    greater_dummy = ListNode()
    less, greater = less_dummy, greater_dummy

    node = head
    while node:
        if node.val < x:
            less.next = node
            less = node
        else:
            greater.next = node
            greater = node
        node = node.next

    greater.next = None  # terminate, or the join builds a cycle
    less.next = greater_dummy.next

    return less_dummy.next


CASES = [
    (([1, 4, 3, 2, 5, 2], 3), [1, 2, 2, 4, 3, 5]),
    (([2, 1], 2), [1, 2]),
    (([4, 3, 2, 5, 2], 3), [2, 2, 4, 3, 5]),
    (([3, 3, 3], 3), [3, 3, 3]),
    (([5, 4, 3], 10), [5, 4, 3]),
    (([1, 2, 3], 0), [1, 2, 3]),
    (([1], 2), [1]),
    (([], 0), []),
]


def solve(values: list[int], x: int) -> list[int]:
    return to_list(partition(from_list(values), x))
