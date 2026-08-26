"""Palindrome Linked List — LeetCode 234."""

from __future__ import annotations

from dataclasses import dataclass

META = {
    "pattern": "linked-lists",
    "symbol": "is_palindrome",
    "insight": "Reverse the second half in place so both halves walk forwards together — then put it back, because you mutated the caller's list.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Return whether the list reads the same forwards and backwards.

Copy the values into an array and compare with its reverse: three lines, O(n)
time, O(n) space, and it is the right thing to say first. The follow-up — "O(n)
time and O(1) space" — is the actual question, and the reason this Easy-tagged
problem shows up in real loops.

Worth asking: **may I mutate the list?** Most interviewers say yes and then
watch whether you put it back.
""",
        ),
        (
            "The insight",
            """
The obstacle is that a singly linked list has no backwards. So make one: reverse
the second half in place, then walk `left` from the head and `right` from the
new head of the reversed half. Three routines you already own — find the middle,
reverse a list, compare two lists — glued together.

Two details do the work:

- Stop `slow` on the **last node of the first half** (`while fast.next and
  fast.next.next`), not on the second middle. Then `slow.next` is precisely the
  second half to reverse, for both parities.
- Drive the comparison loop on `right`, not on `left`. For an odd length the
  second half is one node shorter, so the middle node is skipped automatically —
  which is what you want, since a single centre element is always a palindrome.

The comparison never needs a length check because `right` running out ends it.
""",
        ),
        (
            "Restore what you reversed",
            """
Halfway through this algorithm the caller's list is spliced into two chains, one
of them backwards. If anything else holds a pointer into it — and in production
something always does — you have corrupted shared data to answer a yes/no
question.

Reversing the second half again and reattaching it costs one more O(n/2) pass
and takes one line. Volunteering it is a cheap, genuine signal; being asked for
it after you declared yourself finished is the opposite.

Also state the trade honestly: the O(1) version is not thread safe even for a
read-only caller, because for the duration of the scan the list is not the list.
Under concurrency, the O(n) copy is the correct engineering answer and "I would
ship the array version here" is a better answer than the clever one.
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


def is_palindrome(head: ListNode | None) -> bool:
    def reverse(node: ListNode | None) -> ListNode | None:
        previous: ListNode | None = None
        while node:
            following = node.next
            node.next = previous
            previous = node
            node = following
        return previous

    if head is None or head.next is None:
        return True

    # slow lands on the LAST node of the first half, so slow.next starts half two
    slow, fast = head, head
    while fast.next and fast.next.next:
        slow = slow.next
        fast = fast.next.next

    second = reverse(slow.next)

    left, right = head, second
    matched = True
    while right:  # the shorter half; an odd-length middle is skipped for free
        if left.val != right.val:
            matched = False
            break
        left = left.next
        right = right.next

    slow.next = reverse(second)  # put the caller's list back the way it was
    return matched


CASES = [
    (([1, 2, 2, 1],), True),
    (([1, 2],), False),
    (([1, 2, 3, 2, 1],), True),
    (([1, 2, 3, 3, 1],), False),  # differs one in from the ends
    (([1, 2, 2, 3],), False),
    (([1],), True),
    (([],), True),
    (([-1, 0, -1],), True),
]


def solve(values: list[int]) -> bool:
    return is_palindrome(from_list(values))


def check() -> None:
    for args, expected in CASES:
        assert solve(*args) == expected, (args, expected)

    # The list must survive the scan intact, including the failing path.
    for values in ([1, 2, 3, 2, 1], [1, 2, 2, 1], [1, 2, 3], [1]):
        head = from_list(values)
        is_palindrome(head)
        assert to_list(head) == values, values
