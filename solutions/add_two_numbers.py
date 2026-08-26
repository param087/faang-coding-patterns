"""Add Two Numbers — LeetCode 2."""

from __future__ import annotations

from dataclasses import dataclass

META = {
    "pattern": "linked-lists",
    "symbol": "add_two_numbers",
    "insight": "Loop while either list or the carry is still alive, and unequal lengths plus the final carry stop being special cases.",
    "time": "O(max(m, n))",
    "space": "O(max(m, n)) for the output, O(1) beyond it",
    "sections": [
        (
            "What it asks",
            """
Two non-negative integers stored as linked lists, **least significant digit
first**, one digit per node. Return their sum in the same form.

The reversed storage is a gift, not an obstacle: addition propagates carries from
the least significant end, so the lists are already in the order you want to walk
them. Confirm it — if the interviewer says *most* significant first, that is
LeetCode 445 and the answer changes to two stacks or two reversals.
""",
        ),
        (
            "The insight",
            """
The temptation is to read both lists into integers, add, and split the digits
back out. In Python it even works. Do not offer it: it is the one thing the
question is testing you *not* to do, it is O(n) big-integer arithmetic rather
than the O(n) digit loop, and in Java or C++ it overflows at ten digits against a
constraint of a hundred nodes.

Instead, run one loop with a single condition:

```python
while a or b or carry:
```

Those three terms cover everything. `a or b` handles lists of different lengths —
the exhausted one simply contributes nothing. `carry` handles the extra digit at
the top, which is the case people lose: `[9] + [1]` is `[0, 1]`, and a loop that
stops when both lists run out returns `[0]`.

`divmod(total, 10)` gives carry and digit together, and the carry is always 0 or
1 because the largest possible column is `9 + 9 + 1 = 19`.
""",
        ),
        (
            "The three ways this gets marked down",
            """
- **The trailing carry.** `[9, 9, 9] + [1]` must be `[0, 0, 0, 1]`. Any loop
  written as `while a and b` or `while a or b` gets this wrong, and the sample
  case does not catch it.
- **A leading zero on the result.** Build with a dummy head and return
  `dummy.next`; returning `dummy` prepends a `0`, which as a reversed number is a
  *trailing* zero and is silently accepted by a careless eyeball.
- **Mutating the inputs.** Writing the sum back into `a`'s nodes to save
  allocation is a real thing people reach for under time pressure. It destroys an
  argument the caller still owns, and if `a` and `b` alias the same list it
  produces nonsense.

`[0] + [0]` is worth one line of thought: the answer is `[0]`, not the empty
list. The `while a or b or carry` loop produces it correctly because both lists
still have one node.
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


def add_two_numbers(a: ListNode | None, b: ListNode | None) -> ListNode | None:
    dummy = ListNode(0)
    tail = dummy
    carry = 0

    while a or b or carry:  # `or carry` is what emits the final digit
        total = carry
        if a:
            total += a.val
            a = a.next
        if b:
            total += b.val
            b = b.next

        carry, digit = divmod(total, 10)  # carry is only ever 0 or 1
        tail.next = ListNode(digit)
        tail = tail.next

    return dummy.next


CASES = [
    (([2, 4, 3], [5, 6, 4]), [7, 0, 8]),  # 342 + 465 = 807
    (([0], [0]), [0]),
    (([9, 9, 9, 9, 9, 9, 9], [9, 9, 9, 9]), [8, 9, 9, 9, 0, 0, 0, 1]),
    (([9], [1]), [0, 1]),  # the carry that creates a new digit
    (([1], [9, 9, 9]), [0, 0, 0, 1]),  # carry rippling through a longer list
    (([5], [5]), [0, 1]),
    (([1, 8], [0, 0, 1]), [1, 8, 1]),  # 81 + 100 = 181
]


def solve(a: list[int], b: list[int]) -> list[int]:
    return to_list(add_two_numbers(from_list(a), from_list(b)))
