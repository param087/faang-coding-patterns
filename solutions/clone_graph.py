"""Clone Graph — LeetCode 133."""

from __future__ import annotations

META = {
    "pattern": "graph-traversal",
    "insight": "The original-to-copy map is both the visited set and the answer, so cycles cost nothing extra.",
    "time": "O(V + E)",
    "space": "O(V) for the map, plus O(V) for the stack",
    "sections": [
        (
            "What it asks",
            """
Deep-copy a connected undirected graph given one node. Every node in the copy
must be a new object; no edge may point back into the original.

Ask: is the graph connected (yes on LeetCode — otherwise one traversal cannot
reach everything and you need the node list); can `node` be null (yes, return
null); are values unique (yes, which is why people are tempted to key the map
by value — key it by node identity anyway, it costs nothing and survives the
follow-up where values repeat).
""",
        ),
        (
            "The insight",
            """
The graph has cycles, and undirected edges are cycles of length two, so a
plain DFS that copies each neighbour recursively never terminates.

One `dict` fixes it: `original node -> its copy`. Membership in that dict is
the visited test, and the value is the copy you wire the edge to. So each node
is created once, each edge is walked once from each end, and cycles resolve
themselves — when you come back round to a node already in the map you attach
the existing copy instead of making a second one.

Nothing here needs recursion. An explicit stack is the same three lines and
does not fall over on a 100-node path — or on the 10,000-node one in the
follow-up.
""",
        ),
        (
            "Register the copy before you recurse",
            """
The bug that kills this in an interview is creating the copy *after* walking
the neighbours:

```python
copy = Node(node.val, [clone(n) for n in node.neighbours])   # never returns
clones[node] = copy
```

By the time you insert into the map you have already recursed back into
`node` through its neighbour, and the recursion never bottoms out. The copy
must exist in the map **before** any neighbour is touched — its neighbour list
gets filled in later.

Also: append `clones[current].neighbours` for every neighbour, not only for the
newly-created ones. The edge back to an already-copied node still has to be
recorded, and skipping it produces a graph that is missing exactly the edges
that close a cycle.
""",
        ),
    ],
}


class Node:
    """LeetCode's node, defined locally so the module has no external types."""

    def __init__(self, val: int = 0, neighbours: list[Node] | None = None) -> None:
        self.val = val
        self.neighbours: list[Node] = neighbours if neighbours is not None else []


def clone_graph(node: Node | None) -> Node | None:
    if node is None:
        return None

    clones: dict[Node, Node] = {node: Node(node.val)}
    stack = [node]

    while stack:
        current = stack.pop()
        for neighbour in current.neighbours:
            if neighbour not in clones:
                clones[neighbour] = Node(neighbour.val)  # registered before use
                stack.append(neighbour)
            # Record the edge even when the copy already existed.
            clones[current].neighbours.append(clones[neighbour])

    return clones[node]


def from_adjacency(adjacency: list[list[int]]) -> Node | None:
    """`adjacency[i]` lists the 1-indexed values adjacent to node `i + 1`."""
    if not adjacency:
        return None
    nodes = [Node(i + 1) for i in range(len(adjacency))]
    for i, neighbours in enumerate(adjacency):
        nodes[i].neighbours = [nodes[value - 1] for value in neighbours]
    return nodes[0]


def _reachable(node: Node) -> list[Node]:
    seen: dict[int, Node] = {}
    stack = [node]
    while stack:
        current = stack.pop()
        if current.val in seen:
            continue
        seen[current.val] = current
        stack.extend(current.neighbours)
    return [seen[value] for value in sorted(seen)]


def to_adjacency(node: Node | None) -> list[list[int]]:
    if node is None:
        return []
    return [sorted(n.val for n in found.neighbours) for found in _reachable(node)]


CASES = [
    (([[2, 4], [1, 3], [2, 4], [1, 3]],), [[2, 4], [1, 3], [2, 4], [1, 3]]),
    (([[2, 3], [1, 3], [1, 2]],), [[2, 3], [1, 3], [1, 2]]),  # triangle: cycles
    (([[2], [1, 3], [2, 4], [3]],), [[2], [1, 3], [2, 4], [3]]),
    (([[2], [1]],), [[2], [1]]),  # a single edge is already a 2-cycle
    (([[]],), [[]]),  # one node, no edges
    (([],), []),  # null input
]


def solve(adjacency: list[list[int]]) -> list[list[int]]:
    return to_adjacency(clone_graph(from_adjacency(adjacency)))


def check() -> None:
    for args, expected in CASES:
        assert solve(*args) == expected, args

    # The shape matching is not enough: assert it is genuinely a deep copy.
    original = from_adjacency([[2, 4], [1, 3], [2, 4], [1, 3]])
    assert original is not None
    copy = clone_graph(original)
    assert copy is not None and copy is not original

    originals = _reachable(original)
    copies = _reachable(copy)
    assert [n.val for n in originals] == [n.val for n in copies]
    assert not ({id(n) for n in originals} & {id(n) for n in copies})

    # Mutating the copy must not touch the original.
    copies[0].neighbours.clear()
    assert [n.val for n in originals[0].neighbours] == [2, 4]
