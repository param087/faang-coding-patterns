"""Binary Search Tree Iterator — LeetCode 173."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

META = {
    "pattern": "binary-search-trees",
    "symbol": "BSTIterator",
    "insight": "Keep only the left spine on a stack — that is the in-order traversal paused mid-flight, and it costs O(h) instead of O(n).",
    "time": "O(1) amortised per next(), O(h) for the constructor",
    "space": "O(h)",
    "sections": [
        (
            "What it asks",
            """
Wrap a BST in an iterator exposing `next()` (the next value in sorted order)
and `hasNext()`. The stated targets are **O(1) average** per call and **O(h)**
memory — and those two numbers are the entire problem. Without them, one line
in the constructor solves it.

Ask whether the tree is mutated while the iterator is live (LeetCode: no; in
real code that is the question that decides whether you can hold node
references at all), and whether `next()` may be called after exhaustion
(LeetCode guarantees not).
""",
        ),
        (
            "The obvious answer, and why the constraint forbids it",
            """
Flatten the tree in the constructor: full in-order traversal into a list, then
`next()` is `list[i]; i += 1`. Genuinely O(1) per call, trivially correct, and
worth saying out loud as the baseline.

It fails the **space** bound. With n up to 10⁵ you hold 10⁵ node values for the
lifetime of the iterator even if the caller takes two of them and walks away,
and you pay all 10⁵ visits before the first `next()` returns. The point of an
iterator is that you do not pay for what you do not consume.

O(h) is the interviewer telling you: pause the traversal, do not finish it.
""",
        ),
        (
            "The insight: an explicit stack is a paused recursion",
            """
Recursive in-order is three lines, but you cannot pause it — the call stack
belongs to the interpreter. Materialise that stack yourself and you can stop
between any two nodes.

The invariant is small and worth stating exactly: **the stack holds the nodes
whose left subtrees are fully done but which have not been emitted yet** — in
other words, the left spine of the subtree still to come. Its top is always the
next value in sorted order.

- Constructor: push the whole left spine from the root.
- `next()`: pop, then push the left spine of the popped node's **right** child.
- `hasNext()`: the stack is non-empty.

Depth of the stack is bounded by the height, hence O(h). On a balanced 10⁵-node
tree that is about 17 pointers instead of 10⁵ values.
""",
        ),
        (
            "Why next() is O(1) amortised, not O(h)",
            """
A single `next()` can be expensive: pop a node whose right child has a long
left spine, and that one call pushes h nodes. Interviewers will point at that
and ask how you can claim O(1).

The accounting: every node is pushed **exactly once** and popped **exactly
once** over the iterator's whole life. A complete traversal therefore does 2n
stack operations across n calls to `next()`, which is 2 operations per call
**amortised**. The expensive calls are paid for by the cheap ones that follow —
a node with a deep left spine below it is followed by a run of pops that push
nothing.

Say "amortised O(1), worst case O(h) for an individual call". Claiming worst
case O(1) is wrong and they will know.
""",
        ),
        (
            "Dry run",
            """
Tree `7(3, 15(9, 20))`, sorted order `3, 7, 9, 15, 20`.

- Constructor pushes the left spine from 7: `[7, 3]`.
- `next()` pops 3, right child is null, pushes nothing → **3**. Stack `[7]`.
- `next()` pops 7, pushes the left spine of 15: `[15, 9]` → **7**.
- `next()` pops 9 → **9**. Stack `[15]`.
- `next()` pops 15, pushes the left spine of 20: `[20]` → **15**.
- `next()` pops 20 → **20**. Stack empty, `hasNext()` is false.

Peak stack depth: 2, the height of the tree. Never 5.
""",
        ),
        (
            "Follow-ups",
            """
- **Add `prev()` and `hasPrev()`** (LeetCode 1586). The stack cannot go
  backwards, so the usual answer is to cache the values already emitted in a
  list and keep a cursor — space becomes O(k) in what you have consumed, which
  is still better than O(n) up front.
- **O(1) space** — Morris traversal, using threaded right pointers instead of a
  stack. It temporarily mutates the tree, which rules it out under concurrent
  reads; say that trade-off rather than just naming the technique.
- **Merge two BSTs in sorted order** (LeetCode 1305) — run two of these
  iterators and take the smaller head each time, exactly like merging two
  sorted lists. This is the reason the iterator interface is worth having.
