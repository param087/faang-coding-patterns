"""Sum of Scores of Built Strings — LeetCode 2223."""

from __future__ import annotations

import random

META = {
    "pattern": "string-algorithms",
    "insight": "Building by prepending means the built strings are exactly the suffixes, so the scores are the Z-array of s — sum it.",
    "time": "O(n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
You build `s` one character at a time, **prepending** each new character, so
after `i` steps you hold the last `i` characters of `s`. The score of that
intermediate string is the length of the longest common prefix it shares with
the finished `s`. Return the sum of all n scores.

Strip the story and it says: **the built strings are the suffixes of `s`**, and
score(i) = LCP(`s`, `s[i:]`). The final string scores `n`.

Worth asking, because it is the only implementation trap for a typed language:
how big can the answer get? `"aaa…a"` at n = 10⁵ scores n + (n−1) + … + 1 ≈
**5 × 10⁹**, which overflows a 32-bit `int`. Python does not care; say it
anyway, because in Java or C++ that single word `long` is the difference
between accepted and wrong-answer on the last test case.
""",
        ),
        (
            "The insight",
            """
Brute force compares each suffix with `s` character by character. On a random
string it finishes almost immediately, which is exactly why people submit it —
but on `"aaa…a"` every comparison runs to the end of the string, giving
n²/2 = **5 × 10⁹ character comparisons** at n = 10⁵. That is the adversarial
case, and it is the one in the test set.

The array you want has a name: `z[i]` = length of the longest common prefix of
`s` and `s[i:]`. That is *literally* the score of the i-th built string, so

```
answer = z[0] + z[1] + ... + z[n-1]   with z[0] = n
```

and the Z-function computes the whole array in O(n).

The wrong first answer worth naming: **the KMP prefix function is not this
array.** `failure[i]` is the longest proper prefix of `s[:i+1]` that is also a
suffix of it — a different quantity, and summing it gives a different (smaller)
number. On `"aabaaab"` the Z-array is `[7,1,0,2,3,1,0]` summing to **14**, while
the prefix function is `[0,1,0,1,2,2,3]` summing to **9**. You can *derive* Z
from the prefix function, but the derivation is longer than just writing Z.
""",
        ),
        (
            "The pitfall: the two branches of the Z-box",
            """
Keep `[left, right)` as the match of a prefix of `s` that reaches furthest
right. For a new `i` inside that window, `s[i:right]` equals `s[i-left:right-left]`,
so the already-computed `z[i - left]` is a free head start. Two branches:

- `z[i - left] < right - i` — the earlier match ended *strictly inside* the
  window, and the character that killed it is mirrored here too. `z[i]` is
  exactly `z[i - left]`; no scanning.
- `z[i - left] >= right - i` — the copy only proves the match up to `right`.
  Beyond `right` you know nothing, so you **must** keep comparing.

`z[i] = min(right - i, z[i - left])` followed by the naive `while` handles both.
Dropping the `min` is the classic bug: it copies a value that runs past `right`
and asserts a match nobody verified. Dropping the `while` is the other half of
the same bug — on `"aaabaaaab"` the Z-array is `[9,2,1,0,3,4,2,1,0]`, and index
5 gets only 2 from the box before it has to extend to **4**. Skip the extension
and you both under-count that index and fail to push `right` forward, so the
damage propagates to every later index too.

Linearity: `right` never decreases, and every successful character comparison in
the `while` pushes it forward, so the total work in that loop is at most n
across the whole run. One failed comparison per `i` on top. **O(n)** — and being
able to say *why* is the point of the question.
""",
        ),
    ],
}


def z_function(s: str) -> list[int]:
    """z[i] = length of the longest common prefix of s and s[i:]."""
    n = len(s)
    z = [0] * n
    if n == 0:
        return z
    z[0] = n

    left = right = 0  # [left, right) is the prefix match reaching furthest right
    for i in range(1, n):
        if i < right:
            # min() matters: past `right` the box proves nothing.
            z[i] = min(right - i, z[i - left])
        while i + z[i] < n and s[z[i]] == s[i + z[i]]:
            z[i] += 1
        if i + z[i] > right:
            left, right = i, i + z[i]
    return z


def sum_scores(s: str) -> int:
    return sum(z_function(s))


def _brute_force(s: str) -> int:
    """The definition, spelled out — O(n²), used only to cross-check."""
    total = 0
    for i in range(len(s)):
        k = 0
        while i + k < len(s) and s[k] == s[i + k]:
            k += 1
        total += k
    return total


CASES = [
    (("babab",), 9),
    (("azbazbzaz",), 14),
    (("aaabaaaab",), 22),  # index 5 must extend past the Z-box
    (("aaaa",), 10),  # the n²/2 adversarial shape
    (("aabaaab",), 14),  # 6 if you sum the prefix function instead
    (("abcde",), 5),  # no repeats: only the full string scores
    (("a",), 1),
    (("",), 0),
]


def solve(s: str) -> int:
    return sum_scores(s)


def check() -> None:
    for args, expected in CASES:
        assert solve(*args) == expected, args

    # The Z-box branches are easy to get subtly wrong, so verify the fast
    # version against the definition on a deterministic random sample.
    rng = random.Random(2223)
    for _ in range(300):
        sample = "".join(rng.choice("ab") for _ in range(rng.randint(1, 40)))
        assert sum_scores(sample) == _brute_force(sample), sample
