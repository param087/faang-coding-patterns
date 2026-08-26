"""Valid Number — LeetCode 65."""

from __future__ import annotations

META = {
    "pattern": "string-manipulation",
    "insight": "Three flags — digit, dot, exponent — and reset the digit flag at 'e', because the exponent needs digits of its own.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Decide whether a string is a valid decimal or integer literal: an optional
sign, then digits with an optional decimal point (digits on at least one side),
then optionally `e`/`E` followed by an optional sign and **at least one** digit.

The grammar is the problem, so pin it down before writing anything. The four
that decide most interviews:

- `"4."` and `".9"` are **valid**; `"."` alone is not.
- `"46.e3"` is **valid** — the mantissa only needs a digit somewhere.
- `"1e"` and `"4e+"` are invalid; the exponent needs its own digit.
- `"99e2.5"` is invalid; the exponent must be an integer.

Also confirm no leading or trailing whitespace is allowed (on LC 65 it is not,
unlike the older version of this problem), and that `"Infinity"` and `"nan"`
are out of scope.
""",
        ),
        (
            "The insight",
            """
The wrong first answer is `float(s)` in a `try`. It accepts `"inf"`, `"nan"`,
`"1_0"` (PEP 515 underscores) and surrounding whitespace, and in an interview
it answers a different question than the one asked.

The second wrong answer is nested `if` blocks over positions — split at `e`,
then split at `.`, then check the sign — which is correct but grows to forty
lines and a bug in each corner.

The compact answer: **one left-to-right scan carrying three booleans** —
`seen_digit`, `seen_dot`, `seen_exponent` — and let each character type check
only its own local rule.

- digit → set `seen_digit`
- `+`/`-` → legal only at index 0 or immediately after `e`/`E`
- `.` → illegal if a dot or an exponent has already been seen
- `e`/`E` → illegal if an exponent was seen, or if **no digit** has been seen
  yet; then **reset `seen_digit` to False**
- anything else → reject

Return `seen_digit`. That last reset is the trick that makes the whole thing
work: after `e`, `seen_digit` no longer means "the mantissa had a digit", it
means "the exponent has a digit", and the same final return then validates both
halves. Without it, `"1e"` passes.
""",
        ),
        (
            "Pitfalls",
            """
- **`str.isdigit()` is not ASCII.** `"²".isdigit()` is `True`, and so is
  `"٣".isdigit()` (Arabic-Indic three); `int("²")` then raises. `isdecimal()`
  fixes the superscript but still accepts `"٣"`. Compare `"0" <= char <= "9"`
  and the class is exactly what you meant.
- **Sign position, not sign count.** `"--6"` and `"-+3"` are rejected because
  the character before the second sign is not `e`, not because a counter hit
  two. The positional rule also handles `"+"` alone and `"3-2"` for free.
- **Empty string** returns `False` through `seen_digit` being `False` — no
  special case needed, but do run it.
- **State machine follow-up.** The interviewer may ask for an explicit DFA: 8
  or 9 states with a transition table, which is what a real lexer uses and what
  you would extend to hex or underscores. The flag version is that DFA with the
  state compressed into three bits — worth saying, because it shows the two are
  the same answer rather than a shortcut.
""",
        ),
    ],
}


def is_number(s: str) -> bool:
    seen_digit = False
    seen_dot = False
    seen_exponent = False

    for i, char in enumerate(s):
        if "0" <= char <= "9":  # not isdigit(): that accepts "²" and "٣"
            seen_digit = True
        elif char in "+-":
            # A sign is legal only at index 0 or immediately after e/E.
            if i > 0 and s[i - 1] not in "eE":
                return False
        elif char == ".":
            if seen_dot or seen_exponent:  # exponents are integers
                return False
            seen_dot = True
        elif char in "eE":
            if seen_exponent or not seen_digit:
                return False
            seen_exponent = True
            seen_digit = False  # the exponent must supply its own digit
        else:
            return False

    return seen_digit


CASES = [
    (("0089",), True),
    ((".9",), True),
    (("46.e3",), True),
    (("+6e-1",), True),
    (("",), False),
    ((".",), False),
    (("4e+",), False),
    (("99e2.5",), False),
]


def solve(s: str) -> bool:
    return is_number(s)
