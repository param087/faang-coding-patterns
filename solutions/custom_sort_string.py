"""Custom Sort String — LeetCode 791."""

from __future__ import annotations

from collections import Counter

META = {
    "pattern": "sorting",
    "insight": "Nothing needs comparing: count the letters of s, emit them in the order the permutation gives, then dump whatever is left.",
    "time": "O(n + k), n = len(s), k = len(order)",
    "space": "O(1) — 26 counters",
    "sections": [
        (
            "What it asks",
            """
`order` is a permutation of some distinct letters. Rearrange `s` so that if two
characters both appear in `order`, they appear in `s` in that same relative
order. Characters of `s` absent from `order` may go anywhere.

The clarification that changes the code: **may characters of `order` be missing
from `s`, and may `s` contain characters `order` never mentions?** Both yes —
and the second is the half of the problem people forget to output at all.
""",
        ),
        (
            "The insight",
            """
The comparator answer — build `rank = {c: i}` and `sorted(s, key=lambda c:
rank.get(c, len(order)))` — is a legitimate O(n log n) answer and takes ten
seconds to write. It is worth saying, then improving on.

Since the alphabet has 26 letters, you never need to compare anything. Count
`s` once, then walk `order` and emit `char * count[char]` for each. Any
character left in the counter did not appear in `order`, so append it in any
order. That is O(n + k) with 26 counters of space.

The general move: **when the key space is small and bounded, a counting pass
replaces the sort**. That is what this problem is testing, not the comparator.
""",
        ),
        (
            "Edge cases",
            """
- **Leftovers are the whole trick.** Forgetting the second loop passes the
  sample (`order = "cba"`, `s = "abcd"` still needs its `d`) only if you are
  lucky. Emit them; the order among them is unconstrained.
- **`order` may be empty** — then everything is a leftover and `s` comes back
  unchanged, which is valid.
- **Duplicates in `s` must all survive.** Emitting one copy per character in
  `order` instead of `count` copies is the common bug: `"pekeq"` has two `e`s.
- **`pop(char, 0)`** does double duty — it fetches the count and removes the
  character so the leftover loop cannot re-emit it. A plain `get` needs a
  second `seen` set.
- If `order` were allowed repeats, `pop` still behaves (the second occurrence
  emits nothing); a `rank` dict would silently keep the last index instead.
""",
        ),
    ],
}


def custom_sort_string(order: str, s: str) -> str:
    counts = Counter(s)

    pieces = [char * counts.pop(char, 0) for char in order]
    # Whatever order never mentioned may go anywhere; here, first-seen order.
    pieces.extend(char * count for char, count in counts.items())
    return "".join(pieces)


CASES = [
    (("cba", "abcd"), "cbad"),
    (("kqep", "pekeq"), "kqeep"),
    (("cbafg", "abcd"), "cbad"),
    (("bcafg", "abcd"), "bcad"),
    (("xyz", "zzyyxx"), "xxyyzz"),
    (("a", "aaabbb"), "aaabbb"),
    (("", "hello"), "hello"),
    (("abc", ""), ""),
]


def solve(order: str, s: str) -> str:
    return custom_sort_string(order, s)
