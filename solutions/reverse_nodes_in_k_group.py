"""Reverse Nodes in k-Group — LeetCode 25."""

from __future__ import annotations

from dataclasses import dataclass

META = {
    "pattern": "linked-lists",
    "symbol": "reverse_k_group",
    "insight": "Count k nodes ahead before reversing any of them; the look-ahead is the whole problem, the reversal is Reverse Linked List.",
    "time": "O(n) — every node is walked twice, once to count and once to reverse",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Reverse the list in consecutive blocks of `k`. A trailing block of fewer than
`k` nodes is left **as it is**, not reversed.

Two clarifiers worth spending ten seconds on:

- **May I swap values instead of relinking?** The problem explicitly says no,
  and the interviewer will say no. Ask anyway — it tells them you know the
  cheap way out exists and that you are not taking it.
- **What happens to the leftover tail?** Confirm it stays in original order.
  Half of all failed attempts here reverse the last partial group.
""",
        ),
        (
            "The two versions that fall over",
            """
**Copy values into an array**, reverse each slice of `k`, write them back.
O(n) time but O(n) extra memory, which dies the moment they ask the standard
follow-up: *"can you do it with O(1) extra space?"*

**Recurse per group** — reverse the first `k`, recurse on the rest. Elegant,
and the depth is `n / k`. With the stated bound n = 5000 and `k = 1` that is
**5000 stack frames**, past CPython's default limit of 1000: `RecursionError`
before you get an answer. Mention it, then write the iterative version.
""",
        ),
        (
            "The insight",
            """
Do not reverse and then repair. **Walk `k` nodes forward first.** If you run
off the end during that walk, the remaining block is short and you are done —
return without touching anything.

Once the walk succeeds you hold the three pointers that matter:

- `group_prev` — the node before the block, whose `next` must end up at the
  block's new head;
- `kth` — the block's last node, which becomes its new head;
- `group_next` — the first node after the block.

Then run the ordinary three-pointer reversal, but seed `previous` with
`group_next` instead of `None`. That single substitution stitches the reversed
block onto the rest of the list for free — no second pass to reattach the
tail.
""",
        ),
        (
            "The reconnection, in the only order that works",
            """
After the inner loop, `group_prev.next` is still pointing at the node that
*used* to be first and is now the block's **tail**. That stale pointer is a
gift, not a bug — it is the only handle on the tail you have left:

```python
tail = group_prev.next     # read it BEFORE you overwrite it
group_prev.next = kth      # block's new head
group_prev = tail          # tail is the boundary for the next block
```

Overwrite `group_prev.next` first and the tail is unreachable; you will be
re-walking `k` nodes to find it, and that is where the off-by-ones live.
""",
        ),
        (
            "Dry run",
            """
`1 → 2 → 3 → 4 → 5`, `k = 3`. Dummy `D` in front.

- Walk 3 from `D`: lands on `3`, so the block is real. `group_next = 4`.
- Reverse with `previous = 4`: `1.next = 4`, then `2.next = 1`,
  then `3.next = 2`. List fragment is `3 → 2 → 1 → 4`.
- `tail = D.next = 1`. Set `D.next = 3`. Move `group_prev = 1`.
- Next round: walk 3 from `1` → `4`, `5`, then `None`. **Short block, return.**

`D → 3 → 2 → 1 → 4 → 5`. The second walk is exactly the case that catches an
implementation which reverses first and checks afterwards.
""",
        ),
        (
            "Follow-ups",
            """
- **"Reverse the leftover group too."** Drop the early return: when the walk
  hits `None`, reverse whatever is left with `group_next = None`.
- **"Reverse every other group."** Add a parity flag and, on the skip rounds,
  advance `group_prev` by `k` without reversing.
- **Reverse Linked List II** (positions `m..n`) is this same body with the
  look-ahead replaced by a fixed walk to `m - 1`.
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


def reverse_k_group(head: ListNode | None, k: int) -> ListNode | None:
    if head is None or k <= 1:
        return head

    dummy = ListNode(0, head)
    group_prev = dummy

    while True:
        # Look ahead k nodes. Falling off the end means the block is short.
        kth: ListNode | None = group_prev
        for _ in range(k):
            kth = kth.next
            if kth is None:
                return dummy.next

        group_next = kth.next

        # Three-pointer reversal, seeded with group_next so the block
        # reattaches to the remainder without a second pass.
        previous, current = group_next, group_prev.next
        while current is not group_next:
            following = current.next
            current.next = previous
            previous = current
            current = following

        tail = group_prev.next  # read before overwriting: it is now the tail
        group_prev.next = kth
        group_prev = tail


CASES = [
    (([1, 2, 3, 4, 5], 2), [2, 1, 4, 3, 5]),
    (([1, 2, 3, 4, 5], 3), [3, 2, 1, 4, 5]),
    (([1, 2, 3, 4, 5, 6], 3), [3, 2, 1, 6, 5, 4]),
    (([1, 2, 3, 4], 2), [2, 1, 4, 3]),
    (([1, 2, 3], 5), [1, 2, 3]),
    (([1, 2, 3, 4, 5], 1), [1, 2, 3, 4, 5]),
    (([7], 1), [7]),
    (([], 3), []),
]


def solve(values: list[int], k: int) -> list[int]:
    return to_list(reverse_k_group(from_list(values), k))
