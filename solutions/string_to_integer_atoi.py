"""String to Integer (atoi) — LeetCode 8."""

from __future__ import annotations

META = {
    "pattern": "string-manipulation",
    "insight": "There is no algorithm here — write the four phases (space, sign, digits, clamp) as four separate blocks and none of them interact.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Parse a leading integer out of a string the way C's `atoi` does: skip leading
whitespace, take an optional single `+`/`-`, take digits until a non-digit,
ignore everything after, and clamp the result into signed 32-bit range.

The clarifying questions are the whole interview: does whitespace mean spaces
only (**yes**, `' '`, not `\\t` or `\\n`)? Is a lone `"+"` or `"-"` zero (yes)?
Are `"+-12"` and `"  +  413"` zero (yes — one sign, and no space after it)? Is
`"0032"` thirty-two (yes)? What about `"3.14"` (three)?
""",
        ),
        (
            "The insight",
            """
This is a **parsing spec**, not a puzzle, and the trap is trying to be clever.
Write four sequential phases over one cursor `i`, and never revisit an earlier
phase:

1. skip `' '`;
2. consume at most one sign;
3. accumulate digits with `value = value * 10 + d`;
4. clamp.

Because the phases are ordered and non-overlapping, `"+-12"` dies naturally:
phase 2 eats the `+`, phase 3 sees `-` which is not a digit, and the loop never
runs. Any single regex you write will be harder to defend than these four
blocks; if you do want one, `^[ ]*([+-]?\\d+)` is the honest version and you
should still be able to say what each phase does.

The Python-specific twist: `int` is unbounded, so **you must clamp yourself**.
In C the overflow is what you would detect; here the overflow never happens and
a forgotten clamp silently returns `91283472332`.
""",
        ),
        (
            "The clamp, and where to put it",
            """
Bounds are `[-2**31, 2**31 - 1]` = `[-2147483648, 2147483647]` — note they are
**asymmetric**, so clamping `abs(value)` to `2147483647` and then applying the
sign gets `"-2147483648"` wrong by one.

Clamp **inside** the digit loop, not after it. Deferring it works in Python but
in a language with fixed-width integers the accumulator has already wrapped by
then, and the interviewer is watching for exactly that. Returning early the
moment the running value crosses a bound is safe: more digits can only push it
further out.

Two more that catch people:

- `str.isdigit()` is **True** for `'²'` and other Unicode digit characters, and
  `int('²')` then raises. `'0' <= char <= '9'` is what you actually mean.
- `"  -0012a42"` → `-12`. Leading zeros after the sign are not an error.
""",
        ),
    ],
}

INT_MIN = -(2**31)
INT_MAX = 2**31 - 1


def my_atoi(s: str) -> int:
    i, n = 0, len(s)

    while i < n and s[i] == " ":  # phase 1: spaces only, not \t or \n
        i += 1

    sign = 1
    if i < n and s[i] in "+-":  # phase 2: at most one sign
        sign = -1 if s[i] == "-" else 1
        i += 1

    value = 0
    while i < n and "0" <= s[i] <= "9":  # phase 3: ASCII digits, not .isdigit()
        value = value * 10 + (ord(s[i]) - ord("0"))
        i += 1
        # phase 4, done early: further digits can only push further out of range
        if sign * value <= INT_MIN:
            return INT_MIN
        if sign * value >= INT_MAX:
            return INT_MAX

    return sign * value


CASES = [
    (("42",), 42),
    (("   -042",), -42),
    (("1337c0d3",), 1337),
    (("words and 987",), 0),
    (("-91283472332",), INT_MIN),
    (("2147483648",), INT_MAX),
    (("+-12",), 0),
    (("",), 0),
]


def solve(s: str) -> int:
    return my_atoi(s)
