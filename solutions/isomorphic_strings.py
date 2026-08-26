"""Isomorphic Strings — LeetCode 205."""

from __future__ import annotations

META = {
    "pattern": "arrays-hashing",
    "insight": "Isomorphism is a bijection, so one map is half an answer — the second map is what rejects two letters collapsing onto one.",
    "time": "O(n)",
    "space": "O(1) — bounded by the alphabet",
    "sections": [
        (
            "What it asks",
            """
Can the characters of `s` be replaced to get `t`, with each character mapping
to exactly one character and no two characters mapping to the same one? Order
is preserved; a character may map to itself.

Ask: is the alphabet ASCII or full Unicode (it changes "O(1) space" into
"O(distinct)")? Are the strings guaranteed equal length? LeetCode says yes,
but the guard costs one line and unequal lengths are trivially non-isomorphic.
""",
        ),
        (
            "The insight",
            """
The wrong first answer is a single dictionary `s[i] -> t[i]`, checked for
conflicts. It passes `"egg"/"add"` and every friendly example, then returns
**True** for `"ab"/"aa"`: `a -> a`, `b -> a`, no conflict, but the mapping is
not invertible so `t` cannot be turned back into `s`.

"No two characters map to the same character" is the second half of the
sentence in the problem, and it is the half that decides the question. Keep
both directions and check both on every character.

`setdefault` fuses the two operations — insert-if-absent and read-back — into
one lookup: if the key was already bound, `setdefault` returns the old value
and the comparison fails. No `in` check needed.
""",
        ),
        (
            "The alternative worth mentioning",
            """
Encode each string as the sequence of **first-occurrence indices** of its
characters, then compare:

```
"paper" -> [0, 1, 0, 3, 1]
"title" -> [0, 1, 0, 3, 1]   equal, so isomorphic
```

It is one line with a helper, it is symmetric by construction (so the
two-map bug cannot occur), and it generalises: the same canonical form solves
**Word Pattern** and grouping "all strings with the same shape". The cost is
an extra O(n) list per string versus two small maps.

Say both out loud. Interviewers reading for signal want to hear that the
bijection is the requirement, not that you memorised a particular encoding.
""",
        ),
    ],
}


def is_isomorphic(s: str, t: str) -> bool:
    if len(s) != len(t):
        return False

    forward: dict[str, str] = {}
    backward: dict[str, str] = {}

    for a, b in zip(s, t, strict=True):
        # setdefault returns the existing binding if there is one.
        if forward.setdefault(a, b) != b:
            return False
        if backward.setdefault(b, a) != a:
            return False

    return True


CASES = [
    (("egg", "add"), True),
    (("foo", "bar"), False),
    (("paper", "title"), True),
    (("ab", "aa"), False),  # one-way map says True; not a bijection
    (("badc", "baba"), False),  # forward has no conflict either
    (("abc", "ab"), False),  # length mismatch
    (("a", "a"), True),
    (("", ""), True),
]


def solve(s: str, t: str) -> bool:
    return is_isomorphic(s, t)
