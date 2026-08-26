"""Rotate List — LeetCode 61."""

from __future__ import annotations

from dataclasses import dataclass

META = {
    "pattern": "linked-lists",
    "symbol": "rotate_right",
    "insight": "Close the list into a ring, then cut it n - k % n nodes along; rotation becomes one cut rather than k moves.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Rotate the list right by `k` places: the last `k` nodes move to the front,
keeping their order. `k` can be far larger than the list — the constraint is
`k ≤ 2·10⁹` while `n ≤ 500`.

That gap between `k` and `n` *is* the question. Anyone who writes "repeat the
move-last-to-front step `k` times" is doing 2·10⁹ pointer hops on a 500-node
list.
""",
        ),
        (
            "The insight",
            """
Rotation only has `n` distinct outcomes, so `k %= n` first. Everything after
that is one cut.

Walk to the tail, counting as you go — you need the length anyway for the
modulo, so the walk is not wasted. Then **join the tail to the head**, making
a ring. In a ring, "rotate right by k" and "start reading from a different
node" are the same statement.

The new head sits `n - k` nodes from the old head, so step to the node at
index `n - k - 1`, call that the new tail, take its `next` as the new head,
and sever. Two walks, no extra memory, and `k = 2·10⁹` costs exactly as much
as `k = 1`.
""",
        ),
        (
            "Edge cases",
            """
- **`k % n == 0`** — return `head` unchanged. If you close the ring and then
  cut at offset `n`, you land back on the original tail, which is correct but
  only by luck; returning early is clearer and avoids the walk.
- **Empty or single node** — return immediately. A one-node list closed into a
  ring points at itself, and every arithmetic slip becomes an infinite loop.
- **Forgetting to sever `new_tail.next`** leaves the ring intact. Nothing
  raises; the caller just loops forever the first time it walks the result.
- **`n - k - 1` steps, not `n - k`** — the walk stops on the node *before* the
  new head. Check it on `[1,2], k = 1`: `n - k - 1 = 0` steps, new tail `1`,
  new head `2`. ✓
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


def rotate_right(head: ListNode | None, k: int) -> ListNode | None:
    if head is None or head.next is None:
        return head

    length = 1
    tail = head
    while tail.next:
        tail = tail.next
        length += 1

    k %= length  # k can be 2e9; n is at most 500
    if k == 0:
        return head

    tail.next = head  # close the ring

    new_tail = head
    for _ in range(length - k - 1):
        new_tail = new_tail.next
    new_head = new_tail.next
    new_tail.next = None  # sever, or the caller walks forever

    return new_head


CASES = [
    (([1, 2, 3, 4, 5], 2), [4, 5, 1, 2, 3]),
    (([0, 1, 2], 4), [2, 0, 1]),
    (([1, 2, 3], 1_000_000_000), [3, 1, 2]),
    (([1, 2, 3, 4], 6), [3, 4, 1, 2]),
    (([1, 2, 3], 3), [1, 2, 3]),
    (([1, 2], 1), [2, 1]),
    (([7], 99), [7]),
    (([], 5), []),
]


def solve(values: list[int], k: int) -> list[int]:
    return to_list(rotate_right(from_list(values), k))
