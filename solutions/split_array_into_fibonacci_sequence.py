"""Split Array into Fibonacci Sequence — LeetCode 842."""

from __future__ import annotations

META = {
    "pattern": "backtracking",
    "insight": "Only the first two terms are free choices — every later one is forced, so the search is over O(n²) starting pairs, not 3ⁿ splits.",
    "time": "O(n³) worst case — O(n²) starting pairs, O(n) work to verify each chain",
    "space": "O(n) for the recursion and the output",
    "sections": [
        (
            "What it asks",
            """
Split a string of digits into a sequence of at least three integers where every
term is the sum of the previous two. No leading zeros, every value must fit in a
signed 32-bit integer, and any valid split is accepted. Return `[]` if none
exists.

Two rules that look decorative and are not: a lone `"0"` is a legal term while
`"01"` is not, and the `2³¹ − 1` ceiling is a real constraint, not flavour —
LeetCode's stress case is a 57-digit string whose only near-misses overflow.

Ask whether the answer must be *the* split or *a* split. It is any one, which is
why the code returns on the first success instead of collecting.
""",
        ),
        (
            "The insight",
            """
The branching looks like 3ⁿ. It is not, and seeing why is the whole interview.

Once you have fixed the first two terms, **every remaining term is determined**:
it must equal `a + b`, so there is exactly one candidate string to match against
the input, and either it is there or the branch is dead. So the real search is
over starting pairs — O(n²) of them — with an O(n) deterministic verification
each. O(n³) in the worst case, and far less in practice because most pairs die
at the third term.

In the recursion that becomes three guards inside one loop over the piece length:

- **`if value > expected: break`.** The piece only grows as `end` advances, so
  once it overshoots `a + b` no longer piece can help.
- **`if value < expected: continue`.** Keep extending; the match may be a few
  digits further along.
- **`if value > 2³¹ − 1: break`.** Same monotonicity. Without this the 57-digit
  case builds unbounded Python integers and burns time on chains that can never
  be valid — Python will not overflow for you, which is precisely why this rule
  is in the problem.

Leading zeros: if `num[start] == "0"`, the only legal piece is the single
character `"0"`, so break as soon as the piece is longer than one.
""",
        ),
        (
            "Edge cases",
            """
- **`"0000"` → `[0, 0, 0, 0]`.** Zero is a legal term and `0 + 0 = 0`, so the
  whole string splits. A leading-zero check written as "reject any piece starting
  with `0`" returns `[]` here and is wrong.
- **`"0123"` → `[]`.** The first term must be `0`, then `1`, then `1` — but the
  next character is `2`. Nothing to fall back on.
- **`"1101111"` → `[11, 0, 11, 11]`.** Also `[110, 1, 111]`. Both are accepted;
  if a grader compares exactly, it is comparing against whichever your traversal
  finds first, so pick a deterministic order — shortest prefix first — and say so.
- **Fewer than three terms** is not a sequence. `"1213"` splits arithmetically
  nowhere, and `"11"` is too short to try. The length check belongs at the
  success branch, not at the top.
- **`"539834657215398346785398346991079669377161950407626991942"` → `[]`.** The
  32-bit ceiling is the only thing that rejects it, and it is why the overflow
  guard is a correctness rule rather than an optimisation.
""",
        ),
    ],
}

LIMIT = 2**31 - 1  # values must fit in a signed 32-bit integer


def split_into_fibonacci(num: str) -> list[int]:
    n = len(num)
    path: list[int] = []

    def explore(start: int) -> bool:
        if start == n:
            return len(path) >= 3  # a sequence needs at least three terms

        value = 0
        for end in range(start, n):
            if num[start] == "0" and end > start:
                break  # "0" is legal, "0X" never is
            value = value * 10 + int(num[end])
            if value > LIMIT:
                break  # longer pieces are only larger

            if len(path) >= 2:
                expected = path[-1] + path[-2]
                if value > expected:
                    break  # overshot, and it only grows from here
                if value < expected:
                    continue  # keep extending the piece

            path.append(value)  # choose
            if explore(end + 1):  # explore
                return True
            path.pop()  # un-choose

        return False

    return path if explore(0) else []


CASES = [
    (("1101111",), [11, 0, 11, 11]),  # [110, 1, 111] is equally valid
    (("11235813",), [1, 1, 2, 3, 5, 8, 13]),
    (("123456579",), [123, 456, 579]),
    (("112358130",), []),  # the trailing 0 cannot extend 13, 21
    (("0000",), [0, 0, 0, 0]),  # a lone zero is a legal term
    (("0123",), []),  # 0, 1, 1 — but the string says 2
    (("1213",), []),
    # 57 digits; every chain either mismatches or exceeds 2^31 - 1.
    (("539834657215398346785398346991079669377161950407626991942",), []),
]


def solve(num: str) -> list[int]:
    return split_into_fibonacci(num)


def check() -> None:
    for args, expected in CASES:
        assert solve(*args) == expected

    # Any valid split is accepted, so verify the properties rather than the shape.
    for (num,), expected in CASES:
        if not expected:
            continue
        assert "".join(str(value) for value in expected) == num
        assert len(expected) >= 3
        assert all(value <= LIMIT for value in expected)
        triples = zip(expected, expected[1:], expected[2:], strict=False)
        assert all(a + b == c for a, b, c in triples)