- **`peek()`** — return `self.stack[-1].val` without popping; free with this
  design, awkward with the flattened one only if you forgot the index.
- **Mutation during iteration** — real iterators need a modification counter
  and a `ConcurrentModificationException` equivalent; the stack holds stale
  node references otherwise.
""",
        ),
    ],
}


@dataclass
class TreeNode:
    val: int
    left: TreeNode | None = None
    right: TreeNode | None = None


def from_level_order(values: list[int | None]) -> TreeNode | None:
    if not values or values[0] is None:
        return None
    root = TreeNode(values[0])
    queue = deque([root])
    i = 1
    while queue and i < len(values):
        node = queue.popleft()
        for side in ("left", "right"):
            if i >= len(values):
                break
            value = values[i]
            i += 1
            if value is not None:
                child = TreeNode(value)
                setattr(node, side, child)
                queue.append(child)
    return root


class BSTIterator:
    def __init__(self, root: TreeNode | None) -> None:
        self.stack: list[TreeNode] = []
        self._push_left_spine(root)

    def _push_left_spine(self, node: TreeNode | None) -> None:
        # Everything on this path has its left subtree pending, none emitted.
        while node:
            self.stack.append(node)
            node = node.left

    def has_next(self) -> bool:
        return bool(self.stack)

    def next(self) -> int:
        node = self.stack.pop()  # top of stack is always the next in order
        self._push_left_spine(node.right)
        return node.val


def _inorder(node: TreeNode | None) -> list[int]:
    if not node:
        return []
    return [*_inorder(node.left), node.val, *_inorder(node.right)]


def _drain(iterator: BSTIterator) -> list[int]:
    out: list[int] = []
    while iterator.has_next():
        out.append(iterator.next())
    return out


def _balanced(values: list[int], lo: int, hi: int) -> TreeNode | None:
    if lo > hi:
        return None
    mid = (lo + hi) // 2
    return TreeNode(
        values[mid],
        _balanced(values, lo, mid - 1),
        _balanced(values, mid + 1, hi),
    )


def check() -> None:
    # A full drain must reproduce the sorted in-order sequence.
    for values in (
        [7, 3, 15, None, None, 9, 20],
        [1],
        [],
        [2, 1, 3],
        [5, 3, None, 2, None, 1],  # left-leaning chain: worst case for the stack
        [0, -3, 9, -10, None, 5],  # negatives
    ):
        root = from_level_order(values)
        assert _drain(BSTIterator(root)) == sorted(_inorder(root))

    # The published operation sequence, interleaving the two calls.
    it = BSTIterator(from_level_order([7, 3, 15, None, None, 9, 20]))
    assert it.next() == 3
    assert it.next() == 7
    assert it.has_next() is True
    assert it.next() == 9
    assert it.has_next() is True
    assert it.next() == 15
    assert it.has_next() is True
    assert it.next() == 20
    assert it.has_next() is False

    # has_next() must be a pure query — repeating it consumes nothing.
    peeker = BSTIterator(from_level_order([2, 1, 3]))
    assert peeker.has_next() is True
    assert peeker.has_next() is True
    assert peeker.next() == 1

    # Empty tree: exhausted from the start.
    empty = BSTIterator(None)
    assert empty.has_next() is False
    raised = False
    try:
        empty.next()
    except IndexError:
        raised = True
    assert raised, "next() past the end must not silently return a value"

    # A right-leaning chain of 1000 nodes never holds more than one node.
    chain = TreeNode(1)
    tail = chain
    for value in range(2, 1001):
        tail.right = TreeNode(value)
        tail = tail.right
    walker = BSTIterator(chain)
    emitted: list[int] = []
    peak = 0
    while walker.has_next():
        peak = max(peak, len(walker.stack))
        emitted.append(walker.next())
    assert emitted == list(range(1, 1001))
    assert peak == 1

    # A perfect tree of 1023 nodes: O(h) means 10, not 1023.
    perfect = _balanced(list(range(1023)), 0, 1022)
    balanced_walker = BSTIterator(perfect)
    peak = 0
    emitted = []
    while balanced_walker.has_next():
        peak = max(peak, len(balanced_walker.stack))
        emitted.append(balanced_walker.next())
    assert emitted == list(range(1023))
    assert peak == 10
