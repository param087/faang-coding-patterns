"""Letter Combinations of a Phone Number — LeetCode 17."""

from __future__ import annotations

META = {
    "pattern": "backtracking",
    "insight": "A fixed-depth Cartesian product: depth is the digit index, so there is no `start` and no pruning — only the empty-input special case.",
    "time": "O(n · 4ⁿ) — up to 4ⁿ strings, each O(n) to build",
    "space": "O(n) recursion depth, excluding the output",
    "sections": [
        (
            "What it asks",
            """
Map digits 2–9 to their keypad letters and return every string formed by
picking one letter per digit. Any order.

Two things to nail down: **1, 0, `*` and `#` do not appear** (LeetCode
guarantees 2–9 only, but ask — otherwise you need a policy for a digit with no
letters), and the empty string returns `[]`, **not** `[""]`.
""",
        ),
        (
            "The insight",
            """
This is not a search, it is a Cartesian product with a fixed depth. Every leaf
at depth `n` is an answer and no branch is ever invalid, so the "backtracking"
skeleton degenerates: there is no `start` index, no `used` set, no pruning
condition. The only decision is which letter of `digits[index]` to take next.

That makes the size exact and worth stating: 7 and 9 have four letters, the
rest have three, so the answer count is 3^a · 4^b, bounded by 4ⁿ. With
`n ≤ 4` the worst case — `"7799"` — is 256 strings. There is no faster
algorithm because the output itself is that big; the complexity is
output-bound, and saying so pre-empts the "can you do better" question.

The iterative version is worth having in your pocket: start from `[""]` and, for
each digit, replace the list with `[p + c for p in partial for c in letters]`.
Same work, no recursion, and it makes the product structure obvious.
""",
        ),
        (
            "The empty-input trap",
            """
`digits = ""` must give `[]`. The recursion, left alone, hits `index == 0 ==
len(digits)` immediately and records the empty path, returning `[""]` — one
element where zero are wanted. The iterative build has exactly the same bug
from the other direction: it starts at `[""]` and never enters the loop.

Guard it explicitly at the top. It is the single most common wrong submission
on this problem, it is the first hidden test case, and it costs one line.

Two smaller ones from the same family: build the digit→letters map as a
constant rather than deriving it from arithmetic on `ord`, because 7 and 9
break the three-letters-per-digit pattern; and append `"".join(path)` (or carry
a string through the recursion) rather than the mutable list itself, for the
same aliasing reason as every other backtracking problem.
""",
        ),
    ],
}

KEYPAD = {
    "2": "abc",
    "3": "def",
    "4": "ghi",
    "5": "jkl",
    "6": "mno",
    "7": "pqrs",
    "8": "tuv",
    "9": "wxyz",
}


def letter_combinations(digits: str) -> list[str]:
    if not digits:
        return []  # the trap: not [""]

    result: list[str] = []
    path: list[str] = []

    def explore(index: int) -> None:
        if index == len(digits):
            result.append("".join(path))
            return
        for letter in KEYPAD[digits[index]]:
            path.append(letter)
            explore(index + 1)
            path.pop()

    explore(0)
    return result


def letter_combinations_iterative(digits: str) -> list[str]:
    """The same Cartesian product, built layer by layer."""
    if not digits:
        return []
    partial = [""]
    for digit in digits:
        partial = [prefix + letter for prefix in partial for letter in KEYPAD[digit]]
    return partial


CASES = [
    (("23",), ["ad", "ae", "af", "bd", "be", "bf", "cd", "ce", "cf"]),
    (("",), []),
    (("2",), ["a", "b", "c"]),
    (("9",), ["w", "x", "y", "z"]),
    (
        ("79",),
        [
            "pw", "px", "py", "pz",
            "qw", "qx", "qy", "qz",
            "rw", "rx", "ry", "rz",
            "sw", "sx", "sy", "sz",
        ],
    ),
]


def solve(digits: str) -> list[str]:
    return letter_combinations(digits)


def check() -> None:
    for args, expected in CASES:
        assert letter_combinations(*args) == expected
        assert letter_combinations_iterative(*args) == expected

    # Output size is 3^(digits with three letters) x 4^(7s and 9s).
    assert len(letter_combinations("234")) == 27
    assert len(letter_combinations("7799")) == 256
    assert len(letter_combinations("2379")) == 144
