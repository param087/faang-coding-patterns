"""Reorder List — LeetCode 143."""

from __future__ import annotations

from dataclasses import dataclass

META = {
    "pattern": "linked-lists",
    "symbol": "reorder_list",
    "insight": "The interleaving is the first half zipped with the reversed second half — three routines you already own, run in sequence.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Turn `L0 → L1 → … → Ln-1` into `L0 → Ln-1 → L1 → Ln-2 → …`, in place, without
changing any node's value. Nothing is returned — the caller keeps the head, so
the head node must stay the head.

Two clarifiers worth thirty seconds. **Rewire or rewrite?** The statement says
values may not be changed, which rules out reading everything into an array and
writing it back; the interviewer wants pointer surgery. **Is O(1) space
required?** If not, the node-array version below is a complete answer and takes
two minutes.
""",
        ),
        (
            "The reflex answer, and its number",
            """
The shape of the output invites a loop that walks to the tail, unlinks it,
splices it after the current node, and repeats. Correct — and each of the `n/2`
splices walks half the list on average, so it is `n²/4` pointer hops. At the
stated `n = 5 × 10⁴` that is **6.25 × 10⁸** operations for a problem whose real
answer touches each node about three times.

The other reflex is honest and worth naming: push every node into an array, then
zip inwards from both ends with two indices. O(n) time, **O(n) space**, and only
the space bound separates it from the intended solution. Offer it as the fallback
while you write the real one — it also happens to be much easier to get right
under a ticking clock.
""",
        ),
        (
            "The insight",
            """
Look at the output as two sequences interleaved rather than as one sequence
permuted:

```
first half   1 → 2 → 3
second half  6 → 5 → 4        (i.e. the tail, reversed)
result       1 → 6 → 2 → 5 → 3 → 4
```

Nothing is being sorted or searched. The answer is *the first half zipped with
the reversed second half*, so the whole problem decomposes into three routines
you already own:

1. Find the middle (slow/fast).
2. Reverse the second half (three-pointer loop).
3. Weave the two chains, alternating.

Each is O(n) and each is O(1) space. Say the decomposition out loud before you
write anything — that sentence is what is actually being graded here, and it also
gives you three small correct pieces instead of one large uncertain one.
""",
        ),
        (
            "Sever the halves, or the weave builds a cycle",
            """
This is the detail the problem turns on, and it bites almost everyone once.

After the reversal, the last node of the first half still points at whatever it
pointed at before — which is now a node **inside** the reversed chain. Weave
without cutting and the final splice closes a loop. On `1 → 2`: the weave sets
`2.next = 2`, and `to_list` never returns. The failure presents as a hang, not as
a mismatch, so a test suite of expected values tells you nothing about where it
is. `slow.next = None` immediately after the reversal is the whole fix.

The second half of the detail is *where* you cut. `while fast.next and
fast.next.next` leaves `slow` on the **last node of the first half**, giving
`⌈n/2⌉` nodes to the first chain and `⌊n/2⌋` to the second. The invariant the
weave needs is only that the first chain is **never shorter** than the second —
if it were, the loop would dereference a `None` `first`. For an odd length that
extra node is the middle element, and it correctly falls at the end.

Drive the weave on `second`, the chain that can only be shorter or equal, and
save both `next` pointers before either assignment — the same discipline as plain
reversal: overwrite a link only after you have stored what it pointed to.
""",
        ),
        (
            "Dry run, odd length",
            """
`1 → 2 → 3 → 4 → 5`.

- **Middle.** `slow` stops at `3` (the last node of the first half, since `⌈5/2⌉
  = 3`). `fast` is at `5`.
- **Reverse and sever.** `reverse(4 → 5)` gives `5 → 4`; `slow.next = None` leaves
  the first chain as `1 → 2 → 3`.
- **Weave.** `1.next = 5`, `5.next = 2`; then `2.next = 4`, `4.next = 3`.
  `second` is exhausted, the loop ends.
- Result: `1 → 5 → 2 → 4 → 3`. ✓ and `3.next` is `None`, because the odd middle
  was never rewired.

Then run `1 → 2` in your head **with the `slow.next = None` line deleted**: the
first chain is still `1 → 2`, so the weave saves `first_next = 2`, sets
`1.next = 2`, then `2.next = first_next` — a node pointing at itself. Twenty
seconds, and it is the only bug in this problem that a wrong-answer test cannot
show you.
""",
        ),
        (
            "Follow-ups",
            """
- **"Do it without reversing"** — a deque of nodes, popping alternately from both
  ends. O(n) space, but it is the version to reach for when the list is doubly
  linked, where you can zip from both ends with no reversal at all.
- **Sort List (148)** reuses steps 1 and 2 verbatim for its merge sort split;
  getting the `⌈n/2⌉` / `⌊n/2⌋` split right here is what stops that recursion
  from looping forever on a two-node list.
- **Reverse Nodes in k-Group (25)** is the same "reverse a sub-chain and stitch
  it back" muscle, with a look-ahead length check in front of it.
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


def reorder_list(head: ListNode | None) -> ListNode | None:
    """Reorder in place; the head is returned only so tests can read it back."""

    def reverse(node: ListNode | None) -> ListNode | None:
        previous: ListNode | None = None
        while node:
            following = node.next
            node.next = previous
            previous = node
            node = following
        return previous

    if head is None or head.next is None:
        return head

    # 1. slow ends on the LAST node of the first half: ceil(n/2) nodes there.
    slow, fast = head, head
    while fast.next and fast.next.next:
        slow = slow.next
        fast = fast.next.next

    # 2. Reverse the tail, then cut it loose — without this the weave cycles.
    second = reverse(slow.next)
    slow.next = None

    # 3. Weave. `second` is never longer, so it is the loop's driver.
    first = head
    while second:
        first_next, second_next = first.next, second.next
        first.next = second
        second.next = first_next
        first, second = first_next, second_next

    return head


CASES = [
    (([1, 2, 3, 4],), [1, 4, 2, 3]),
    (([1, 2, 3, 4, 5],), [1, 5, 2, 4, 3]),
    (([1, 2, 3],), [1, 3, 2]),
    (([1, 2],), [1, 2]),  # hangs forever if the halves are not severed
    (([1],), [1]),
    (([],), []),
    (([1, 2, 3, 4, 5, 6],), [1, 6, 2, 5, 3, 4]),
    (([2, 2, 2, 2],), [2, 2, 2, 2]),
]


def solve(values: list[int]) -> list[int]:
    return to_list(reorder_list(from_list(values)))
