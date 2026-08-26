"""Partition Labels — LeetCode 763."""

from __future__ import annotations

META = {
    "pattern": "two-pointers",
    "insight": "A letter's last occurrence is a floor on where its part can end; cut only when the sweep reaches the running max of those floors.",
    "time": "O(n)",
    "space": "O(1) — 26 last-seen indices",
    "sections": [
        (
            "What it asks",
            """
Cut `s` into as many pieces as possible such that **no letter appears in two
pieces**. Return the piece lengths, in order.

Two pointers walking the same direction: `start` pins the current piece, `end`
is the furthest index the piece is currently obliged to reach. Worth
confirming: the pieces must concatenate back to `s` (yes — this is a partition,
not a selection), and the alphabet is lowercase a–z (so the last-occurrence
table is 26 slots, not a hash map you have to defend).
""",
        ),
        (
            "The insight",
            """
One pass to record `last[c]`, the final index of each letter. Then sweep once
more, and at index `i` widen the current piece:

```
end = max(end, last[s[i]])
```

`end` is the running maximum of every obligation the piece has taken on. When
`i == end`, every letter seen since `start` has been fully consumed — nothing
inside can recur later — so cut, and it is safe to cut *immediately* because
cutting earlier is impossible and cutting later would only merge two valid
pieces into one. Greedy-earliest is optimal, and that sentence is the proof.
""",
        ),
        (
            "The wrong cut condition",
            """
The tempting version cuts when `i == last[s[i]]` — "I have finished this
letter, so end the piece". It is wrong the moment a letter's span **encloses**
another's.

`"abac"`: `last = {a: 2, b: 1, c: 3}`. At `i = 1` you have `last['b'] == 1`, so
the naive rule cuts `"ab"` — but `a` reappears at index 2, straddling the cut.
The correct answer is `[3, 1]`: `"aba"` then `"c"`. Only the running max sees
that `b` is trapped inside `a`'s span.

Two smaller traps:

- `end` must **never move backwards**; it is `max(end, ...)`, not an
  assignment.
- Reset `start = i + 1` at the cut, and reset `end` too (or let the next
  `max(end, last[s[i]])` do it — but only because `end == i` at that instant;
  say why, do not just hope).

Same shape as **Merge Intervals**: you are merging the spans `[first[c],
last[c]]` and reporting the merged widths. If the interviewer pushes on a
larger alphabet or unicode, swap the 26-array for a dict and nothing else
changes.
""",
        ),
    ],
}


def partition_labels(s: str) -> list[int]:
    last = {ch: i for i, ch in enumerate(s)}  # last occurrence of each letter

    sizes: list[int] = []
    start = end = 0
    for i, ch in enumerate(s):
        end = max(end, last[ch])  # take on this letter's obligation
        if i == end:  # nothing seen since `start` recurs later
            sizes.append(end - start + 1)
            start = i + 1

    return sizes


CASES = [
    (("ababcbacadefegdehijhklij",), [9, 7, 8]),
    (("eccbbbbdec",), [10]),
    (("abac",), [3, 1]),  # b is enclosed by a's span: kills the naive cut
    (("abaccbdeffed",), [6, 6]),
    (("abcabc",), [6]),
    (("abc",), [1, 1, 1]),
    (("a",), [1]),
    (("",), []),
]


def solve(s: str) -> list[int]:
    return partition_labels(s)
