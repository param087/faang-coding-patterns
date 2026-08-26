"""Reorganize String — LeetCode 767."""

from __future__ import annotations

from collections import Counter

META = {
    "pattern": "sorting",
    "insight": "Write the letters most-frequent-first into the even slots, then the odd ones — same-letter copies land two apart by construction.",
    "time": "O(n) — the tally sorts at most 26 entries",
    "space": "O(n) for the output",
    "sections": [
        (
            "What it asks",
            """
Rearrange the letters of `s` so that no two adjacent characters are equal, or
return `""` if that is impossible.

Two things to pin down before writing:

- **Any valid arrangement, or a specific one?** Any. That licences a
  *constructive* answer instead of a search, and it is the difference between an
  O(n) solution and backtracking.
- **Alphabet size?** Lowercase ASCII on LeetCode, so the tally is 26 entries and
  every "sort the counts" step is O(1) in disguise.

Note the shape of the answer: a feasibility test plus a construction. Candidates
who only write the construction fail `"aaab"`; candidates who only write the
test have not answered the question.
""",
        ),
        (
            "The insight",
            """
**Feasibility is a counting argument.** A letter appearing `c` times needs `c-1`
separators between its copies, so it fits iff it can claim every other slot:

```
c <= ceil(n / 2)  ->  (n + 1) // 2
```

`"aaab"`: n = 4, ceil = 2, and `a` appears 3 times — impossible, and no amount of
clever placement changes that.

**The construction is the parity trick.** Walk the letters in descending order of
frequency and write them into positions `0, 2, 4, ...`; when you run off the end,
drop to `1` and continue `1, 3, 5, ...`. Copies of one letter are written
consecutively, so within a parity run they sit exactly two apart and can never
touch.

The only place adjacency could appear is the wrap from the last even slot to the
first odd slot, and that is precisely what the feasibility test rules out: a
letter spanning the wrap would have to occupy the tail of the evens *and* the
head of the odds, which takes more than `ceil(n / 2)` copies. Placing the
most frequent letter first is what guarantees it fits entirely inside the evens.

`"vvvlo"` → `v` at 0, 2, 4, then `l` at 1 and `o` at 3 → `"vlvov"`.
""",
        ),
        (
            "The sort key is the count, not the letter",
            """
The tempting shortcut — sort the string alphabetically, cut it in half,
interleave the halves — looks equivalent and is not. `"vvvlo"` sorts to
`"lovvv"`; halves `"lov"` and `"vv"` interleave to `"lvovv"`, which ends in a
double `v`. It is feasible input and the method still fails, because the halves
are only balanced when the sort puts the *frequent* letters first.

Sort by count descending. The letters are a tie-break at most.

Two more things that bite:

- **The wrap index is 1, not 0.** Resetting to 0 overwrites everything you have
  already written, and the result still has the right length, so the bug shows
  up as a wrong string rather than a crash.
- **Check feasibility before building, not after.** Detecting the collision at
  the end means you have already produced garbage you now have to distinguish
  from a real answer.

A heap of `(-count, letter)` popping two distinct letters per step is the other
standard answer — O(n log 26), same result, more code. It earns its keep on the
generalisation: **Rearrange String k Distance Apart**, where copies must be `k`
apart instead of 2. Parity dies there; the heap plus a cooldown queue survives.
""",
        ),
    ],
}


def reorganize_string(s: str) -> str:
    n = len(s)
    counts = Counter(s)

    if n == 0 or max(counts.values()) > (n + 1) // 2:
        return ""

    result = [""] * n
    index = 0
    for letter, count in counts.most_common():  # frequency descending
        for _ in range(count):
            if index >= n:
                index = 1  # drop to the odd slots, never back to 0
            result[index] = letter
            index += 2

    return "".join(result)


CASES = [
    # Any valid arrangement is accepted; these are what this construction emits.
    (("aab",), "aba"),
    (("aaab",), ""),  # 3 > ceil(4/2): infeasible, whatever you try
    (("vvvlo",), "vlvov"),  # breaks sort-alphabetically-then-interleave
    (("zzzzz",), ""),
    (("aabb",), "abab"),
    (("aaabbc",), "ababac"),  # the most frequent letter exactly fills the evens
    (("a",), "a"),
    (("",), ""),
]


def solve(s: str) -> str:
    return reorganize_string(s)


def check() -> None:
    for args, expected in CASES:
        assert solve(*args) == expected, args

    for text in ("aab", "vvvlo", "aabb", "aaabbc", "aaabbbccc", "aabbcc", "aaaabbbb", "ab", "a"):
        result = reorganize_string(text)
        assert Counter(result) == Counter(text), (text, result)
        assert all(a != b for a, b in zip(result, result[1:], strict=False)), (text, result)

    # "" is returned exactly when the counting argument says it must be.
    for text in ("aaab", "zzzzz", "aaaab", "aabbbbb", ""):
        assert reorganize_string(text) == "", text
