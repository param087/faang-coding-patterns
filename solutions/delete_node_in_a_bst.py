"""Delete Node in a BST — LeetCode 450."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

META = {
    "pattern": "binary-search-trees",
    "symbol": "delete_node",
    "insight": "Deleting a two-child node is really deleting its in-order successor, which by construction has no left child.",
    "time": "O(h)",
    "space": "O(h) for the recursion",
    "sections": [
        (
            "What it asks",
            """
Remove the node holding `key` from a BST and return the new root. The result
must still be a BST; it need not be balanced, and any valid answer is accepted.

Ask two things before writing code: **what if the key is absent** (return the
tree unchanged — do not throw), and **must the tree stay balanced** (no; if it
did, you would be writing AVL rebalancing, not this).

The reason this is the hard one of the BST trio is that deletion is the only
operation that has to *repair* the tree rather than extend it.
""",
        ),
        (
            "The insight",
            """
Descend to the node exactly as in search, then split on how many children it
has:

- **No children** — return `None`; the parent's pointer becomes null.
- **One child** — return that child; it slots straight into the parent's
  pointer, and every value in it is already on the correct side of every
  ancestor.
- **Two children** — the hard case, and the whole point of the problem.

For two children, you cannot just promote one side; the other side would have
nowhere to hang. Instead take the **in-order successor**: the smallest value in
the right subtree, i.e. walk right once then left as far as possible. Copy its
value into the node being deleted, then recursively delete the successor from
the right subtree.

That recursive call is guaranteed easy: the successor is the leftmost node of
its subtree, so it has **no left child**, and therefore falls into the
zero-or-one-child case. The recursion cannot descend into another two-child
deletion.

Return the subtree root from every branch and have the caller reassign
`node.left = delete(node.left, key)`. That is what rewires the parent — Python
has no reference-to-a-pointer, so trying to mutate the parent's field from the
child's frame is how people end up with a tree that silently keeps the deleted
node.
""",
        ),
        (
            "The pitfall: successor vs predecessor",
            """
Either works. The in-order **predecessor** (largest in the left subtree) is the
mirror image and is equally correct — but pick one and be consistent, because
mixing them mid-implementation produces a tree that passes small tests and
fails on the first node that has two children two levels deep.

Two more traps:

- **Copy the value, then delete the successor node.** Deleting the successor
  first leaves you holding a value with nowhere to put it.
- **Delete the successor by value, not by "it was a leaf".** The successor may
  have a right child, which must be reattached to the successor's parent. The
  recursive call handles this for free; a hand-unlinked version usually does
  not, and that lost right subtree is the classic bug here.
- **Key absent** — the descent falls off the bottom, `None` comes back, and the
  parent reassigns its own child to itself. Unchanged tree, no special case.
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


def to_level_order(root: TreeNode | None) -> list[int | None]:
    if not root:
        return []
    out: list[int | None] = []
    queue: deque[TreeNode | None] = deque([root])
    while queue:
        node = queue.popleft()
        if node is None:
            out.append(None)
            continue
        out.append(node.val)
        queue.append(node.left)
        queue.append(node.right)
    while out and out[-1] is None:
        out.pop()
    return out


def delete_node(root: TreeNode | None, key: int) -> TreeNode | None:
    if not root:
        return None  # key absent: the parent reassigns its child to itself

    if key < root.val:
        root.left = delete_node(root.left, key)
    elif key > root.val:
        root.right = delete_node(root.right, key)
    else:
        # Zero or one child: promote whatever is there.
        if not root.left:
            return root.right
        if not root.right:
            return root.left
        # Two children: take the in-order successor, which has no left child.
        successor = root.right
        while successor.left:
            successor = successor.left
        root.val = successor.val
        root.right = delete_node(root.right, successor.val)

    return root


CASES = [
    (([5, 3, 6, 2, 4, None, 7], 3), [5, 4, 6, 2, None, None, 7]),  # two children
    (([5, 3, 6, 2, 4, None, 7], 5), [6, 3, 7, 2, 4]),  # two children at the root
    (([5, 3, 6, 2, None, None, 7], 3), [5, 2, 6, None, None, None, 7]),  # left child only
    (([5, 3, 6, 2, 4, None, 7], 0), [5, 3, 6, 2, 4, None, 7]),  # key absent
    (([5], 5), []),  # last node
    (([], 0), []),
    (([0, -3, 9, -10, None, 5], -10), [0, -3, 9, None, None, 5]),  # leaf, negatives
]


def solve(values: list[int | None], key: int) -> list[int | None]:
    return to_level_order(delete_node(from_level_order(values), key))
