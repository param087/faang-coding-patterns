"""Copy List with Random Pointer — LeetCode 138."""

from __future__ import annotations

META = {
    "pattern": "linked-lists",
    "symbol": "copy_random_list",
    "insight": "A random pointer can target a node you have not created yet, so create every node in pass one and wire them in pass two.",
    "time": "O(n)",
    "space": "O(n) for the map, O(1) for the weave",
    "sections": [
        (
            "What it asks",
            """
Deep-copy a singly linked list whose nodes carry an extra `random` pointer to
any node in the list, or to `None`. The copy must share **no nodes** with the
original, and its `random` pointers must target the copies, not the originals.

Ask whether the original may be mutated. If the answer is "yes, as long as you
restore it", the O(1)-space weave below is on the table; if it must stay
untouched throughout — a concurrent reader, say — you are stuck with the map.
""",
        ),
        (
            "The insight",
            """
The obstacle is ordering: `node.random` may point **forward**, at a node that
does not exist in the copy yet. Any single-pass attempt has to invent a
placeholder and patch it later, which is just a worse hash map.

So split the work:

1. **Pass one** — walk the list and create one bare clone per node. Record
   `original → clone` in a dict.
2. **Pass two** — walk again and set `clone.next = map[node.next]` and
   `clone.random = map[node.random]`, guarding `None`.

Key the dict by the node object itself. Nodes hash by identity, which is
exactly right — two different nodes holding the same value must map to two
different clones, so a value-keyed dict is silently wrong on any list with
duplicates.
""",
        ),
        (
            "The O(1)-space weave",
            """
The follow-up is "now without the map". Interleave the copies into the
original list:

1. `A → A' → B → B' → C → C'`, by splicing each clone directly after its
   original.
2. Now every clone is one hop from its original, so
   `clone.random = node.random.next` — no lookup table at all. This is the
   step the whole trick exists for.
3. Unzip the two lists, restoring `node.next` on the originals.

Three passes, O(1) extra space. The pitfall is step 3: if you only rebuild the
copy's `next` chain and forget to restore the original's, you hand back a
mangled input — and that is precisely the assertion the grader runs.
""",
        ),
    ],
}


class Node:
    """A list node with an extra pointer to an arbitrary node, or None."""

    __slots__ = ("next", "random", "val")

    def __init__(self, val: int, nxt: Node | None = None, random: Node | None = None) -> None:
        self.val = val
        self.next = nxt
        self.random = random


def copy_random_list(head: Node | None) -> Node | None:
    if head is None:
        return None

    # Pass one: every clone exists before any pointer is wired.
    clones: dict[Node, Node] = {}
    node: Node | None = head
    while node:
        clones[node] = Node(node.val)
        node = node.next

    # Pass two: forward-pointing randoms now resolve.
    node = head
    while node:
        clone = clones[node]
        clone.next = clones[node.next] if node.next else None
        clone.random = clones[node.random] if node.random else None
        node = node.next

    return clones[head]


def build(spec: list[list[int | None]]) -> Node | None:
    """[[val, random_index_or_None], ...] -> a list with random pointers."""
    nodes = [Node(int(val)) for val, _ in spec]
    for i, node in enumerate(nodes):
        node.next = nodes[i + 1] if i + 1 < len(nodes) else None
        target = spec[i][1]
        node.random = nodes[target] if target is not None else None
    return nodes[0] if nodes else None


def encode(head: Node | None) -> list[list[int | None]]:
    """Inverse of build(), so a correct copy round-trips to its own spec."""
    nodes: list[Node] = []
    node = head
    while node:
        nodes.append(node)
        node = node.next
    position = {n: i for i, n in enumerate(nodes)}
    return [[n.val, position[n.random] if n.random else None] for n in nodes]


CLASSIC = [[7, None], [13, 0], [11, 4], [10, 2], [1, 0]]

CASES = [
    ((CLASSIC,), CLASSIC),
    (([[1, 1], [2, 1]],), [[1, 1], [2, 1]]),
    (([[3, None], [3, 0], [3, 2]],), [[3, None], [3, 0], [3, 2]]),
    (([[1, 0]],), [[1, 0]]),
    (([[1, None]],), [[1, None]]),
    (([[4, 2], [5, 1], [6, 0]],), [[4, 2], [5, 1], [6, 0]]),
    (([],), []),
]


def solve(spec: list[list[int | None]]) -> list[list[int | None]]:
    head = build(spec)
    copied = copy_random_list(head)

    # Poison the originals: a "copy" that shares any node now shows -1.
    node = head
    while node:
        node.val = -1
        node = node.next

    return encode(copied)
