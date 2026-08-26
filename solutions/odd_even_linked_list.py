"""Odd Even Linked List — LeetCode 328."""

from __future__ import annotations

from dataclasses import dataclass

META = {
    "pattern": "linked-lists",
    "symbol": "odd_even_list",
    "insight": "Grow two chains at once out of the alternating nodes, then join them — the only state you must save first is the head of the even chain.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Group the nodes at odd **positions** (1-indexed) before those at even positions,
keeping the relative order inside each group. In place, O(1) space.

Positions, not values. `[2, 4, 6, 8]` becomes `[2, 6, 4, 8]`, not `[2, 4, 6, 8]`
— reading it as "even numbers last" is a genuine misread that survives the sample
case, because the sample happens to be `[1, 2, 3, 4, 5]` where position and value
parity coincide. Confirm which one is meant in one sentence and move on.

"Relative order preserved" also rules out the swap-based approach that would
otherwise be tempting: you are splitting, not permuting.
""",
        ),
        (
            "The insight",
            """
Do not count. Do not index. Walk the list once with two tails — one for the odd
chain, one for the even chain — and notice that each tail's *next* node of the
same parity is exactly `tail.next.next`. So each step is:

```python
odd.next = even.next      # skip the even node
even.next = odd.next.next # skip the odd node just linked
```

The chains consume the list in lockstep, each node is visited once, and no extra
storage is needed beyond three pointers.

The one piece of state you must capture **before** the first rewrite is
`even_head = head.next`. The very first assignment (`odd.next = even.next`)
destroys the only reference to the start of the even chain, and without it there
is nothing to attach at the end. Saving it costs one line and is the difference
between this working and being unrecoverable.
""",
        ),
        (
            "Why the loop tests even, not odd",
            """
`while even and even.next` — both terms, and on `even`, which is the trailing
pointer of the two.

`even` is the trailing pointer — `odd` moves first inside the body — so `even` is
the one that can be sitting on the last node when the body starts. `even` guards
the `even.next` read; `even.next` guards the `odd.next` read that follows it.

Write `while odd and odd.next` instead and both failure modes appear: `[1, 2, 3,
4]` comes back as `1 → 3 → 4 → 2`, silently wrong, and `[1, 2, 3, 4, 5, 6]`
raises `AttributeError` when the body assigns through an `odd` that has just
become `None`. One of those you would catch in the sample; the other you would
not.

Two more things:

- **Guard `head is None or head.next is None` up front**, because `even_head =
  head.next` runs before the loop and a one-node list has no even chain at all.
- **`odd.next = even_head` after the loop.** When the loop exits, `odd` is on the
  last odd-positioned node and its `next` still points into the even chain (or is
  already correct by accident); the explicit join is what makes the result well
  formed for both parities. When the length is even, `even` ends as `None` and the
  even chain already terminates properly; when it is odd, the last even node's
  `next` was set to `None` on the final iteration.
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


def odd_even_list(head: ListNode | None) -> ListNode | None:
    if head is None or head.next is None:
        return head

    odd = head
    even = head.next
    even_head = even  # saved BEFORE the first rewrite destroys the reference

    while even and even.next:  # `even` trails, so `even` is the one to guard
        odd.next = even.next
        odd = odd.next
        even.next = odd.next
        even = even.next

    odd.next = even_head  # stitch the even chain on the end
    return head


CASES = [
    (([1, 2, 3, 4, 5],), [1, 3, 5, 2, 4]),
    (([2, 1, 3, 5, 6, 4, 7],), [2, 3, 6, 7, 1, 5, 4]),
    (([2, 4, 6, 8],), [2, 6, 4, 8]),  # positions, not values
    (([1, 2, 3, 4, 5, 6],), [1, 3, 5, 2, 4, 6]),
    (([1, 2, 3],), [1, 3, 2]),
    (([1, 2],), [1, 2]),
    (([1],), [1]),
    (([],), []),
]


def solve(values: list[int]) -> list[int]:
    return to_list(odd_even_list(from_list(values)))
