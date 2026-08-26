"""Palindrome Partitioning — LeetCode 131."""

from __future__ import annotations

META = {
    "pattern": "backtracking",
    "insight": "The cut positions are the decision variable: at index `i`, take every prefix that is a palindrome and recurse on the rest.",
    "time": "O(n · 2ⁿ) — up to 2ⁿ⁻¹ partitions, each O(n) to copy",
    "space": "O(n²) for the palindrome table, O(n) recursion depth",
    "sections": [
        (
            "What it asks",
            """
Cut `s` into pieces so that **every** piece is a palindrome, and return all
such cuttings. `"aab"` gives `[["a","a","b"], ["aa","b"]]`.

Worth confirming: single characters count as palindromes (so an answer always
exists — the all-singletons cut), and the pieces must partition the string with
no gaps or overlaps. `n ≤ 16` in the constraints is the giveaway that
exhaustive enumeration is expected: there are n−1 gaps, each cut or not, so at
most 2¹⁵ = 32 768 candidate partitions.
""",
        ),
        (
            "The insight",
            """
Do not think about "pieces", think about **cut positions**. Standing at index
`start`, the only decision is where the current piece ends. So loop
`end` from `start` to the end of the string, and whenever `s[start:end+1]` is
a palindrome, commit that piece and recurse from `end + 1`.

That framing gives you the two halves for free:

- **Base case**: `start == len(s)` — the string is exhausted, `path` is a
  complete partition, record a copy.
- **Pruning**: the palindrome test on the prefix. A non-palindromic prefix
  prunes the entire subtree behind it, which is what keeps this well under the
  2ⁿ⁻¹ bound on real strings. On `"abcdefgh"` only the eight single letters
  ever pass, so there is precisely one answer and the tree is a path.

The pathological input is `"aaaa…"`, where every prefix is a palindrome and all
2ⁿ⁻¹ partitions are valid. That case is the reason the complexity has to be
quoted as exponential no matter how clever the palindrome test is — the output
alone is that large.
""",
        ),
        (
            "Precompute the palindrome table",
            """
The version most people write calls `sub == sub[::-1]` inside the loop. That is
O(n) per test, O(n) tests per node, so O(n²) *per node* of an exponential
tree — and it re-tests the same substring on every branch that passes through
it.

Precompute instead. `is_pal[i][j]` is true when `s[i..j]` is a palindrome, via
the recurrence

```
is_pal[i][j] = (s[i] == s[j]) and (j - i < 2 or is_pal[i + 1][j - 1])
```

filled with `i` descending so `i + 1` is always ready. That is O(n²) time and
O(n²) space once, after which every test in the recursion is a single array
lookup and the search cost collapses to O(number of nodes).

The follow-up worth pre-empting: **Palindrome Partitioning II** asks only for
the *minimum* number of cuts. Enumerating partitions to find the smallest is
exponential for a question that is O(n²) — the same `is_pal` table plus
`cuts[i] = 1 + min(cuts[j+1] for valid pieces s[i..j])`. Recognising when the
answer wants a count rather than the list is what separates the two problems.
""",
        ),
    ],
}


def partition(s: str) -> list[list[str]]:
    n = len(s)
    # is_pal[i][j]: s[i..j] inclusive is a palindrome.
    is_pal = [[False] * n for _ in range(n)]
    for i in range(n - 1, -1, -1):
        for j in range(i, n):
            if s[i] == s[j] and (j - i < 2 or is_pal[i + 1][j - 1]):
                is_pal[i][j] = True

    result: list[list[str]] = []
    path: list[str] = []

    def explore(start: int) -> None:
        if start == n:
            result.append(path[:])
            return
        for end in range(start, n):
            if not is_pal[start][end]:
                continue  # a bad prefix prunes the whole subtree
            path.append(s[start : end + 1])
            explore(end + 1)
            path.pop()

    explore(0)
    return result


CASES = [
    (("aab",), [["a", "a", "b"], ["aa", "b"]]),
    (("aaa",), [["a", "a", "a"], ["a", "aa"], ["aa", "a"], ["aaa"]]),
    (("aba",), [["a", "b", "a"], ["aba"]]),
    (("abc",), [["a", "b", "c"]]),
    (("cdd",), [["c", "d", "d"], ["c", "dd"]]),
    (("a",), [["a"]]),
    (("",), [[]]),
]


def solve(s: str) -> list[list[str]]:
    return partition(s)
