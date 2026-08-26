"""Permutation in String — LeetCode 567."""

from __future__ import annotations

META = {
    "pattern": "sliding-window",
    "insight": "A permutation is a multiset, so the question is only whether some window of fixed length has the same letter counts as s1.",
    "time": "O(|s1| + |s2|)",
    "space": "O(1) — two 26-slot count arrays",
    "sections": [
        (
            "What it asks",
            """
Does `s2` contain **any permutation of `s1`** as a contiguous substring?
Return a boolean.

Ask: is the alphabet lowercase a–z (yes on LeetCode, so counts fit in a
26-array)? Does case matter? Must the substring be contiguous (yes — if it
were a subsequence this becomes a different, easier counting problem).

The first thing to say out loud: a permutation has a **fixed length**. So this
is a fixed-width window, not the grow-and-shrink kind, and the only thing
being tested is letter counts.
""",
        ),
        (
            "The insight",
            """
Permutation means "same multiset of characters". Two 26-slot arrays, `need`
for `s1` and `window` for the current `len(s1)` characters of `s2`, and you
want them equal at some position.

Slide the window one character at a time: add on the right, drop on the left.
Comparing the arrays outright is O(26) per position, giving O(26n) — perfectly
acceptable, and worth offering first.

To make it genuinely O(1) per step, carry `matches`: how many of the 26
letters currently have `window[c] == need[c]`. Each character that enters or
leaves changes exactly one slot, so `matches` moves by at most one:

- if the slot has just *become* equal, `matches += 1`;
- if it has just *left* equality, `matches -= 1`.

`matches == 26` means the window is a permutation. Note that letters absent
from both arrays count as matching — that is why the target is 26 and not the
number of distinct letters in `s1`.
""",
        ),
        (
            "Edge cases",
            """
- **`len(s1) > len(s2)`** — no window exists; return `False` before touching
  any index.
- **Empty `s1`** — the empty permutation is trivially present, so `True`. The
  count-only loop never fires for an empty window, so this needs its own
  guard; LeetCode's constraints hide the bug, an interviewer will not.
- **Repeated letters in `s1`**, `"aab"` vs `"eidbaaooo"` — a `set` of required
  characters passes wrongly here. Counts, not sets.
- **The equality direction.** After incrementing, the two cases to test are
  `window[c] == need[c]` (just became equal) and `window[c] == need[c] + 1`
  (just overshot). Writing `>` instead of `== need[c] + 1` decrements
  `matches` repeatedly on a long run of the same letter and the flag never
  recovers.
""",
        ),
    ],
}

ALPHABET = 26


def check_inclusion(s1: str, s2: str) -> bool:
    width = len(s1)
    if width == 0:
        return True
    if width > len(s2):
        return False

    need = [0] * ALPHABET
    window = [0] * ALPHABET
    for char in s1:
        need[ord(char) - ord("a")] += 1

    # Letters absent from both sides already match, hence the count over all 26.
    matches = sum(1 for slot in range(ALPHABET) if need[slot] == window[slot])

    for right, char in enumerate(s2):
        entering = ord(char) - ord("a")
        window[entering] += 1
        if window[entering] == need[entering]:
            matches += 1
        elif window[entering] == need[entering] + 1:  # just overshot
            matches -= 1

        if right >= width:
            leaving = ord(s2[right - width]) - ord("a")
            window[leaving] -= 1
            if window[leaving] == need[leaving]:
                matches += 1
            elif window[leaving] == need[leaving] - 1:  # just fell short
                matches -= 1

        if matches == ALPHABET:
            return True

    return False


CASES = [
    (("ab", "eidbaooo"), True),
    (("ab", "eidboaoo"), False),
    (("abc", "bbbca"), True),
    (("aab", "eidbaaooo"), True),
    (("hello", "ooolleoooleh"), False),
    (("a", "a"), True),
    (("ab", "a"), False),
    (("", ""), True),
]


def solve(s1: str, s2: str) -> bool:
    return check_inclusion(s1, s2)
