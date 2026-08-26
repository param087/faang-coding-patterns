"""Generate Parentheses — LeetCode 22."""

from __future__ import annotations

META = {
    "pattern": "backtracking",
    "insight": "Build only valid strings: open a bracket while any remain, close one only while closes trail opens.",
    "time": "O(4ⁿ / √n) — the nth Catalan number, times O(n) to emit each string",
    "space": "O(n) recursion depth, excluding the output",
    "sections": [
        (
            "What it asks",
            """
All well-formed strings of `n` pairs of parentheses. `n = 3` gives five:
`((()))`, `(()())`, `(())()`, `()(())`, `()()()`.

There is nothing to clarify about the statement, which is a signal in itself:
the interviewer wants to watch you decide **where the validity check lives**.
""",
        ),
        (
            "The insight",
            """
The obvious plan — enumerate all 2^(2n) strings over `{(, )}` and keep the
balanced ones — is generate-and-test. At n = 8 that is 65 536 candidates for
1430 answers, and at n = 12 it is 16.7 million for 208 012. You are throwing
away 98% of the work.

Instead make invalid strings **unreachable**. Carry two counters and let them
gate the two choices:

- add `(` while `open < n` — you have brackets left to spend;
- add `)` while `close < open` — there is something open to close.

Those two conditions are exactly the definition of a balanced string built left
to right: the running prefix never has more closes than opens, and the totals
match at the end. Every leaf is therefore valid by construction, and there is
no validity check anywhere in the code — the pruning *is* the check.

The number of leaves is the nth Catalan number, C(n) = (2n)! / (n!(n+1)!), which
is Θ(4ⁿ / n^1.5); multiply by the O(n) string build for the stated bound.
Quoting Catalan by name is worth doing — it is the same count as distinct BSTs
of n nodes and as full binary trees with n internal nodes, and interviewers
like the connection.
""",
        ),
        (
            "Where the wrong versions go wrong",
            """
Three failure modes, in the order they show up:

- **`close < n` instead of `close < open`.** Produces `)(` — balanced by count,
  invalid by prefix. The condition must reference `open`, not `n`.
- **Validating at the leaf.** Correct, but it is generate-and-test wearing a
  recursion costume; the whole point is that the invariant is maintained on the
  way down.
- **Appending the mutable buffer.** `result.append(path)` instead of
  `"".join(path)` (or a string parameter) stores an alias that the next `pop()`
  edits. Strings are immutable, so carrying `path: str` and passing
  `path + "("` sidesteps the bug entirely, at the cost of O(n) copies per call —
  a fair trade at these sizes, and worth naming as a trade rather than a
  freebie.

Edge case: `n = 0` returns `[""]` under this recursion, since the empty string
is vacuously balanced. LeetCode constrains `n ≥ 1` so it is never tested;
state the convention rather than letting the interviewer wonder.
""",
        ),
    ],
}


def generate_parenthesis(n: int) -> list[str]:
    result: list[str] = []

    def explore(path: str, opened: int, closed: int) -> None:
        if len(path) == 2 * n:
            result.append(path)
            return
        if opened < n:  # brackets left to spend
            explore(path + "(", opened + 1, closed)
        if closed < opened:  # something is open to close
            explore(path + ")", opened, closed + 1)

    explore("", 0, 0)
    return result


CASES = [
    ((3,), ["((()))", "(()())", "(())()", "()(())", "()()()"]),
    ((1,), ["()"]),
    ((2,), ["(())", "()()"]),
    ((0,), [""]),
]


def solve(n: int) -> list[str]:
    return generate_parenthesis(n)


def _is_balanced(s: str) -> bool:
    depth = 0
    for character in s:
        depth += 1 if character == "(" else -1
        if depth < 0:
            return False
    return depth == 0


def check() -> None:
    for args, expected in CASES:
        assert generate_parenthesis(*args) == expected

    # The answer count is Catalan: 1, 1, 2, 5, 14, 42, 132, 429.
    catalan = [1, 1, 2, 5, 14, 42, 132, 429]
    for n, expected_count in enumerate(catalan):
        produced = generate_parenthesis(n)
        assert len(produced) == expected_count, (n, len(produced))
        assert len(set(produced)) == expected_count  # no repeats
        assert all(_is_balanced(s) and len(s) == 2 * n for s in produced)
