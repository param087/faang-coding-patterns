"""Remove K Digits — LeetCode 402."""

from __future__ import annotations

META = {
    "pattern": "stack",
    "insight": "Scanning left to right, a digit is worth deleting exactly when the digit after it is smaller — the leftmost such drop costs the most.",
    "time": "O(n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Delete exactly `k` digits from a numeric string so the remaining digits, in
their original order, form the smallest possible number. Return it as a string
with no leading zeros, and `"0"` if everything is gone.

Ask two things: **must exactly `k` be removed, or at most `k`?** (Exactly — and
that changes the ending.) And **is the input guaranteed digits only, no sign?**
(Yes on LeetCode; a sign would flip the whole comparison.)
""",
        ),
        (
            "The insight",
            """
Length is fixed at `n - k`, so the comparison is purely lexicographic and the
**leftmost** position dominates: fixing digit 0 is worth more than every later
digit combined.

That gives a local rule. Walking left to right, if the current digit is smaller
than the one before it, deleting that predecessor shrinks a more significant
place — always a win, always take it. So the kept digits must end up
**non-decreasing** as far as the budget allows, which is a monotonic stack:

```
for digit in num:
    while stack and k and stack[-1] > digit:
        stack.pop(); k -= 1
    stack.append(digit)
```

Each digit is pushed once and popped at most once, so the nested `while` is
amortised O(n), not O(nk). Greedy is safe here because a pop is never regretted:
the digit it uncovers is smaller, so any later arrangement is still improved.

The wrong first answer is "remove the `k` largest digits". `"112"`, `k = 1` has
no large digit to remove, and `"1432219"`, `k = 3` needs the `4` gone but keeps
the `9` — position beats magnitude.
""",
        ),
        (
            "The three endings that break it",
            """
The stack loop is four lines; the bugs are all after it.

1. **Leftover `k`.** If the input is already non-decreasing — `"112"`, `k = 1` —
   nothing ever pops and the budget is untouched. Removal is mandatory, so trim
   the last `k` digits: the tail is the least significant place. `stack[:-k]`
   only when `k > 0`, because `stack[:-0]` is the empty list.
2. **Leading zeros.** `"10200"`, `k = 1` leaves `"0200"`. Strip with `lstrip`,
   not by deleting one character — `"10001"`, `k = 4` leaves three of them.
3. **Empty result.** `"10"`, `k = 2` deletes everything; the answer is `"0"`,
   not `""`.

Related: **Remove Duplicate Letters** (316) and **Smallest Subsequence of
Distinct Characters** (1081) are the same loop with a "can I still see this
character later?" guard replacing the `k` budget.
""",
        ),
    ],
}


def remove_k_digits(num: str, k: int) -> str:
    stack: list[str] = []

    for digit in num:
        # A smaller digit arriving makes the larger one above it deletable.
        while stack and k > 0 and stack[-1] > digit:
            stack.pop()
            k -= 1
        stack.append(digit)

    # Already non-decreasing: nothing popped, so spend the rest on the tail.
    if k > 0:
        stack = stack[:-k]

    return "".join(stack).lstrip("0") or "0"


CASES = [
    (("1432219", 3), "1219"),
    (("10200", 1), "200"),  # leading zero must be stripped
    (("10", 2), "0"),  # everything removed
    (("112", 1), "11"),  # non-decreasing: budget spent on the tail
    (("10001", 4), "0"),  # several leading zeros at once
    (("9", 1), "0"),
    (("1234567890", 9), "0"),
    (("5337", 2), "33"),
]


def solve(num: str, k: int) -> str:
    return remove_k_digits(num, k)
