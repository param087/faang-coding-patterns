"""Sort Characters By Frequency — LeetCode 451."""

from __future__ import annotations

from collections import Counter

META = {
    "pattern": "sorting",
    "insight": "Frequencies are bounded by the string length, so index by count instead of comparing counts — a bucket walk, not a sort.",
    "time": "O(n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Rearrange a string so that characters appear grouped and ordered by how often
they occur, most frequent first. Any ordering among characters with the same
frequency is accepted.

Two clarifications worth voicing: the alphabet is **not** just lowercase (digits
and both cases appear, so 128 buckets, not 26), and ties are free — which is
what lets you skip a comparison sort entirely.
""",
        ),
        (
            "The insight",
            """
The obvious answer is `Counter(s).most_common()`, which is O(k log k) in the
alphabet size — perfectly acceptable, and worth saying out loud first.

The better answer uses the fact that **every frequency lies in `1..n`**. Build
an array of `n + 1` buckets and drop each character into `buckets[count]`, then
walk the buckets from `n` down to `1` and emit `char * count`. That is a
counting sort on the frequency, so the whole thing is O(n) with no comparisons
at all.

The output length is `n`, so O(n) is the floor; this hits it.
""",
        ),
        (
            "Edge cases",
            """
- **Ties are arbitrary, so pin them deliberately.** `Counter` preserves first
  appearance order and appending within a bucket keeps it, so `"cccaaa"` comes
  back as `"cccaaa"` rather than `"aaaccc"`. The grader accepts either; a
  *test suite* needs the behaviour to be deterministic, which it is here.
- **Case matters.** `"Aabb"` → `"bbAa"`: `'A'` and `'a'` are different
  characters. Lower-casing the input to save buckets silently changes the
  answer.
- **Empty string** — the bucket array is `[0]` long and the descending walk
  never executes, so it returns `""` with no special case.
- **All identical** — one bucket at index `n`, one emit.
- Building the result with `+=` on a string is O(n²) in the worst case; collect
  the pieces in a list and `"".join` them.
""",
        ),
    ],
}


def frequency_sort(s: str) -> str:
    counts = Counter(s)

    # buckets[c] = characters occurring exactly c times; c is at most len(s).
    buckets: list[list[str]] = [[] for _ in range(len(s) + 1)]
    for char, count in counts.items():
        buckets[count].append(char)

    pieces: list[str] = []
    for count in range(len(s), 0, -1):
        for char in buckets[count]:
            pieces.append(char * count)
    return "".join(pieces)


CASES = [
    (("tree",), "eetr"),
    (("cccaaa",), "cccaaa"),
    (("Aabb",), "bbAa"),
    (("2a554442f544",), "4444455522af"),
    (("abbccc",), "cccbba"),
    (("aaa",), "aaa"),
    (("a",), "a"),
    (("",), ""),
]


def solve(s: str) -> str:
    return frequency_sort(s)
