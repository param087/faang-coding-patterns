"""Design a Text Editor — LeetCode 2296."""

from __future__ import annotations

META = {
    "pattern": "ood",
    "symbol": "TextEditor",
    "insight": "Split the document at the cursor into two stacks facing each other — the cursor stops being an index and becomes the gap between them.",
    "time": "O(len(text)) to add, O(k) for a delete or a cursor move",
    "space": "O(total characters)",
    "sections": [
        (
            "What it asks",
            """
A text editor with a cursor:

- `addText(text)` — insert at the cursor, which ends up after the insertion;
- `deleteText(k)` — delete up to `k` characters to the **left** of the cursor
  and return how many were actually deleted;
- `cursorLeft(k)` / `cursorRight(k)` — move up to `k`, clamped at the ends.

All three cursor operations return **the last up to 10 characters left of the
cursor** — up to, not exactly.

Ask whether `k` is bounded. It is, at 40 here, which is what licenses an O(k)
move; unbounded `k` changes the answer entirely (see the last section). Also
ask whether text right of the cursor is ever deleted — it is not, which is why
one of the two structures is write-only during deletes.
""",
        ),
        (
            "The insight",
            """
Every operation is anchored at the cursor and touches only its immediate
neighbourhood. That is the definition of a **gap buffer**, and the two-stack
form of it is four lines of Python.

Hold the document as `left` (everything before the cursor, in order) and
`right` (everything after, **reversed**, so its top is the character just right
of the cursor). Then:

- `addText` — push onto `left`;
- `deleteText` — pop from `left`;
- `cursorLeft` — move `k` characters from `left` to `right`;
- `cursorRight` — move `k` characters from `right` to `left`;
- the return value — the last 10 of `left`.

There is no cursor variable. Its position *is* `len(left)`, so it cannot drift
out of sync with the text, and every insertion or deletion adjusts it for free.
That is the thing to say aloud: the bug class this design eliminates is the
stale index after an edit, and that bug class is most of the problem.

The naive alternative — one string plus an integer index — is correct and
quadratic. Strings are immutable, so each `addText` copies the whole document:
with 2·10⁴ calls over a document reaching 8·10⁵ characters that is up to
**1.6·10¹⁰ character copies**. A Python list of characters with `insert` at an
arbitrary index is the same O(n) shift wearing a mutable costume; only moving
the work to the *ends* fixes it.
""",
        ),
        (
            "Edge cases",
            """
- **`k` past the end.** `deleteText` returns `min(k, len(left))`, not `k` — the
  count actually removed. Cursor moves clamp silently and are still expected to
  return their context; deleting 10 from an empty left side returns `0`, not a
  crash.
- **Fewer than 10 characters left of the cursor.** `left[-10:]` already yields
  everything there is. Writing `left[len(left) - 10:]` instead is the bug: at
  length 4 that slices from index −6 and returns the wrong four characters.
- **Deleting deletes left, moving is symmetric.** `deleteText` never touches
  `right`, so text after the cursor survives every delete — which is exactly
  what makes the "delete then move right" sequence a good test.
- **The join cost.** `"".join(left[-10:])` is O(10), a constant. Returning
  `"".join(left)` and slicing afterwards would be O(n) per call and undo the
  whole design.
- **Unbounded `k`**, the real follow-up: O(k) moves become the bottleneck when a
  caller jumps 10⁶ characters repeatedly. Then you want a rope or a balanced BST
  keyed by subtree size, giving O(log n) seek-to-offset — and the interviewer is
  usually asking whether you know that exists, not asking you to write it.
""",
        ),
    ],
}


class TextEditor:
    """Two stacks facing each other; the cursor is the gap between them."""

    def __init__(self) -> None:
        self.left: list[str] = []  # before the cursor, in order
        self.right: list[str] = []  # after the cursor, reversed

    def addText(self, text: str) -> None:
        self.left.extend(text)

    def deleteText(self, k: int) -> int:
        removed = min(k, len(self.left))  # the count actually deleted
        del self.left[len(self.left) - removed :]
        return removed

    def cursorLeft(self, k: int) -> str:
        for _ in range(min(k, len(self.left))):
            self.right.append(self.left.pop())
        return self._context()

    def cursorRight(self, k: int) -> str:
        for _ in range(min(k, len(self.right))):
            self.left.append(self.right.pop())
        return self._context()

    def _context(self) -> str:
        return "".join(self.left[-10:])  # -10, not len-10: shorter text must survive


def check() -> None:
    editor = TextEditor()
    editor.addText("leetcode")
    assert editor.deleteText(4) == 4  # left is "leet"
    editor.addText("practice")  # left is "leetpractice"
    assert editor.cursorRight(3) == "etpractice"  # nothing to the right; last 10
    assert editor.cursorLeft(8) == "leet"  # fewer than 10 characters left
    assert editor.deleteText(10) == 4  # only 4 were there
    assert editor.cursorLeft(2) == ""  # already at the start
    assert editor.cursorRight(6) == "practi"  # the text after the cursor survived

    # The delete-left-only contract: text right of the cursor is untouched.
    split = TextEditor()
    split.addText("abcdef")
    assert split.cursorLeft(3) == "abc"
    assert split.deleteText(2) == 2  # removes "bc", leaves "def" to the right
    assert split.cursorRight(10) == "adef"

    # An empty editor: every operation is a no-op that still answers.
    empty = TextEditor()
    assert empty.deleteText(5) == 0
    assert empty.cursorLeft(5) == ""
    assert empty.cursorRight(5) == ""
    assert empty.deleteText(0) == 0

    # Exactly 10 and exactly 11 characters, the boundary of the context window.
    window = TextEditor()
    window.addText("0123456789")
    assert window.cursorLeft(0) == "0123456789"
    window.addText("A")
    assert window.cursorLeft(0) == "123456789A"
    assert window.cursorLeft(1) == "0123456789"  # the "A" moved right, 10 remain

    # Interleaved inserts around a moved cursor.
    weave = TextEditor()
    weave.addText("hello")
    assert weave.cursorLeft(2) == "hel"
    weave.addText("XY")
    assert weave.cursorRight(2) == "helXYlo"
    assert weave.deleteText(3) == 3
    assert weave.cursorLeft(9) == ""
    assert weave.cursorRight(20) == "helX"
