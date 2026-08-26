"""Merge Two Sorted Lists — LeetCode 21."""

from __future__ import annotations

from dataclasses import dataclass

META = {
    "pattern": "linked-lists",
    "symbol": "merge_two_lists",
    "insight": "A dummy head deletes the 'is this the first node yet' branch, leaving a loop of one comparison and one splice.",
    "time": "O(m + n)",
    "space": "O(1) — nodes are re-linked, never copied",
    "sections": [
        (
            "What it asks",
            """
Splice two sorted lists into one sorted list and return its head.

Ask two things. **Splice or copy?** — splice; the interviewer wants pointer
work, and allocating `m + n` fresh nodes throws away the only reason the input
is a linked list. **Which list wins a tie?** — take from `a` when values are
equal and the merge is *stable*, which is exactly what Merge k Sorted Lists and
Sort List need from it.
""",
        ),
        (
            "The insight",
            """
Every version written without a dummy head opens with the same twenty lines: is
the result empty yet, is this the first node, do I have a tail to attach to. A
dummy node answers all of that before the loop starts — `tail` is always a real
node, so `tail.next = ...` is always legal.

Two more things keep it short:

- **Attach the remainder, do not walk it.** When one list runs out, the other is
  already sorted and already linked. One assignment (`tail.next = a or b`) takes
  all of it. Looping over it node by node is the same answer with more places to
  go wrong.
- **Return `dummy.next`, never `dummy`.** Dropping that one line returns a list
  with a phantom `0` on the front, and it is the most common slip here by a wide
  margin.
""",
        ),
        (
            "Edge cases",
            """
- **One or both lists empty.** The dummy head handles it with no special case:
  the loop never runs, and `tail.next = a or b` does everything.
- **All of `a` below all of `b`, and the reverse.** These are the cases that
  actually exercise the remainder line; a merge that walks the leftover instead
  of attaching it usually still passes them, which is why they are worth having.
- **Equal values across the two lists.** `a.val <= b.val` is stable, `<` is not.
  Both return a sorted list, so tests pass either way and the bug only surfaces
  later, inside whatever stable sort you built on top of this.
- **The recursive one-liner** is four lines and O(m + n) stack. At LeetCode's 50
  nodes it is fine; say the trade out loud rather than reaching for it silently,
  because the same instinct at n = 10⁵ blows the stack.
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


def merge_two_lists(a: ListNode | None, b: ListNode | None) -> ListNode | None:
    dummy = ListNode(0)  # so `tail` is never None and needs no special case
    tail = dummy

    while a and b:
        if a.val <= b.val:  # <= not <, so equal keys keep their original order
            tail.next = a
            a = a.next
        else:
            tail.next = b
            b = b.next
        tail = tail.next

    tail.next = a or b  # the rest is already sorted and already linked

    return dummy.next  # not `dummy`


CASES = [
    (([1, 2, 4], [1, 3, 4]), [1, 1, 2, 3, 4, 4]),
    (([], []), []),
    (([], [0]), [0]),
    (([5], []), [5]),
    (([1, 2, 3], [4, 5, 6]), [1, 2, 3, 4, 5, 6]),
    (([4, 5, 6], [1, 2, 3]), [1, 2, 3, 4, 5, 6]),
    (([2, 2, 2], [2, 2]), [2, 2, 2, 2, 2]),
    (([-9, -3, 0], [-7, -1, 2]), [-9, -7, -3, -1, 0, 2]),
]


def solve(a: list[int], b: list[int]) -> list[int]:
    return to_list(merge_two_lists(from_list(a), from_list(b)))
