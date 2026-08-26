"""Map Sum Pairs — LeetCode 677."""

from __future__ import annotations

META = {
    "pattern": "tries",
    "symbol": "MapSum",
    "insight": "Push the delta (new value minus old) down the key's path so every node holds its subtree total, turning sum(prefix) into a walk.",
    "time": "O(L) per insert and per sum",
    "space": "O(total key characters)",
    "sections": [
        (
            "What it asks",
            """
Design a map with two operations:

- `insert(key, value)` — set the key's value, **overwriting** any previous one;
- `sum(prefix)` — the total of the values of all keys starting with `prefix`.

The single question that decides the design: *does `insert` on an existing key
overwrite or add?* It overwrites. Everything below exists to make overwrite
cheap without re-traversing a subtree, and an implementation that assumes
"insert is always new" passes the sample and fails the moment a key repeats.

Also worth asking: are `sum` calls hot relative to `insert`? Up to 50 calls in
the constraints, so nothing forces the aggressive version — but the aggressive
version is the answer they want.
""",
        ),
        (
            "The insight",
            """
Two designs are obviously available and both are lopsided:

- **Store values at word-ends.** `insert` is O(L); `sum` has to walk the whole
  subtree under the prefix, which is O(size of subtree).
- **Store a running total on every node.** `sum` becomes a plain O(L) walk down
  to the prefix node and a single read — but `insert` has to *know what it is
  replacing*.

Take the second, and pay for the overwrite with one extra hash map:
`self.values[key]` keeps the last value inserted for that key. Then

> `delta = value - self.values.get(key, 0)`

and adding `delta` to every node on the key's path keeps every node's total
exactly equal to the sum of the values below it. A fresh key has `delta =
value`; a re-insert of the same key with a smaller value pushes a **negative**
delta and the totals correct themselves without touching anything else.

`sum` is then: walk the prefix, return the node's total, or 0 if the walk falls
off. No subtree traversal, no accumulation.
""",
        ),
        (
            "The pitfall this problem exists for",
            """
`insert("apple", 3)` then `insert("apple", 2)` must leave `sum("ap") == 2`.
The version that writes `node.total += value` on every path node gives **5**,
and passes every test where keys are distinct. That is the whole question.

Related traps:

- **Keeping the old value on the terminal node instead of in a side map.** It
  works, but the terminal node may not exist yet on a fresh insert, and you
  must read it *before* you start mutating the path — reading it after you have
  already added along the way gives the wrong delta.
- **`sum` on a prefix that is also a full key.** `sum("apple")` includes
  `"apple"` itself, not only its extensions. The node total covers both because
  the delta was applied to *every* node on the path, terminal included.
- **The empty prefix.** `sum("")` is the total of everything, read straight off
  the root — which is why the root must receive the delta too. A loop that
  starts at `root.children[key[0]]` silently makes `sum("")` return 0.
- **Deletion**, the natural follow-up, is `insert(key, 0)` plus dropping the
  side-map entry — no new code, which is a good sign the invariant is right.
""",
        ),
    ],
}


class TrieNode:
    __slots__ = ("children", "total")

    def __init__(self) -> None:
        self.children: dict[str, TrieNode] = {}
        self.total = 0  # sum of the values of every key below (and at) this node


class MapSum:
    def __init__(self) -> None:
        self.root = TrieNode()
        self.values: dict[str, int] = {}  # last value per key, for the delta

    def insert(self, key: str, value: int) -> None:
        delta = value - self.values.get(key, 0)  # read before mutating
        self.values[key] = value

        node = self.root
        node.total += delta  # the root too, so sum("") works
        for character in key:
            node = node.children.setdefault(character, TrieNode())
            node.total += delta

    def sum(self, prefix: str) -> int:
        node = self.root
        for character in prefix:
            child = node.children.get(character)
            if child is None:
                return 0
            node = child
        return node.total


CASES: list[tuple[tuple, object]] = []


def check() -> None:
    mapping = MapSum()
    mapping.insert("apple", 3)
    assert mapping.sum("ap") == 3
    mapping.insert("app", 2)
    assert mapping.sum("ap") == 5
    assert mapping.sum("app") == 5  # "app" itself plus "apple"
    assert mapping.sum("apple") == 3

    # The overwrite. The "+= value" version returns 7 here.
    mapping.insert("apple", 5)
    assert mapping.sum("ap") == 7
    assert mapping.sum("apple") == 5

    # Overwriting downwards pushes a negative delta.
    mapping.insert("apple", 1)
    assert mapping.sum("ap") == 3
    assert mapping.sum("a") == 3
    assert mapping.sum("") == 3  # everything, read off the root

    # A prefix nobody has.
    assert mapping.sum("b") == 0
    assert mapping.sum("applesauce") == 0

    # Negative and zero values are legal arithmetic even if the constraints
    # keep them out; the invariant must not assume positivity.
    signed = MapSum()
    signed.insert("ab", 10)
    signed.insert("ac", -4)
    assert signed.sum("a") == 6
    assert signed.sum("ac") == -4
    signed.insert("ab", 0)
    assert signed.sum("a") == -4

    # Deletion as insert(key, 0).
    signed.insert("ac", 0)
    assert signed.sum("") == 0
    assert signed.sum("a") == 0

    # Fresh instance: empty everything.
    empty = MapSum()
    assert empty.sum("") == 0
    assert empty.sum("anything") == 0

    # A key that is a strict prefix of another, inserted in the other order.
    ordered = MapSum()
    ordered.insert("abcd", 4)
    ordered.insert("ab", 2)
    assert ordered.sum("ab") == 6
    assert ordered.sum("abc") == 4
    assert ordered.sum("abcd") == 4
    assert ordered.sum("abcde") == 0
