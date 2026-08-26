"""Longest Duplicate Substring — LeetCode 1044."""

from __future__ import annotations

MOD = (1 << 61) - 1
BASE = 131

META = {
    "pattern": "string-algorithms",
    "insight": "Duplicate lengths are downward-closed, so binary search the length and let a rolling hash answer the fixed-length question in one pass.",
    "time": "O(n log n) expected",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Return the longest substring that occurs at least twice in `s`. Occurrences
**may overlap** — `"aaaaa"` answers `"aaaa"`, taken from positions 0 and 1.
Return the empty string if nothing repeats. Any one of several equally long
answers is accepted.

Confirm the overlap rule first; the non-overlapping variant is a genuinely
different (and harder) problem, and candidates lose the round by silently
assuming the wrong one. `n ≤ 3·10⁴`.
""",
        ),
        (
            "The insight",
            """
Two moves, and you need both.

**Monotonicity.** If some substring of length `L` occurs twice, then its own
prefix of length `L - 1` occurs twice as well. So "does a duplicate of length
`L` exist?" is `True` for every `L` up to the answer and `False` above it —
a step function, which is exactly what binary search on the answer needs.
That collapses the problem to O(log n) feasibility checks.

**Rabin-Karp for the check.** For a fixed `L`, slide a window and hash each of
the `n - L + 1` substrings with a rolling polynomial hash; a repeat is a hash
seen twice. One O(n) pass per check, O(n log n) overall — about 3·10⁴ × 15 =
4.5·10⁵ window hashes at the stated limit.

The alternative is a suffix automaton or suffix array with LCP, which gives
O(n) or O(n log n) deterministically and is the "right" answer in a
string-algorithms course. In a 40-minute interview, binary search plus rolling
hash is the one you can actually finish and debug.
""",
        ),
        (
            "Verification, and the input that decides the complexity",
            """
Hash equality is not string equality. The code below confirms every hash hit
with a real slice comparison, which makes the result **deterministic** — no
"probably correct" caveat when the interviewer asks.

What that costs is bounded by how often the hash lies. With a 2⁶¹ modulus, a
false hit across the ~5·10⁵ comparisons this makes has probability around
10⁻⁷, so verification is essentially free — *on genuine collisions*. The real
cost is genuine matches: on `"aaaa…a"` every window matches every other, and a
naive bucket scan degenerates to O(n²) per check.

The fix in the code is that the confirmation compares against candidates in the
same hash bucket and returns on the first success, so the "everything matches"
case exits immediately rather than being the slow one. The input that would
actually hurt is one with many equal-hash-but-unequal windows, and that is
precisely what the wide modulus rules out.

If you want the caveat gone entirely, draw `BASE` randomly at start-up; it is
fixed here so the tests are reproducible.
""",
        ),
    ],
}


def longest_dup_substring(s: str) -> str:
    n = len(s)
    if n < 2:
        return ""

    power = [1] * (n + 1)
    prefix = [0] * (n + 1)
    for i, character in enumerate(s):
        power[i + 1] = power[i] * BASE % MOD
        prefix[i + 1] = (prefix[i] * BASE + ord(character)) % MOD

    def window(lo: int, hi: int) -> int:
        return (prefix[hi] - prefix[lo] * power[hi - lo]) % MOD

    def find(length: int) -> int:
        """Start index of some substring of this length seen twice, else -1."""
        buckets: dict[int, list[int]] = {}
        for i in range(n - length + 1):
            digest = window(i, i + length)
            candidates = buckets.setdefault(digest, [])
            for j in candidates:
                if s[j : j + length] == s[i : i + length]:  # confirm, never trust
                    return i
            candidates.append(i)
        return -1

    best_start, best_length = 0, 0
    low, high = 1, n - 1  # a duplicate can be at most n - 1 long
    while low <= high:
        mid = (low + high) // 2
        start = find(mid)
        if start >= 0:
            best_start, best_length = start, mid
            low = mid + 1
        else:
            high = mid - 1

    return s[best_start : best_start + best_length]


CASES = [
    (("banana",), "ana"),
    (("mississippi",), "issi"),
    (("abcabcabc",), "abcabc"),  # the two occurrences overlap
    (("ababab",), "abab"),
    (("aaaaa",), "aaaa"),
    (("abcd",), ""),
    (("aa",), "a"),
    (("a",), ""),
    (("",), ""),
]


def solve(s: str) -> str:
    return longest_dup_substring(s)
