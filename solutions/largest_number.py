"""Largest Number — LeetCode 179."""

from __future__ import annotations

from functools import cmp_to_key

META = {
    "pattern": "sorting",
    "insight": "Order is decided pairwise by which concatenation reads larger, a+b against b+a — no property of a single number can do it.",
    "time": "O(n log n · d), d = digits per number",
    "space": "O(n · d) for the string copies",
    "sections": [
        (
            "What it asks",
            """
Given non-negative integers, concatenate them in whatever order produces the
largest possible number, and return it **as a string**.

Ask two things up front: can the result exceed a 64-bit integer (yes — 100
numbers of 9 digits each, so the return type must be a string), and can the
input be all zeros (yes, and that single case is where most submissions fail).
""",
        ),
        (
            "The brute force, and why it fails",
            """
Try every permutation and keep the largest concatenation. Correct, and useless:
the constraint is n ≤ 100, and 100! ≈ 9.3 × 10¹⁵⁷ — more orderings than there
are atoms in the observable universe.

The interesting question is not "how do I search this" but "is there a *local*
rule that produces the global optimum". There is.
""",
        ),
        (
            "The insight",
            """
For two candidates `a` and `b`, the only thing that matters is which of the two
gluings is bigger:

```
a before b  ⟺  a + b > b + a   (string concatenation)
```

Because both sides have identical length and identical digit multisets, this is
just a lexicographic comparison of two equal-length strings — no big-integer
arithmetic needed.

Sort the whole array with that comparator and concatenate. The point of the
problem is recognising that a **pairwise** rule, applied by a sort, gives the
globally optimal arrangement.
""",
        ),
        (
            "Why the comparator is legal",
            """
This is the follow-up an interviewer will actually push on: `sort` requires a
**strict weak ordering**, so the rule has to be transitive. It is —
`a+b > b+a` is equivalent to comparing the infinite repetitions `aaa…` and
`bbb…` lexicographically, and lexicographic order on infinite strings is a
total order. Say that; do not just assert "it works".

The wrong first answers, both of which pass the samples:

- **Sort the strings descending lexicographically.** `[121, 12]` gives
  `"121" > "12"`, so you emit `"12112"`, but `"12121"` is larger.
- **Sort by first digit, break ties by length.** `[3, 30]` is fine, `[30, 34]`
  is fine, `[8308, 830]` is not — you need the concatenation test, not a proxy
  for it.
""",
        ),
        (
            "The all-zeros trap",
            """
`[0, 0]` sorts to `"0" + "0"` = `"00"`. The expected answer is `"0"`.

One guard covers it: if the first character of the result is `'0'`, every
number was zero, so return `"0"`. Stripping leading zeros with `lstrip` is the
buggy version — it turns `"00"` into `""`.
""",
        ),
        (
            "Dry run",
            """
`[3, 30, 34, 5, 9]` as strings `["3", "30", "34", "5", "9"]`.

- `"3"` vs `"30"`: `"330"` > `"303"`, so **3 before 30**. The shorter one wins
  here, which is the case that kills length-based tie-breaks.
- `"34"` vs `"3"`: `"343"` > `"334"`, so **34 before 3**.
- Final order `9, 5, 34, 3, 30` → `"9534330"`.
""",
        ),
        (
            "Follow-ups",
            """
- **Smallest concatenation** — flip the comparator; the zero guard becomes
  "strip leading zeros, but keep one digit".
- **Cost of `cmp_to_key`** — each comparison builds two strings of length `2d`,
  so the true bound is O(n log n · d), not O(n log n). With d ≤ 10 that is
  irrelevant here, but say it, because it is the difference between quoting a
  formula and understanding it.
- **Why not compare numerically?** `int(a + b)` works in Python and overflows
  everywhere else. The string comparison is the portable answer.
""",
        ),
    ],
}


def _compare(a: str, b: str) -> int:
    """Negative when `a` should come first — i.e. when a+b reads larger."""
    if a + b > b + a:
        return -1
    if a + b < b + a:
        return 1
    return 0


def largest_number(nums: list[int]) -> str:
    words = sorted((str(n) for n in nums), key=cmp_to_key(_compare))
    joined = "".join(words)
    if not joined:
        return ""
    # "00" must collapse to "0"; lstrip("0") would wrongly give "".
    return "0" if joined[0] == "0" else joined


CASES = [
    (([10, 2],), "210"),
    (([3, 30, 34, 5, 9],), "9534330"),
    (([121, 12],), "12121"),
    (([432, 43243],), "43243432"),
    (([0, 1, 0],), "100"),
    (([0, 0],), "0"),
    (([0],), "0"),
    (([],), ""),
]


def solve(nums: list[int]) -> str:
    return largest_number(nums)
