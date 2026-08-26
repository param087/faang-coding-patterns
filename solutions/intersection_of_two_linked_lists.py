"""Intersection of Two Linked Lists — LeetCode 160."""

from __future__ import annotations

from dataclasses import dataclass

META = {
    "pattern": "linked-lists",
    "symbol": "get_intersection_node",
    "insight": "Send each pointer down the other list when it runs out; both then walk exactly m + n steps and are forced to align at the junction.",
    "time": "O(m + n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Two singly linked lists may share a suffix. Return the first **shared node**, or
`None`. The lists have no cycles, and the original structure must be unchanged
when you return.

Intersection means *the same node object*, not a node with an equal value. Two
lists ending `… → 3` and `… → 3` with different `3` nodes do **not** intersect.
That is the trap the problem is built around, and it is why `is` appears in the
loop rather than `==`. Ask it explicitly if the statement is ambiguous — in a
real code base "equal" and "same" diverge constantly.

Note the shape the definition forces: once two singly linked lists share one
node, they share **everything after it**, because each node has exactly one
`next`. So the intersection is always a common suffix, never a crossing.
""",
        ),
        (
            "The insight",
            """
The obstacle is the length mismatch: aligned from the front, the two pointers are
at different distances from the junction, so they never meet. Two standard fixes
work and are worth naming before you write the clever one:

- **Hash set** of node identities from list A, then walk B. O(m + n) time, O(m)
  space, and impossible to get wrong.
- **Measure and align**: count both lengths, advance the longer head by the
  difference, then walk in step. O(1) space, two extra passes, and it is a
  perfectly good answer.

The two-pointer trick removes the counting. Let `a` be the length of A's unique
prefix, `b` B's unique prefix, and `c` the shared suffix. Walk pointer `p` down A
then A→B, and `q` down B then B→A. `p` reaches the junction after `a + b + c`
steps and so does `q` — `b + a + c`. The switch equalises the path lengths, so
they arrive at the same node at the same time without either of them knowing how
long anything was.
""",
        ),
        (
            "Why it terminates when there is no intersection",
            """
The loop looks unbounded, and the reason it is not is worth being able to state:
each pointer redirects **once**, on the step after it falls off the end. If the
lists do not intersect, `p` runs A then B and `q` runs B then A, so both hit
`None` on the same step — `m + n + 1` — and `p is q` becomes true with both
`None`. The function returns `None`, which is the right answer.

That only works if you redirect on the `None` itself rather than on the last
node:

```python
p = p.next if p else head_b     # correct
p = p.next.next if ... else ... # skips the shared None, loops forever
```

The version that jumps straight from the tail to the other head never lets both
pointers be `None` simultaneously when the lengths differ, and it spins until the
judge times out.

Two more details: use `is` / `is not` for the comparison, never `==`; and both
pointers starting at the two heads handles the case where the lists are
*identical* — `p is q` is true immediately and the head is returned.
""",
        ),
    ],
}


@dataclass
class ListNode:
    val: int
    next: ListNode | None = None


def to_list(head: ListNode | None) -> list[int]:
    out: list[int] = []
    while head:
        out.append(head.val)
        head = head.next
    return out


def with_prefix(values: list[int], tail: ListNode | None) -> ListNode | None:
    """Build `values` as fresh nodes in front of an existing (shared) tail."""
    head = tail
    for value in reversed(values):
        head = ListNode(value, head)
    return head


def get_intersection_node(a: ListNode | None, b: ListNode | None) -> ListNode | None:
    if a is None or b is None:
        return None

    p, q = a, b
    while p is not q:  # identity: equal values are not an intersection
        p = b if p is None else p.next  # redirect ON the None, not before it
        q = a if q is None else q.next

    return p  # the junction, or None when both fell off together


CASES = [
    (([4, 1], [5, 6, 1], [8, 4, 5]), [8, 4, 5]),
    (([1, 9, 1], [3], [2, 4]), [2, 4]),
    (([2, 6, 4], [1, 5], []), []),
    (([1, 2, 3], [9, 3], []), []),  # equal trailing values, no shared node
    (([], [], [7]), [7]),  # the same list twice
    (([1], [], [2, 3]), [2, 3]),  # B *is* the shared suffix
    (([1, 1, 1], [1, 1], [1]), [1]),
    (([5], [5], []), []),
    (([], [], []), []),
]


def solve(a_only: list[int], b_only: list[int], common: list[int]) -> list[int]:
    """`common` is the genuinely shared suffix; the answer is [] when there is none."""
    tail = with_prefix(common, None)
    a = with_prefix(a_only, tail)
    b = with_prefix(b_only, tail)
    return to_list(get_intersection_node(a, b))
