"""Is Subsequence — LeetCode 392."""

from __future__ import annotations

META = {
    "pattern": "two-pointers",
    "insight": "Matching each character of s at its earliest possible position in t is never worse, so one forward sweep decides it.",
    "time": "O(|s| + |t|)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Is `s` a subsequence of `t` — can you delete some characters from `t`, without
reordering the rest, and be left with `s`?

Two pointers, one per string. Advance `j` through `t` every step; advance `i`
only on a match. `s` is a subsequence exactly when `i` reaches `len(s)`.

The clarifying question that matters is **the follow-up**, and it is worth
asking up front: *"is `t` fixed while many different `s` are queried?"* If the
answer is yes, the linear scan is the wrong shape and the interviewer is
waiting for you to notice.
""",
        ),
        (
            "The insight",
            """
Greedy is safe here, and you should be able to say *why* rather than just
assert it. Exchange argument: suppose some valid embedding of `s` into `t`
matches `s[i]` at position `p`. The greedy scan matches `s[i]` at the earliest
free position `q ≤ p`. Rewriting that embedding to use `q` instead of `p`
leaves the remaining suffix of `t` strictly larger, so it is still valid.
Induct: greedy never paints you into a corner.

That is the whole problem. There is no backtracking, no DP table, and any
answer that reaches for `O(|s|·|t|)` edit-distance machinery is over-built.
""",
        ),
        (
            "Follow-up: 10⁹ queries against one t",
            """
"Suppose there are 10⁹ incoming `s`, each up to 100 long, against one fixed
`t` of length 10⁴." Rescanning `t` per query is 10⁹ × 10⁴ = **10¹³ character
comparisons**. Dead.

Preprocess `t` into a jump table: `nxt[i][c]` = the smallest index `j ≥ i` with
`t[j] == c`, or `n` if there is none. Build it backwards in one pass, `O(26n)`
time and memory — 260 000 ints for n = 10⁴, trivial.

Each query then costs `O(|s|)` **table lookups, independent of |t|**: 10⁹ × 100
= 10¹¹ … still large, but now it is the query volume that is the problem, not
the algorithm, and that is the answer they want.

The memory-lean alternative, when 26n is too much: store per-character sorted
index lists and binary-search each one, `O(|s| log |t|)` per query with `O(n)`
total memory. Both are acceptable; know which constraint pushes you to which.

`SubsequenceMatcher` below implements the jump table, and `check()` asserts it
agrees with the two-pointer scan on every case.
""",
        ),
    ],
}


def is_subsequence(s: str, t: str) -> bool:
    i = 0  # position in s; j walks t unconditionally
    for j in range(len(t)):
        if i < len(s) and s[i] == t[j]:
            i += 1
    return i == len(s)


class SubsequenceMatcher:
    """Follow-up form: preprocess t once, answer each s in O(|s|). Lowercase a-z."""

    def __init__(self, t: str) -> None:
        self.n = len(t)
        # nxt[i][c] = first index >= i holding c, else n. Row n is the sentinel.
        self.nxt = [[self.n] * 26 for _ in range(self.n + 1)]
        for i in range(self.n - 1, -1, -1):
            self.nxt[i] = self.nxt[i + 1][:]
            self.nxt[i][ord(t[i]) - 97] = i

    def matches(self, s: str) -> bool:
        i = 0
        for ch in s:
            i = self.nxt[i][ord(ch) - 97]
            if i == self.n:
                return False
            i += 1  # consume the matched character
        return True


CASES = [
    (("abc", "ahbgdc"), True),
    (("axc", "ahbgdc"), False),
    (("aab", "baab"), True),  # greedy must not stop at the first 'a' it sees
    (("acb", "abc"), False),  # order is part of the question
    (("aaa", "aa"), False),
    (("", "abc"), True),
    (("abc", ""), False),
    (("", ""), True),
]


def check() -> None:
    for args, expected in CASES:
        assert solve(*args) == expected, (args, expected)
        # The jump-table form must agree with the scan on every case.
        assert SubsequenceMatcher(args[1]).matches(args[0]) == expected, args


def solve(s: str, t: str) -> bool:
    return is_subsequence(s, t)
