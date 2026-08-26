"""Text Justification — LeetCode 68."""

from __future__ import annotations

META = {
    "pattern": "string-manipulation",
    "insight": "Pack greedily, then distribute spaces with one divmod — the leftmost gaps take the remainder, and only the last line is exempt.",
    "time": "O(total characters)",
    "space": "O(total characters) for the output",
    "sections": [
        (
            "What it asks",
            """
Break a list of words into lines of exactly `maxWidth` characters, packing as
many words per line as fit, padding with spaces so each line is fully
justified. Extra spaces go to the **leftmost** gaps. The last line, and any
line holding a single word, are left-justified and padded on the right.

Clarify before you write: is packing **greedy** (yes — you are not allowed to
optimise line breaks), can a word be longer than `maxWidth` (no), can `words`
be empty (LeetCode says no, but say what you would return), and is a trailing
line always padded to full width (yes, including a single-word last line).
""",
        ),
        (
            "Greedy is mandated — and that is a constraint, not a licence",
            """
The natural instinct of anyone who has met typesetting is Knuth–Plass: choose
line breaks to minimise the sum of squared trailing spaces. That is a clean
`O(n²)` DP — at n = 300 words it is 9 × 10⁴ states, trivially fast — and it
produces **different output**, so it fails every test.

Say this out loud and move on. The value is showing that you know the greedy
is a specification, not an optimisation you chose. It also pre-empts the
interviewer's follow-up, which is exactly that DP.

What makes this a Hard is not the algorithm. It is that there are **three**
line formats (fully justified, single word, last line), an off-by-one hiding in
the fit test, and an uneven space split. Every one of those is a place to lose
the problem on a whiteboard.
""",
        ),
        (
            "The fit test",
            """
A line of `k` words needs at least `k - 1` separating spaces, so before adding
a word ask:

```python
line_chars + len(line) + len(word) > max_width
```

`len(line)` — not `len(line) - 1` — is the trick: the `k - 1` existing minimum
gaps **plus** the one new gap the incoming word needs. Writing `len(line) - 1`
lets one word too many onto every line, and the failure only shows up on
inputs where a line happens to land exactly on the boundary — which is most of
them, since the packing is greedy.

`line_chars` is a running sum of word lengths. Recomputing `sum(map(len, line))`
per candidate word is `O(k)` inside an `O(n)` loop and buys nothing.
""",
        ),
        (
            "Distributing the spaces",
            """
For a justified line with `gaps = len(line) - 1`:

```python
width, extra = divmod(max_width - line_chars, gaps)
```

Every gap gets `width` spaces; the first `extra` gaps get one more. That single
`divmod` is the whole rule — no loop that adds one space at a time and
re-checks the total.

The leftward bias matters: `"a computer. Art is"` in width 20 has 5 spaces
across 3 gaps → `width = 1, extra = 2` → `a··computer.··Art·is`. Distributing
the remainder to the **right** gaps instead is the most common wrong answer,
and it is silent — the lines are still the correct width.
""",
        ),
        (
            "The two exempt lines",
            """
- **Single word on a line**: `gaps == 0`, so the `divmod` divides by zero.
  Handle it before you compute, and the format is left-justify + pad.
- **The last line**: `" ".join(line).ljust(max_width)`, always, even if it has
  several words. It never goes through the justification path.

Both come out as `ljust`, which is tempting to merge — don't. They are
triggered by different conditions (position in the output vs. number of words),
and merging them is how the last line ends up justified when it happens to hold
two words.
""",
        ),
        (
            "Dry run",
            """
`["This", "is", "an", "example", "of", "text", "justification."]`, width 16.

- `This`(4) + `is`(2): `4 + 1 + 2 = 7` ≤ 16, keep going. + `an`(2):
  `6 + 2 + 2 = 10` ≤ 16, keep. + `example`(7): `8 + 3 + 7 = 18` > 16 → **flush**.
  Line chars 8, gaps 2, spaces 8 → `divmod(8, 2) = (4, 0)` →
  `"This    is    an"`.
- `example` `of` `text`: chars 13, gaps 2, spaces 3 → `divmod(3, 2) = (1, 1)`,
  so the **first** gap gets 2 → `"example  of text"`.
- `justification.` is the last line → `"justification.  "`.

That middle line is the one to walk through in an interview: it is the only
place the uneven split shows, and it is where a right-biased remainder produces
`"example of  text"` instead.
""",
        ),
        (
            "Follow-ups",
            """
- **Do not pad the last line** — a one-line change, and a common real-world
  variant (this is how every text editor actually behaves).
- **Words longer than `maxWidth`** — hyphenate, or overflow the line. Ask which;
  neither is obviously right.
- **Knuth–Plass** for real typesetting quality: `O(n²)` DP over break points,
  cost = cube or square of the slack on each line, last line free. TeX uses it.
- **Centred or right-aligned** output: only `_justify` changes, which is a
  decent argument for having factored it out in the first place.
""",
        ),
    ],
}


def full_justify(words: list[str], max_width: int) -> list[str]:
    lines: list[str] = []
    line: list[str] = []
    line_chars = 0  # sum of word lengths on the current line, spaces excluded

    for word in words:
        # len(line) = the existing minimum gaps plus the one this word needs
        if line_chars + len(line) + len(word) > max_width:
            lines.append(_justify(line, line_chars, max_width))
            line, line_chars = [], 0

        line.append(word)
        line_chars += len(word)

    if line:  # the last line is left-justified, however many words it holds
        lines.append(" ".join(line).ljust(max_width))

    return lines


def _justify(line: list[str], line_chars: int, max_width: int) -> str:
    gaps = len(line) - 1
    if gaps == 0:
        return line[0].ljust(max_width)  # single word: left-justified, not centred

    width, extra = divmod(max_width - line_chars, gaps)  # leftmost `extra` gaps get +1
    padded = [word + " " * (width + (1 if i < extra else 0)) for i, word in enumerate(line[:-1])]
    return "".join(padded) + line[-1]


CASES = [
    (
        (["This", "is", "an", "example", "of", "text", "justification."], 16),
        ["This    is    an", "example  of text", "justification.  "],
    ),
    (
        (["What", "must", "be", "acknowledgment", "shall", "be"], 16),
        ["What   must   be", "acknowledgment  ", "shall be        "],
    ),
    (
        (
            [
                "Science", "is", "what", "we", "understand", "well", "enough",
                "to", "explain", "to", "a", "computer.", "Art", "is",
                "everything", "else", "we", "do",
            ],
            20,
        ),
        [
            "Science  is  what we",
            "understand      well",
            "enough to explain to",
            "a  computer.  Art is",
            "everything  else  we",
            "do                  ",
        ],
    ),
    (
        (["Listen", "to", "many,", "speak", "to", "a", "few."], 6),
        ["Listen", "to    ", "many, ", "speak ", "to   a", "few.  "],
    ),
    ((["a"], 1), ["a"]),
    ((["a", "b", "c", "d", "e"], 1), ["a", "b", "c", "d", "e"]),
    ((["a", "b"], 3), ["a b"]),
    (([], 5), []),
]


def solve(words: list[str], max_width: int) -> list[str]:
    return full_justify(words, max_width)
