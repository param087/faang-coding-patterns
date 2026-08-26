"""Serialize and Deserialize Binary Tree — LeetCode 297."""

from __future__ import annotations

from collections import deque
from collections.abc import Iterator
from dataclasses import dataclass

META = {
    "pattern": "binary-trees",
    "symbol": "Codec",
    "insight": "Preorder with explicit null markers is self-delimiting: the recursion that writes the string is the one that reads it back.",
    "time": "O(n) both ways",
    "space": "O(n) for the string, O(h) recursion",
    "sections": [
        (
            "What it asks",
            """
Turn a binary tree into a string and turn that string back into the same tree.
The format is **yours to choose** — the only contract is that the round trip
preserves the structure.

Ask two things before writing anything:

- **What is in the values?** Negatives and multi-digit numbers on LeetCode, so
  one character per node is off the table and you need a real delimiter.
- **Is the string going over a wire?** If size matters you are into bit-packing
  and level-order-with-run-lengths; if not, comma-separated preorder is the
  answer they want.
""",
        ),
        (
            "The insight",
            """
Preorder alone does **not** determine a tree — `[1,2]` could be 2 as a left
child or a right child. Inorder alone does not either. The usual fix is to pair
two traversals, and that is the wrong instinct here.

Write the nulls down.

> A preorder stream **with explicit null markers** is self-delimiting: each
> token is either a leaf-of-the-recursion (`#`) or a node that consumes exactly
> two subtrees after it.

That makes deserialisation a single left-to-right cursor over the tokens with
no index arithmetic at all — `read()` takes one token and, if it is a value,
recursively reads its left subtree and then its right. The reader mirrors the
writer line for line, which is why this is the version to write under time
pressure: there is nothing to get subtly wrong.

Use an **iterator** over the tokens rather than an index. `next(tokens)`
advances shared state for free; an index needs `nonlocal` or a boxed counter.
""",
        ),
        (
            "The pitfalls",
            """
- **Truthiness on the node, not `is None`.** A node holding `0` is falsy in the
  helper only if you test `if not node.val`; test the node itself, or better,
  `if node is None`.
- **`"".split(",")` is `[""]`, not `[]`.** Serialising the empty tree must emit
  a real marker (`"#"`) so the reader has something to consume.
- **Delimiterless formats.** `str(node.val)` concatenated without a separator
  cannot distinguish `1,2` from `12`, and a `-` sign makes it worse.
- **BST version (LeetCode 449) is different on purpose.** There the ordering
  constraint lets you drop the nulls entirely and rebuild from preorder with a
  value range — a strictly smaller string. If the interviewer says "BST", that
  is the answer they are fishing for.
""",
        ),
    ],
}


@dataclass
class TreeNode:
    val: int
    left: TreeNode | None = None
    right: TreeNode | None = None


class Codec:
    NULL = "#"

    def serialize(self, root: TreeNode | None) -> str:
        parts: list[str] = []

        def write(node: TreeNode | None) -> None:
            if node is None:
                parts.append(self.NULL)  # the marker is what makes it decodable
                return
            parts.append(str(node.val))
            write(node.left)
            write(node.right)

        write(root)
        return ",".join(parts)

    def deserialize(self, data: str) -> TreeNode | None:
        tokens: Iterator[str] = iter(data.split(","))

        def read() -> TreeNode | None:
            token = next(tokens)
            if token == self.NULL:
                return None
            node = TreeNode(int(token))
            node.left = read()  # order matters: preorder wrote left first
            node.right = read()
            return node

        return read()


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
    if root is None:
        return []
    out: list[int | None] = []
    queue = deque([root])
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


CASES = [
    (([1, 2, 3, None, None, 4, 5],), [1, 2, 3, None, None, 4, 5]),
    (([],), []),
    (([0],), [0]),  # a falsy value: kills any `if not node.val` test
    (([-1, -2, -3, 1000, None, None, -1000],), [-1, -2, -3, 1000, None, None, -1000]),
    (([1, 2, None, 3, None, 4],), [1, 2, None, 3, None, 4]),  # left spine
    (([1, None, 2, None, 3],), [1, None, 2, None, 3]),  # right spine
    (([5, 5, 5, 5],), [5, 5, 5, 5]),  # duplicates
]


def solve(values: list[int | None]) -> list[int | None]:
    codec = Codec()
    return to_level_order(codec.deserialize(codec.serialize(from_level_order(values))))
