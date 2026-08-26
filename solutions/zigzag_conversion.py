"""Zigzag Conversion — LeetCode 6."""

from __future__ import annotations

META = {
    "pattern": "string-manipulation",
    "insight": "You never need the geometry: walk the string once and bounce a row pointer between 0 and numRows - 1.",
    "time": "O(n)",
    "space": "O(n) for the row buffers",
    "sections": [
        (
            "What it asks",
            """
Write the string down a zigzag of `numRows` rows — down the column, then
diagonally back up — and read it off row by row.

The picture is the whole difficulty. `"PAYPALISHIRING"` with 3 rows:

```
P   A   H   N
A P L S I I G
Y   I   R
```

read row-wise gives `"PAHNAPLSIIGYIR"`. Nothing is inserted or padded; the
blanks in that diagram are not characters.
""",
        ),
        (
            "The insight",
            """
The trap is that the diagram invites you to build a `numRows × n` character
grid and fill in the diagonals. That is O(numRows · n) memory, a pile of index
arithmetic for the diagonal legs, and a filtering pass to strip the blanks. At
`numRows = 1000` and `n = 1000` that is a million cells to hold 1000 characters.

You do not need the columns at all. **Only the row of each character matters**,
and the rows follow a trivial pattern: 0, 1, 2, …, numRows-1, numRows-2, …, 1,
0, 1, … So keep one `row` index and one `step` that is `+1` on the top row and
`-1` on the bottom row, append each character to its row's buffer, and join.

One pass, no grid, and the diagonal is never modelled explicitly — it is just
the descent running backwards.
""",
        ),
        (
            "The numRows == 1 trap",
            """
With `numRows == 1` the top row and the bottom row are the same row. The
`if row == 0` branch fires first, `step` stays `+1`, and the very next
character indexes `rows[1]` — **IndexError**. Guard it explicitly; this is the
single most common failure on this problem and it is not in the sample input.

`numRows >= len(s)` needs no guard: every row gets at most one character and
joining them reproduces the input, which is already correct.

Two follow-ups the interviewer may reach for:

- **O(1) extra space**, writing straight into the output. The zigzag has period
  `cycle = 2 · numRows - 2`; row `r` contains the characters at indices
  `j + r` and `j + cycle - r` for each `j` stepping by `cycle`, skipping the
  second when `r` is the first or last row. Faster, and much easier to get
  wrong — reach for it only if asked.
- **Decoding** a zigzag string back to the original: same row-length
  arithmetic, run the other way.
""",
        ),
    ],
}


def convert(s: str, num_rows: int) -> str:
    if num_rows == 1:
        return s  # top row and bottom row coincide; step would never flip

    rows: list[list[str]] = [[] for _ in range(num_rows)]
    row, step = 0, 1

    for char in s:
        rows[row].append(char)
        if row == 0:
            step = 1
        elif row == num_rows - 1:
            step = -1
        row += step

    return "".join("".join(chars) for chars in rows)


CASES = [
    (("PAYPALISHIRING", 3), "PAHNAPLSIIGYIR"),
    (("PAYPALISHIRING", 4), "PINALSIGYAHRPI"),
    (("ABCDE", 2), "ACEBD"),
    (("A", 1), "A"),
    (("AB", 1), "AB"),
    (("ABC", 5), "ABC"),
    (("", 3), ""),
    (("ABCD", 4), "ABCD"),
]


def solve(s: str, num_rows: int) -> str:
    return convert(s, num_rows)
