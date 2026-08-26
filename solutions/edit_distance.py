"""Edit Distance — LeetCode 72."""

from __future__ import annotations

META = {
    "pattern": "dp-strings",
    "insight": "Three predecessors, one per operation — and the base row is not zero, because emptying a string costs a deletion per character.",
    "time": "O(m · n)",
    "space": "O(min(m, n))",
    "sections": [
        (
            "What it asks",
            """
Minimum insertions, deletions and replacements to turn `a` into `b`.

Ask: do the three operations cost the same (yes here — a weighted variant
changes the recurrence); is it case-sensitive; can either string be empty.
""",
        ),
        (
            "Brute force",
            """
Recurse over the three operations at every position: O(3^(m+n)).

Then observe that the same `(i, j)` pair recurs constantly — which is the
signal for memoisation, and from there for a bottom-up table.
""",
        ),
        (
            "State",
            """
> `dp[i][j]` = the minimum operations to turn the first `i` characters of `a`
> into the first `j` characters of `b`.

Two pointers, one into each string. That is the state for essentially every
two-string DP, and once you accept it the recurrence is a two-case split.
""",
        ),
        (
            "The three predecessors",
            """
Name them as you write them — it makes the code readable and demonstrates you
know what each term *is*:

- `previous[j]` → **delete** from `a`
- `current[j-1]` → **insert** into `a`
- `previous[j-1]` → **replace**

When the characters already match, the cost carries over from the diagonal for
free and none of the three applies.
""",
        ),
        (
            "The base cases are not zero",
            """
Turning a string of length `i` into the empty string costs `i` deletions. So
row 0 is `0..n` and column 0 is `0..m`.

Initialising them to zero produces an answer that is too small and passes
several test cases before failing. This is the bug this problem has.
""",
        ),
        (
            "Dry run",
            """
`"horse" → "ros"` = **3**: replace h→r, delete r, delete e.

Trace the first row and column to show the base cases, then one interior cell
where the characters differ and the `min` of three applies.
""",
        ),
        (
            "Follow-ups",
            """
- **Reconstruct the edits** — walk backwards through the table following
  whichever predecessor produced each value.
- **Weighted operations** — multiply each term by its cost; the structure is
  unchanged.
- **One Edit Distance** — a two-pointer scan, O(n), no table needed. Knowing
  that the general machinery is overkill there is worth saying.
- **Delete Operation for Two Strings** — `m + n - 2·LCS`, the same table read
  differently.
""",
        ),
    ],
}


def min_distance(a: str, b: str) -> int:
    # Roll the shorter dimension to keep space at O(min(m, n)).
    if len(b) > len(a):
        a, b = b, a

    rows, cols = len(a), len(b)
    previous = list(range(cols + 1))  # base row: i deletions to empty

    for i in range(1, rows + 1):
        current = [i] + [0] * cols  # base column, same reason
        for j in range(1, cols + 1):
            if a[i - 1] == b[j - 1]:
                current[j] = previous[j - 1]  # free: characters already match
            else:
                current[j] = 1 + min(
                    previous[j],  # delete
                    current[j - 1],  # insert
                    previous[j - 1],  # replace
                )
        previous = current

    return previous[cols]


CASES = [
    (("horse", "ros"), 3),
    (("intention", "execution"), 5),
    (("", "abc"), 3),
    (("abc", ""), 3),
    (("", ""), 0),
    (("abc", "abc"), 0),
    (("a", "b"), 1),
]


def solve(a: str, b: str) -> int:
    return min_distance(a, b)
