"""Distinct Echo Substrings — LeetCode 1316."""

from __future__ import annotations

MOD = (1 << 61) - 1  # Mersenne prime: wide enough that collisions are negligible
BASE = 131

META = {
    "pattern": "string-algorithms",
    "insight": "Fix the half-length first: an echo of half-length L is just a position where two adjacent length-L windows hash the same.",
    "time": "O(n²)",
    "space": "O(n²) worst case for the set of distinct echoes",
    "sections": [
        (
            "What it asks",
            """
Count **distinct** substrings of `text` that can be written as `a + a` for some
non-empty string `a`. Distinct as strings, not as positions — `"abcabcabc"`
contains `"abcabc"` twice but it counts once.

The two things to pin down before coding: distinctness is by content (that is
what forces a set rather than a counter), and `n ≤ 2000`, which is the
constraint telling you O(n²) is the target and O(n² log n) is probably still
fine.
""",
        ),
        (
            "The insight",
            """
Enumerating every substring and testing it is O(n³) — 2000³ = 8·10⁹, dead on
arrival. The reframe: **iterate over the half-length, not the substring.**

For a fixed half-length `L`, the substring starting at `i` of length `2L` is an
echo exactly when `text[i:i+L] == text[i+L:i+2L]`. With a precomputed
polynomial hash each of those windows is O(1), so the test is O(1), and the two
nested loops over `L` and `i` give O(n²) — 4·10⁶ at n = 2000.

Distinctness falls out of the same hash. Store `(L, hash_of_first_half)` in a
set: the first half plus the length determines the whole echo, so that pair is
a faithful identity for it. Storing the substrings themselves would be
correct but quadratic in memory *per entry* — up to 10⁶ echoes of average
length 10³ is a gigabyte of slices, which is the version that passes the
samples and dies on the real input.
""",
        ),
        (
            "Collisions — the question they will ask",
            """
"What if two different strings hash the same?" You need a real answer, not a
shrug.

The hash here is `sum(text[i] · BASE^k) mod (2⁶¹ - 1)`. Two distinct strings
collide with probability about `n / MOD` for a fixed pair; across the ~10⁶
pairs this problem compares, the union bound gives roughly
`10¹² / 2⁶¹ ≈ 4·10⁻⁷`. That is the number to quote.

The caveat is that a *fixed* base is deterministic, so an adversary who knows
it can construct a Thue-Morse collision. `BASE` is fixed here so the tests are
reproducible; in a contest with hacking, or if the interviewer pushes, draw it
randomly at start-up — that is one line and it removes the attack entirely,
because the adversary must now beat a random base.

The determinism-preserving alternative: verify each hash hit with a real slice
comparison. It costs O(L) per hit, which is fine when hits are rare but is O(n³)
on `"aaaa…a"`, where every position is a hit. Worth knowing that the trade
exists and which input decides it.
""",
        ),
    ],
}


def distinct_echo_substrings(text: str) -> int:
    n = len(text)
    power = [1] * (n + 1)
    prefix = [0] * (n + 1)
    for i, character in enumerate(text):
        power[i + 1] = power[i] * BASE % MOD
        prefix[i + 1] = (prefix[i] * BASE + ord(character)) % MOD

    def window(lo: int, hi: int) -> int:
        """Hash of text[lo:hi] in O(1)."""
        return (prefix[hi] - prefix[lo] * power[hi - lo]) % MOD

    # (half length, hash of the first half) identifies the echo uniquely.
    seen: set[tuple[int, int]] = set()
    for half in range(1, n // 2 + 1):
        for i in range(n - 2 * half + 1):
            left = window(i, i + half)
            if left == window(i + half, i + 2 * half):
                seen.add((half, left))

    return len(seen)


CASES = [
    (("abcabcabc",), 3),
    (("leetcodeleetcode",), 2),
    (("aabbaabb",), 3),
    (("abababab",), 3),
    (("aaaa",), 2),
    (("aaaaa",), 2),
    (("abc",), 0),
    (("a",), 0),
    (("",), 0),
]


def solve(text: str) -> int:
    return distinct_echo_substrings(text)
