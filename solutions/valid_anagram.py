"""Valid Anagram — LeetCode 242."""

from __future__ import annotations

from collections import Counter

META = {
    "pattern": "arrays-hashing",
    "insight": "An anagram is an equal multiset, so one tally incremented by s and decremented by t must never go negative.",
    "time": "O(n)",
    "space": "O(1) — 26 letters, or O(k) distinct characters for Unicode",
    "sections": [
        (
            "What it asks",
            """
Decide whether `t` is a rearrangement of `s`, using every character exactly as
often as it appears.

Ask about the alphabet. LeetCode restricts the input to lowercase English
letters, which is what licences the O(1) space claim — a 26-slot array. The
interviewer will almost always follow up with **"what if the input is
Unicode?"**, and the answer is a dict, with space O(k) in the number of
distinct code points. Also confirm whether case and whitespace matter; on
LeetCode they do not arise, in an interview they usually do.
""",
        ),
        (
            "The insight",
            """
Anagram means *equal multisets*, nothing more. Sorting both strings proves it
in O(n log n); counting proves it in O(n), and the constraint on the alphabet
is the hint that counting is expected.

Two details do the real work:

1. **The length guard.** `len(s) != len(t)` is an O(1) rejection, and without
   it a one-directional decrement pass is wrong: counting down `t` against a
   tally built from `s` accepts `s = "aab"`, `t = "ab"` unless you also check
   that nothing is left over.
2. **Bail on the first negative.** Once a count drops below zero, `t` has a
   character `s` cannot supply. No need to finish the pass.

`Counter(s) == Counter(t)` is a legitimate one-liner and worth saying, but
write the explicit version — it is the one that generalises to streaming input
and to the early exit.
""",
        ),
        (
            "Follow-ups",
            """
- **Unicode.** Swap the 26-array for a dict. Then worry about normalisation:
  `"é"` is one code point (U+00E9) or two (`e` + U+0301), and those are the
  same grapheme but different multisets. `unicodedata.normalize("NFC", s)`
  first, and say why.
- **Group Anagrams (49)** — the same canonical-form idea, but the tally becomes
  a hash key rather than a comparison.
- **Find All Anagrams in a String (438)** — a fixed-width sliding window over
  the same 26-slot tally, updating two counts per step instead of rebuilding.
""",
        ),
    ],
}


def is_anagram(s: str, t: str) -> bool:
    if len(s) != len(t):
        return False  # O(1) rejection, and it is what makes the one-way pass correct

    counts = Counter(s)
    for character in t:
        counts[character] -= 1
        if counts[character] < 0:
            return False  # t needs a character s cannot supply

    return True


CASES = [
    (("anagram", "nagaram"), True),
    (("rat", "car"), False),
    (("aacc", "ccac"), False),  # same character set, different multiplicities
    (("aab", "ab"), False),  # the case a missing length guard accepts
    (("", ""), True),
    (("a", ""), False),
    (("你好吗", "吗好你"), True),
    (("ab", "ba"), True),
]


def solve(s: str, t: str) -> bool:
    return is_anagram(s, t)
