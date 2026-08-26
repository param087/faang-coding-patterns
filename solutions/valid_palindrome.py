"""Valid Palindrome — LeetCode 125."""

from __future__ import annotations

META = {
    "pattern": "two-pointers",
    "insight": "Filter lazily instead of eagerly: skip junk with the pointers themselves and the O(n) copy disappears.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Decide whether a string reads the same forwards and backwards once you ignore
everything that is not a letter or a digit, and treat case as irrelevant.

The clarifying question that matters: **what counts as alphanumeric?** Digits
are included — that is easy to miss, and `"0P"` is the test that catches it.
Ask about Unicode too; `str.isalnum()` says `True` for `"é"` and `"٣"`, which
may or may not be what the interviewer wants.
""",
        ),
        (
            "The insight",
            """
The one-liner everyone writes first is:

```python
clean = [c.lower() for c in s if c.isalnum()]
return clean == clean[::-1]
```

That is correct and it is a fine thing to say out loud — but it builds two
extra strings, so it is O(n) space. The interviewer's real question is the
O(1)-space version.

Run two pointers inwards and **filter lazily**: each pointer advances over
junk until it lands on something alphanumeric, then the two are compared. No
copy, no reversal, one pass.
""",
        ),
        (
            "Edge cases",
            """
- **`""` and `" "` are palindromes.** Both collapse to nothing, and the loop
  never runs. Answer `True`.
- **`"0P"` is not.** Both characters are alphanumeric, so nothing is skipped;
  `'0'` vs `'p'` differ. Anyone who compared with ASCII arithmetic (`ord(a) -
  ord(b) == 32`) gets this wrong, because `'0'` and `'P'` are exactly 32 apart.
- **The inner skip loops need `left < right`**, or a string of pure punctuation
  walks off the end.
- `.lower()` on a digit is a no-op, so there is no need to branch on it.
""",
        ),
    ],
}


def is_palindrome(s: str) -> bool:
    left, right = 0, len(s) - 1

    while left < right:
        while left < right and not s[left].isalnum():
            left += 1
        while left < right and not s[right].isalnum():
            right -= 1
        if s[left].lower() != s[right].lower():
            return False
        left += 1
        right -= 1

    return True


CASES = [
    (("A man, a plan, a canal: Panama",), True),
    (("race a car",), False),
    (("",), True),
    ((" ",), True),
    ((".,",), True),
    (("0P",), False),  # both alphanumeric; ASCII-offset comparisons fail here
    (("Ab_a",), True),
    (("12321",), True),
]


def solve(s: str) -> bool:
    return is_palindrome(s)
