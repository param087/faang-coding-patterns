"""Design In-Memory File System — LeetCode 588."""

from __future__ import annotations

META = {
    "pattern": "design",
    "symbol": "FileSystem",
    "insight": "One node type with a children map and a content string, plus a single walk-the-path helper that every method delegates to.",
    "time": "O(path depth) per call, plus O(k log k) to sort a listing of k entries",
    "space": "O(total path segments + total content)",
    "sections": [
        (
            "What it asks",
            """
Premium, so in my own words: build a filesystem held entirely in memory,
addressed by absolute paths, with four operations.

- **List a path.** If it names a directory, return its immediate entry names in
  **lexicographic order**. If it names a file, return a single-element list
  holding that file's own name.
- **Make a directory**, creating every missing intermediate directory along the
  way — `mkdir -p`, not `mkdir`.
- **Append content to a file**, creating the file (and its parent directories)
  if it does not exist. Appending, never overwriting.
- **Read a file's content back.**

Worth clarifying: paths are always absolute and start with `/`; the root is
`"/"`; and you may assume calls are well-formed — no listing a path whose
parent is a file, no reading a directory. Say that you would return an error
rather than silently creating something if the assumption were dropped.
""",
        ),
        (
            "The insight",
            """
This looks like four problems and it is one: **every method is a walk down a
trie of path segments**, and they differ only in what happens when a segment is
missing and what you do at the end.

```
_parts("/a/b/c") -> ["a", "b", "c"]
_walk(parts, create=True)  -> the node, making nodes on the way
_walk(parts, create=False) -> the node, assuming it exists
```

Write that helper first and the four public methods are three lines each. The
`create` flag is the entire difference between "make a directory" and "list a
directory", and candidates who skip it end up with four near-identical loops
and a bug in one of them.

Use **one node type**, not a `File` class and a `Directory` class. A node has a
`children` dict and a `content` string; a boolean says which it is. Two classes
force `isinstance` checks at every level of the walk and buy nothing — the
inheritance instinct is exactly what to resist under a 35-minute clock.

Root is the node reached by the empty segment list, which falls out of
`_parts("/") == []` for free.
""",
        ),
        (
            "Edge cases",
            """
- **`"/".split("/")` is `["", ""]`.** Filter empty segments or the root becomes
  a child named `""` and nothing else works. This is the first bug everyone
  writes.
- **An empty file and an empty directory are indistinguishable** without a flag:
  both have no children and no content. Carry `is_file` explicitly rather than
  inferring it from `content != ""`.
- **Listing a file returns its own name**, not its contents and not `[]` —
  which is why the walk has to keep the last segment around.
- **Appending, not assigning.** A second write to the same path concatenates.
  In Python, repeated `+=` on `str` is O(total²) if a file is written a million
  times; a list of chunks joined on read is the fix worth naming.
- **Making a directory that already exists is a no-op**, and must not wipe its
  children — which the `setdefault`-style walk gives you automatically.
- **Sort the listing.** Insertion order is not lexicographic order, and this is
  the assertion the hidden tests check first.
""",
        ),
    ],
}


class FileSystem:
    class _Node:
        __slots__ = ("children", "chunks", "is_file")

        def __init__(self, is_file: bool = False) -> None:
            self.is_file = is_file
            self.children: dict[str, FileSystem._Node] = {}
            self.chunks: list[str] = []  # joined on read: avoids O(total^2) appends

    def __init__(self) -> None:
        self.root = self._Node()

    @staticmethod
    def _parts(path: str) -> list[str]:
        return [part for part in path.split("/") if part]  # "/" -> [], not ["", ""]

    def _walk(self, parts: list[str], *, create: bool = False) -> _Node:
        node = self.root
        for part in parts:
            child = node.children.get(part)
            if child is None:
                if not create:
                    raise KeyError(f"no such path segment: {part}")
                child = self._Node()
                node.children[part] = child
            node = child
        return node

    def ls(self, path: str) -> list[str]:
        parts = self._parts(path)
        node = self._walk(parts)
        if node.is_file:
            return [parts[-1]]  # a file lists as its own name
        return sorted(node.children)  # insertion order is not lexicographic

    def mkdir(self, path: str) -> None:
        self._walk(self._parts(path), create=True)  # mkdir -p; existing dirs untouched

    def addContentToFile(self, filePath: str, content: str) -> None:
        node = self._walk(self._parts(filePath), create=True)
        node.is_file = True
        node.chunks.append(content)  # append, never overwrite

    def readContentFromFile(self, filePath: str) -> str:
        return "".join(self._walk(self._parts(filePath)).chunks)


def check() -> None:
    fs = FileSystem()
    assert fs.ls("/") == []  # empty root, and "/" must not split into [""]

    fs.mkdir("/a/b/c")
    fs.addContentToFile("/a/b/c/d", "hello")
    assert fs.ls("/") == ["a"]
    assert fs.readContentFromFile("/a/b/c/d") == "hello"

    # Listing a file returns its own name, not its content.
    assert fs.ls("/a/b/c/d") == ["d"]
    assert fs.ls("/a/b/c") == ["d"]

    # Appending concatenates; it never replaces.
    fs.addContentToFile("/a/b/c/d", " world")
    assert fs.readContentFromFile("/a/b/c/d") == "hello world"

    # mkdir on an existing path must not wipe its children.
    fs.mkdir("/a/b")
    assert fs.ls("/a/b") == ["c"]
    assert fs.readContentFromFile("/a/b/c/d") == "hello world"

    # Listings are sorted, not in insertion order, and mix files with directories.
    sorted_fs = FileSystem()
    for name in ("zeta", "alpha", "Mid", "beta"):
        sorted_fs.mkdir(f"/{name}")
    sorted_fs.addContentToFile("/apple.txt", "x")
    assert sorted_fs.ls("/") == ["Mid", "alpha", "apple.txt", "beta", "zeta"]

    # Writing to a path whose directories do not exist creates them.
    deep = FileSystem()
    deep.addContentToFile("/x/y/z.txt", "abc")
    assert deep.ls("/x") == ["y"]
    assert deep.ls("/x/y") == ["z.txt"]
    assert deep.readContentFromFile("/x/y/z.txt") == "abc"

    # An empty directory and an empty file are distinct.
    flags = FileSystem()
    flags.mkdir("/dir")
    flags.addContentToFile("/file", "")
    assert flags.ls("/dir") == []
    assert flags.ls("/file") == ["file"]
    assert flags.readContentFromFile("/file") == ""
    assert flags.ls("/") == ["dir", "file"]
