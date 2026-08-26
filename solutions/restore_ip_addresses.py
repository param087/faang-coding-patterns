"""Restore IP Addresses — LeetCode 93."""

from __future__ import annotations

META = {
    "pattern": "backtracking",
    "insight": "Four segments of one to three digits each — so the search is at most 3⁴ = 81 splits, and the whole problem is the validity rules.",
    "time": "O(1) — at most 3⁴ = 81 splits, each O(n) to join",
    "space": "O(1) beyond the output",
    "sections": [
        (
            "What it asks",
            """
Insert three dots into a digit string so it reads as a valid IPv4 address, and
return every way to do it. Each of the four segments must be `0`–`255` with no
leading zeros.

Ask what "no leading zeros" means for `"0"` — a lone zero is legal, `"01"` is
not. That single rule is what most wrong answers get wrong, and the string
`"010010"` is the case that exposes it.

Ask whether the input can contain non-digits. LeetCode says digits only; if not,
you need a guard, since `int(piece)` on `"+1"` succeeds and lies to you.
""",
        ),
        (
            "The insight",
            """
This looks like a search problem and is really a **bounded enumeration**. Four
segments, each one to three characters, so at most 3⁴ = **81** candidate splits
regardless of input length. Nothing here is exponential and saying so up front
is worth marks: the interviewer is watching for whether you notice that `n ≤ 12`
is not a coincidence.

So the code is the standard choose / explore / un-choose skeleton with the
interesting parts in the guards:

- **Length prune.** With `needed` segments left and `remaining` characters, bail
  if `remaining < needed` (can't fill) or `remaining > 3 * needed` (can't
  consume). This is what turns a 3000-character input into an instant `[]`.
- **`break`, not `continue`, on a leading zero.** If a one-character piece
  starts with `0`, every longer piece from the same index also starts with `0`,
  so the whole rest of the loop is dead.
- **`break` on `> 255` too**, for the same reason: extending the piece only
  makes the number larger.

Both breaks are the difference between an enumeration that reasons and one that
tests 81 candidates and filters.
""",
        ),
        (
            "The cases that decide it",
            """
- `"010010"` → `["0.10.0.10", "0.100.1.0"]`. A solution that only rejects pieces
  whose integer value round-trips differently, or that checks `piece != "0"`
  clumsily, drops one of these.
- `"0000"` → `["0.0.0.0"]` and nothing else. Not `[]`, and not four ways.
- `"25525511135"` → two answers, `"255.255.11.135"` and `"255.255.111.35"`.
  Getting only one usually means the loop stops at the first success.
- `"1111111111111"` (13 digits) → `[]`, caught by the length prune before any
  recursion.

Stated as a predicate, a piece is valid iff `len(piece) == 1` **or**
(`piece[0] != "0"` and `int(piece) <= 255`). The loop below encodes exactly that
but turns each failure into a `break`, because both failure modes are monotone
in the piece length — say that sentence out loud when you write the breaks, or
they read as a bug.
""",
        ),
    ],
}


def restore_ip_addresses(s: str) -> list[str]:
    result: list[str] = []
    parts: list[str] = []
    n = len(s)

    def explore(start: int) -> None:
        needed = 4 - len(parts)
        remaining = n - start

        if needed == 0:
            if remaining == 0:
                result.append(".".join(parts))
            return
        # Too few characters to fill the rest, or too many to consume.
        if remaining < needed or remaining > 3 * needed:
            return

        for length in (1, 2, 3):
            if start + length > n:
                break
            piece = s[start : start + length]
            if piece[0] == "0" and length > 1:
                break  # every longer piece also has the leading zero
            if int(piece) > 255:
                break  # every longer piece is larger still
            parts.append(piece)
            explore(start + length)
            parts.pop()

    explore(0)
    return result


CASES = [
    (("25525511135",), ["255.255.11.135", "255.255.111.35"]),
    # A lone "0" is legal; "00" is not.
    (("0000",), ["0.0.0.0"]),
    (
        ("101023",),
        ["1.0.10.23", "1.0.102.3", "10.1.0.23", "10.10.2.3", "101.0.2.3"],
    ),
    # The leading-zero case that catches sloppy validation.
    (("010010",), ["0.10.0.10", "0.100.1.0"]),
    (("111111111111",), ["111.111.111.111"]),
    (("1111111111111",), []),  # 13 digits — pruned before any recursion
    (("1",), []),
    (("",), []),
]


def solve(s: str) -> list[str]:
    return restore_ip_addresses(s)
