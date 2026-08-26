"""Expression Add Operators — LeetCode 282."""

from __future__ import annotations

META = {
    "pattern": "string-manipulation",
    "insight": "Carry the last operand so '*' can undo its own additive contribution: value - previous + previous * operand.",
    "time": "O(4^n · n) — three operators or a join at each of the n-1 gaps, times the string build",
    "space": "O(n) recursion depth, plus the output",
    "sections": [
        (
            "What it asks",
            """
Given a digit string and a target, insert `+`, `-` or `*` (or nothing, joining
digits into a multi-digit operand) between the digits so that the expression
evaluates to the target. Return **every** such expression. Order is free.

Constraints matter here: `num` is at most 10 digits, which is what makes an
exponential search acceptable. 4⁹ ≈ 262 000 leaves — trivial. Confirm there is
no unary minus (the first character never gets an operator) and that all
results must be returned, not counted.
""",
        ),
        (
            "The insight",
            """
The enumeration is easy — at each gap, pick one of four choices. The problem is
that you cannot evaluate as you go, because `*` binds tighter than the `+` you
already committed to. Having built `2 + 3` and holding the running value `5`,
reading `* 2` next must produce `8`, not `10`.

The standard fix is to build every expression string and evaluate it at the
leaf. That is a whole second parser and it re-reads the prefix at every leaf.

The real fix is one extra parameter: **`previous`, the signed value of the last
operand folded into `value`**. Then `*` is exact arithmetic:

```
value - previous + previous * operand
```

Subtract what the last operand contributed, put it back multiplied. The new
`previous` becomes `previous * operand`, so chains like `2 + 3 * 4 * 5` keep
working — each `*` undoes the *accumulated* product, not just the last factor.

The signs fall out too: after `-`, `previous` is `-operand`, so
`1 - 2 * 3` computes `-1 - (-2) + (-2 · 3)` = `-5`. Correct, with no separate
sign bookkeeping.
""",
        ),
        (
            "Leading zeros, and `break` not `continue`",
            """
`"05"` is not a legal operand, so any prefix longer than one character that
starts with `"0"` is rejected. Two details:

- Bare `"0"` **is** legal. The test is `len(operand) > 1 and operand[0] == "0"`,
  not `operand[0] == "0"`.
- Use `break`, not `continue`. Once the current operand starts with `0`, every
  *longer* prefix from the same start also starts with `0`, so continuing the
  loop only enumerates more rejects. `"105"` with target 5 is the case that
  exercises it: `"1*0+5"` and `"10-5"` are the answers, and `"1*05"` must never
  be generated.

Two more worth naming:

- **The first operand takes no operator.** Guard on `start == 0`, otherwise you
  emit `"+123"`.
- **Overflow.** Python has arbitrary-precision integers, so this is free here —
  but in Java or C++ the intermediate products on a 10-digit input blow past
  32 bits and you need `long` plus an early cutoff. If the interview language
  is not Python, say this before they ask.

Follow-up: if only the **count** were required, this is still exponential —
there is no DP over positions, because the reachable value set is unbounded.
""",
        ),
    ],
}


def add_operators(num: str, target: int) -> list[str]:
    results: list[str] = []
    n = len(num)

    def backtrack(start: int, expression: str, value: int, previous: int) -> None:
        if start == n:
            if value == target:
                results.append(expression)
            return

        for end in range(start + 1, n + 1):
            operand_text = num[start:end]
            if len(operand_text) > 1 and operand_text[0] == "0":
                break  # every longer prefix also has a leading zero
            operand = int(operand_text)

            if start == 0:
                backtrack(end, operand_text, operand, operand)  # no leading operator
                continue

            backtrack(end, f"{expression}+{operand_text}", value + operand, operand)
            backtrack(end, f"{expression}-{operand_text}", value - operand, -operand)
            # Undo the last operand's additive contribution, re-add it multiplied.
            backtrack(
                end,
                f"{expression}*{operand_text}",
                value - previous + previous * operand,
                previous * operand,
            )

    if n:
        backtrack(0, "", 0, 0)
    return results


CASES = [
    (("123", 6), ["1*2*3", "1+2+3"]),
    (("232", 8), ["2*3+2", "2+3*2"]),
    (("105", 5), ["1*0+5", "10-5"]),
    (("00", 0), ["0*0", "0+0", "0-0"]),
    (("123", 15), ["12+3"]),
    (("99", 9), []),
    (("3456237490", 9191), []),
    (("1", 1), ["1"]),
]


def solve(num: str, target: int) -> list[str]:
    # Any order is accepted; sort so the cases are deterministic.
    return sorted(add_operators(num, target))
