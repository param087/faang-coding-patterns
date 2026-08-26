"""String Compression — LeetCode 443."""

from __future__ import annotations

META = {
    "pattern": "string-manipulation",
    "insight": "A run of length r costs at most r characters to encode, so a write pointer trailing a read pointer can never overtake it.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Compress a character array **in place** to runs of `char` + count, where a run
of length 1 gets no count, and return the new length. The caller only looks at
the first `length` entries; what sits beyond them is irrelevant.

Ask: are counts written as **individual digit characters** (yes — a run of 12
becomes `'1'`, `'2'`, two array slots, not one)? Is the array only lowercase
(no — LeetCode allows any printable ASCII, including digits, which matters if
anyone asks you to *decompress*)? Must it be `O(1)` extra space (yes, that is
the entire point — otherwise you would build a new list).
""",
        ),
        (
            "The insight",
            """
Two pointers into the same array: `read` scans runs, `write` lays down the
encoding behind it. The question is why that is safe — why `write` cannot
overrun data `read` has not consumed yet.

Count the characters a run of length `r` costs:

- `r = 1` → 1 slot (`"a"`), consumed 1;
- `r = 2` → 2 slots (`"a2"`), consumed 2;
- `r ≥ 3` → `1 + len(str(r))` slots, and `1 + len(str(r)) ≤ r` for every
  `r ≥ 3` (at `r = 100` it is 4 slots for 100 characters).

So the encoding of every prefix is never longer than the prefix itself, hence
`write ≤ read` holds as an invariant throughout. That inequality is the answer
to "prove the in-place version is correct", and it is what the interviewer is
actually asking about — not the loop.

Consume the whole run before writing anything. Writing per character and
patching the count afterwards works too, but you end up rewriting digits when a
run crosses 9 → 10, and that is where the bugs live.
""",
        ),
        (
            "The three ways it breaks",
            """
- **Multi-digit counts.** `str(run)` then write one slot per digit. `chars[write]
  = str(run)` puts `"12"` in a single cell — Python will not complain, the
  length comes out wrong, and the returned array looks almost right.
- **Runs of length 1 write no count.** `"abc"` compresses to `"abc"`, length 3,
  not `"a1b1c1"`. The `if run > 1` guard is one line and is the most-missed
  requirement in the problem.
- **The return value is the length, not the string.** Graders check
  `chars[:length]`. Returning `"".join(...)` passes your own test and fails
  theirs.

And one to raise unprompted: this encoding is **not reversible** once digits
can appear in the input. `['a', '1', '2']` compresses to `"a12"`, which decodes
back as twelve `a`s. LeetCode does not test it, but saying it shows you have
read the alphabet constraint rather than assumed lowercase — and the fix (an
escape character, or a length prefix) is the same one every real run-length
encoder needs.
""",
        ),
    ],
}


def compress(chars: list[str]) -> int:
    write = 0
    read = 0

    while read < len(chars):
        char = chars[read]
        run = 0
        while read < len(chars) and chars[read] == char:  # consume the whole run first
            read += 1
            run += 1

        chars[write] = char
        write += 1
        if run > 1:  # a run of 1 gets no count at all
            for digit in str(run):  # one array slot per digit
                chars[write] = digit
                write += 1

    return write  # write <= read held throughout, so nothing was clobbered


CASES = [
    ((["a", "a", "b", "b", "c", "c", "c"],), (6, "a2b2c3")),
    ((["a"],), (1, "a")),
    ((["a", "b", "c"],), (3, "abc")),
    ((["a", "b", "b"],), (3, "ab2")),
    ((["a"] * 12,), (3, "a12")),
    ((["a"] * 100 + ["b"],), (5, "a100b")),
    ((["a", "a", "a", "b", "b", "a", "a"],), (6, "a3b2a2")),
    (([],), (0, "")),
]


def solve(chars: list[str]) -> tuple[int, str]:
    working = list(chars)  # compress mutates in place; keep CASES reusable
    length = compress(working)
    return length, "".join(working[:length])
