"""Flatten Binary Tree to Linked List — LeetCode 114."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

META = {
    "pattern": "binary-trees",
    "symbol": "flatten",
    "insight": "A node's left subtree slots between it and its right subtree, and the splice point is that subtree's rightmost node.",
    "time": "O(n) — every edge is walked at most twice",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Rewire the tree in place into a right-leaning chain in **preorder**: every
`left` becomes `None`, every `right` points at the next preorder node.

Ask whether "in place" means the same node objects (it does — you may not
allocate a new tree), and confirm the target order is preorder rather than
inorder, because the recursion differs.

The follow-up is stated in the problem itself: **O(1) extra space**. Since it
is going to be asked anyway, write that version.
""",
        ),
        (
            "The insight",
            """
Look at what flattening one node means:

```
    1              1
   / \\              \\
  2   5    ->        2
 / \\   \\              \\
3   4   6              3
                        \\
                         4
                          \\
                           5
                            \\
                             6
```

The left subtree, flattened, is inserted **between the node and its right
subtree**. So there is exactly one non-obvious quantity: where does the old
right subtree reattach? At the **rightmost node of the flattened left subtree**
— the last node of the left subtree in preorder.

And you do not need it flattened first to find it: the rightmost node reachable
by `right` pointers from `node.left` is already that node, before or after
flattening. So the whole algorithm is a `while` loop with no recursion and no
stack:

```
if node.left:
    tail = rightmost of node.left
    tail.right = node.right
    node.right = node.left
    node.left  = None
node = node.right
```

The `rightmost` scan looks quadratic and is not: each edge is traversed at most
twice overall, once by the outer walk and once as part of one right spine, so
the total is O(n). This is Morris traversal wearing a different hat.
""",
        ),
        (
            "The order trap",
            """
The instinctive recursion is wrong:

```python
flatten(node.left)
flatten(node.right)
node.right = node.left     # node.right has just been overwritten
```

By the time you assign, the original right subtree is gone unless you saved it
in a local **first**. Every correct recursive version does one of three things:

1. saves `right = node.right` before touching anything;
2. runs in **reverse preorder** (right, left, node) with a `prev` pointer, so
   the tail is already built when you get to a node — six lines, O(h) stack;
3. does the splice above, O(1) space.

Two other ways this goes wrong:

- **Collecting preorder into a list and rewiring** works and is O(n) space. Say
  it as the baseline, then improve it; leading with it and stopping there is
  what turns this into a "medium, done adequately".
- **Forgetting `node.left = None`.** The judge compares structure, and a tree
  with stale left pointers is not a linked list even if the right chain is
  perfect.
""",
        ),
    ],
}


@dataclass
class TreeNode:
    val: int
    left: TreeNode | None = None
    right: TreeNode | None = None


def flatten(root: TreeNode | None) -> None:
    node = root
    while node is not None:
        if node.left is not None:
            tail = node.left
            while tail.right is not None:  # last node of the left subtree in preorder
                tail = tail.right
            tail.right = node.right  # splice the old right subtree on behind it
            node.right = node.left
            node.left = None
        node = node.right


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


CASES = [
    (([1, 2, 5, 3, 4, None, 6],), [1, 2, 3, 4, 5, 6]),
    (([],), []),
    (([0],), [0]),
    (([1, 2],), [1, 2]),  # left child only
    (([1, None, 2],), [1, 2]),  # already flat
    (([1, 2, None, 3, None, 4],), [1, 2, 3, 4]),  # left spine
    (([1, 2, 3, 4, 5, 6, 7],), [1, 2, 4, 5, 3, 6, 7]),
]


def solve(values: list[int | None]) -> list[int]:
    root = from_level_order(values)  # fresh tree each call: flatten() mutates
    flatten(root)
    chain: list[int] = []
    node = root
    while node is not None:
        assert node.left is None, "flatten must clear every left pointer"
        chain.append(node.val)
        node = node.right
    return chain
