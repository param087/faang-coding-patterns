"""Flatten a Multilevel Doubly Linked List — LeetCode 430."""

from __future__ import annotations

META = {
    "pattern": "linked-lists",
    "symbol": "flatten",
    "insight": "A child list is spliced in front of the parent's successor, so park that successor on a stack until the branch runs out.",
    "time": "O(n)",
    "space": "O(d) for the stack, d = nesting depth",
    "sections": [
        (
            "What it asks",
            """
A doubly linked list where some nodes also have a `child` pointer to another
such list, arbitrarily deep. Flatten it into a single level: wherever a node
has a child, the whole child list is spliced in **between** that node and its
`next`, recursively. All `child` pointers end up `None`.

Ask what "flattened" means for the reverse direction. It means the result must
be a valid doubly linked list — every `prev` correct — which is half the marks
and the half people forget.
""",
        ),
        (
            "The insight",
            """
This is a pre-order DFS, and the traversal order — node, then its child
branch, then its successor — is precisely what the flattened list is.

Walk forward with a single pointer:

- **Node has a child?** Push `node.next` (if any) onto a stack, then wire
  `node.next = node.child`, set the child's `prev` back to `node`, and clear
  `node.child`.
- **Ran out of `next` with a non-empty stack?** Pop and attach; that is
  returning from a recursive call.
- Otherwise just step forward.

The stack holds the successors you deferred, one per level you descended, so
it is O(d) rather than O(n). Recursion works too, but it must return the
branch's **tail**, not its head — the caller has to attach the deferred
successor to something, and re-walking to find that tail turns the solution
quadratic on a list nested n deep.
""",
        ),
        (
            "The two pointers the grader checks",
            """
**`child` must be set to `None`.** Splicing the branch in without clearing
`child` leaves a list that reads correctly forward and still fails, because
the judge walks every node asserting `child is None`. It also leaves a second
path to the same nodes — a graph, not a list.

**`prev` must be repaired at both seams.** Two places, and the second is the
one that gets missed:

- entering a branch: `child.prev = node`;
- leaving one: `popped.prev = tail_of_branch`.

Miss the second and the forward walk is perfect while the backward walk skips
the entire branch. Test it by walking to the tail and coming back via `prev`,
which is what `solve` here returns as its second element — a forward-only
check passes buggy code.
""",
        ),
    ],
}


class Node:
    """Doubly linked, plus an optional child list hanging off any node."""

    __slots__ = ("child", "next", "prev", "val")

    def __init__(self, val: int) -> None:
        self.val = val
        self.prev: Node | None = None
        self.next: Node | None = None
        self.child: Node | None = None


def flatten(head: Node | None) -> Node | None:
    stack: list[Node] = []
    node = head

    while node:
        if node.child:
            if node.next:
                stack.append(node.next)  # deferred successor
            node.next = node.child
            node.child.prev = node
            node.child = None  # the judge asserts this
        elif node.next is None and stack:
            resumed = stack.pop()
            node.next = resumed
            resumed.prev = node  # the seam people forget
        node = node.next

    return head


def build(items: list) -> Node | None:
    """Nested list -> multilevel list; a sub-list is the previous node's child.

    [1, [2, 3], 4] is 1 -> 4 at the top level, with 1.child = 2 -> 3.
    """
    head: Node | None = None
    tail: Node | None = None
    for item in items:
        if isinstance(item, list):
            if tail is None:
                raise ValueError("a child list needs a preceding node")
            tail.child = build(item)
            continue
        node = Node(item)
        if tail is None:
            head = node
        else:
            tail.next = node
            node.prev = tail
        tail = node
    return head


def walk(head: Node | None) -> tuple[list[int], list[int]]:
    """Values going forward via `next`, then coming back via `prev`."""
    forward: list[int] = []
    node, tail = head, None
    while node:
        forward.append(node.val)
        tail, node = node, node.next

    backward: list[int] = []
    node = tail
    while node:
        backward.append(node.val)
        node = node.prev
    return forward, backward


CASES = [
    (([1, 2, 3, [7, 8, [11, 12], 9, 10], 4, 5, 6],),
     ([1, 2, 3, 7, 8, 11, 12, 9, 10, 4, 5, 6], [6, 5, 4, 10, 9, 12, 11, 8, 7, 3, 2, 1])),
    (([1, [2, 3], 4, [5], 6],), ([1, 2, 3, 4, 5, 6], [6, 5, 4, 3, 2, 1])),
    (([1, [2, [3, [4]]]],), ([1, 2, 3, 4], [4, 3, 2, 1])),
    (([1, [2], 3],), ([1, 2, 3], [3, 2, 1])),
    (([1, [2]],), ([1, 2], [2, 1])),
    (([1, 2],), ([1, 2], [2, 1])),
    (([1],), ([1], [1])),
    (([],), ([], [])),
]


def solve(items: list) -> tuple[list[int], list[int]]:
    return walk(flatten(build(items)))


def check() -> None:
    for args, expected in CASES:
        assert solve(*args) == expected, f"case {args!r}"

    # Every child pointer must be cleared, not merely bypassed.
    head = flatten(build([1, 2, 3, [7, 8, [11, 12], 9, 10], 4, 5, 6]))
    node = head
    while node:
        assert node.child is None, f"node {node.val} kept its child pointer"
        if node.next:
            assert node.next.prev is node, f"broken prev at {node.next.val}"
        node = node.next
