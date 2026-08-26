"""Top K Frequent Words — LeetCode 692."""

from __future__ import annotations

import heapq
from collections import Counter

META = {
    "pattern": "sorting",
    "insight": "One key runs in two directions: (-count, word) sorts frequency down and breaks ties alphabetically up.",
    "time": "O(n + m log k) — n words, m distinct",
    "space": "O(m)",
    "sections": [
        (
            "What it asks",
            """
Return the `k` most frequent words, ordered by frequency descending, ties broken
by the word ascending in dictionary order. Unlike Top K Frequent *Elements*, the
output order is fully specified — there is no "any order" escape hatch, and the
tie rule is the problem.

Worth asking: is the comparison case-sensitive (on LeetCode yes, plain ASCII
lowercase), and is `k` guaranteed at most the number of distinct words (yes).
The line that decides your answer is the follow-up printed in the statement:
**O(n log k) time and O(k) space**. That rules out sorting the whole tally and
is the entire reason the question exists.
""",
        ),
        (
            "The insight",
            """
The counting is trivial. The interview is in the key.

Frequency descends, the word ascends. Python only sorts one way, so encode the
direction *in the key* rather than in a comparator: negate the count, leave the
word alone.

```python
key = (-counts[word], word)
```

Tuples compare left to right, so `-count` decides first and `word` only settles
ties. This is the pattern's whole thesis — the sort is one line once the key is
right, and a bespoke `cmp_to_key` comparator here is a step backwards: slower,
and more surface for an off-by-one in the sign.

`heapq.nsmallest(k, ...)` applies that key while keeping only `k` items in the
heap, giving **O(m log k)** and O(k) extra space, and it hands the results back
already ordered. Plain `sorted(...)[:k]` is O(m log m) — fine when `k` is close
to `m`, and worth naming as the one-liner you would ship if the constraint were
not stated.
""",
        ),
        (
            "The trap in the hand-rolled heap",
            """
The textbook O(n log k) shape is "push into a **min**-heap, pop when it exceeds
size k". That requires the heap's order to be the *reverse* of the answer's
order: smallest count first, and for equal counts the **alphabetically largest**
word first, so it is the one evicted.

You can negate the count. You cannot negate a string. `(count, word)` evicts the
alphabetically *smallest* word on a tie — the exact opposite of what the problem
wants — and this passes the sample and fails on ties, which is the worst kind of
bug to find at minute 35.

The two ways out:

```python
class Entry:                       # wrap and invert only the string half
    def __lt__(self, other):
        if self.count != other.count:
            return self.count < other.count
        return self.word > other.word   # note the flip
```

or let `heapq.nsmallest` keep the size-`k` heap for you under the forward key
`(-count, word)`, which is what the code below does.

One more detail people lose: popping a size-`k` min-heap yields the answer
**backwards**. Reverse it. `nsmallest` sidesteps that too, which is a large part
of why it is the version to write under time pressure.
""",
        ),
    ],
}


def top_k_frequent(words: list[str], k: int) -> list[str]:
    counts = Counter(words)
    # -count descends, word ascends: two directions in a single key.
    return heapq.nsmallest(k, counts, key=lambda word: (-counts[word], word))


CASES = [
    ((["i", "love", "leetcode", "i", "love", "coding"], 2), ["i", "love"]),
    (
        (["the", "day", "is", "sunny", "the", "the", "the", "sunny", "is", "is"], 4),
        ["the", "is", "sunny", "day"],
    ),
    # Frequency outranks the alphabet — a key of just `word` passes neither.
    ((["b", "b", "a"], 1), ["b"]),
    # Every count tied, so the answer is purely lexicographic.
    ((["c", "b", "a"], 2), ["a", "b"]),
    # A tie that straddles the cut-off.
    ((["a", "b", "c", "a", "b"], 2), ["a", "b"]),
    ((["aaa", "aa", "a"], 3), ["a", "aa", "aaa"]),  # shorter first, not longer
    ((["only"], 1), ["only"]),
    (([], 0), []),
]


def solve(words: list[str], k: int) -> list[str]:
    return top_k_frequent(words, k)
