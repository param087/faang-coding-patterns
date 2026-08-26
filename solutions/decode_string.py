"""Decode String — LeetCode 394."""

from __future__ import annotations

META = {
    "pattern": "string-manipulation",
    "insight": "A '[' suspends the string you were building; push it with its repeat count and the ']' resumes exactly where you left off.",
    "time": "O(L) where L is the length of the decoded output",
    "space": "O(L)",
    "sections": [
        (
            "What it asks",
            """
Expand a string encoded as `k[encoded]`, where the bracketed part repeats `k`
times and the encodings nest: `3[a2[c]]` → `accaccacc`.

Ask three things before writing anything:

- Is the input guaranteed **well formed** (LeetCode says yes — no stray
  brackets, every `k` followed by `[`)? This decides whether you need error
  handling, which is most of the code if the answer is no.
- Can `k` be **multi-digit**? Yes, up to 300 — so `10[a]` is ten `a`s, not one
  `a` after a `1` and a `0`.
- Can digits appear **outside** a repeat count, as literal characters? No. If
  they could, the grammar becomes ambiguous and you would need a delimiter.
""",
        ),
        (
            "What actually costs, and it is not the parse",
            """
The input is tiny — LeetCode caps it at 30 characters. The **output** is not:
with `k ≤ 300` and three levels of nesting, `300[300[300[a]]]` expands to
`2.7 × 10⁷` characters. So any solution is `Ω(L)` in the output length, and the
only thing you can get wrong is doing more than one pass over it.

The naive version does exactly that: repeatedly find the innermost `k[...]`,
expand it, restart. Each pass is `O(L)` and there is one pass per nesting
level, so it is `O(d · L)` — plus, in Python, a full string rebuild each time.
The stack does it in a single left-to-right pass.

The other real cost is `current += char` inside a loop. On CPython that is
usually amortised, but if you are asked to defend it, accumulate into a list
and `"".join` at each `]`.
""",
        ),
        (
            "The insight",
            """
Read left to right and keep exactly one "string being built". A `[` means
**suspend** it: the text so far is not going anywhere, but the next stretch of
characters belongs to a repeat group. So push the suspended text together with
its repeat count, and start a fresh empty string.

A `]` means **resume**: pop the suspended text and the count, multiply out what
you just built, and glue it on.

```python
stack.append((current, count))    # on '['
previous, repeat = stack.pop()    # on ']'
current = previous + current * repeat
```

That is the entire algorithm, and the stack is doing precisely what a
recursive descent parser's call stack would do — which is the honest answer to
"could you do this recursively?" Yes, and it is the same shape: a helper that
consumes up to the matching `]` and returns both the decoded chunk **and** the
cursor. The stack version avoids having to thread that cursor back out, which
is where the recursive version usually breaks.
""",
        ),
        (
            "What exactly goes on the stack",
            """
Push **both** the prefix and the count, as a pair. Pushing only the count is
the classic bug: `abc3[cd]xyz` loses the `abc`, because when the `]` fires the
`current` you are holding is `cd` and the `abc` has nowhere to come back from.

The count is accumulated the same way as in every parser —
`count = count * 10 + int(char)` — and **reset to 0** at the `[`, not at the
`]`. Leaving it set means `2[a]3[b]` reads the second count as 23.

Note also what a `]` does *not* do: it does not touch `count`. By then the
count for that group has long been consumed and zeroed.
""",
        ),
        (
            "Dry run",
            """
`3[a2[c]]`

| char | current | count | stack |
| --- | --- | --- | --- |
| `3` | `""` | 3 | `[]` |
| `[` | `""` | 0 | `[("", 3)]` |
| `a` | `"a"` | 0 | `[("", 3)]` |
| `2` | `"a"` | 2 | `[("", 3)]` |
| `[` | `""` | 0 | `[("", 3), ("a", 2)]` |
| `c` | `"c"` | 0 | `[("", 3), ("a", 2)]` |
| `]` | `"acc"` | 0 | `[("", 3)]` |
| `]` | `"accaccacc"` | 0 | `[]` |

The row that matters is the first `]`: `current` becomes `"a" + "c" * 2`, so
the prefix `a` survives because it was pushed, not because of anything the
inner group did.

Then run `abc3[cd]xyz` → `abccdcdcdxyz`, which exercises text on **both** sides
of a group. If your version drops the `abc`, this is where it shows.
""",
        ),
        (
            "Follow-ups",
            """
- **Malformed input** — unmatched `]` (empty stack on pop), unmatched `[`
  (non-empty stack at the end), a `k` with no bracket. Each is one line, and
  naming them unprompted is the difference between "solved it" and "would ship
  it".
- **`k = 0`** — `0[abc]` should give `""`. The code already does; `"abc" * 0`
  is `""`. Worth stating out loud rather than testing silently.
- **Number of Atoms** (LeetCode 726) is this problem with chemistry: same
  stack, but the payload is a counter per element instead of a string, and the
  multiplier applies to every count in the popped frame.
- **Basic Calculator** (224) is the same skeleton again — push the pending
  result and sign at `(`, restore at `)`.
- **Encode**, i.e. produce the shortest `k[...]` form of a string, is a
  completely different (and much harder) interval-DP problem — LeetCode 471.
""",
        ),
    ],
}


def decode_string(s: str) -> str:
    stack: list[tuple[str, int]] = []  # (text built before '[', its repeat count)
    current = ""
    count = 0

    for char in s:
        if char.isdigit():
            count = count * 10 + int(char)  # multi-digit k
        elif char == "[":
            stack.append((current, count))  # suspend: push the prefix too
            current, count = "", 0
        elif char == "]":
            previous, repeat = stack.pop()  # resume where we left off
            current = previous + current * repeat
        else:
            current += char

    return current


CASES = [
    (("3[a]2[bc]",), "aaabcbc"),
    (("3[a2[c]]",), "accaccacc"),
    (("2[abc]3[cd]ef",), "abcabccdcdcdef"),
    (("abc3[cd]xyz",), "abccdcdcdxyz"),
    (("10[a]",), "a" * 10),
    (("2[2[2[a]]]",), "a" * 8),
    (("xyz",), "xyz"),
    (("",), ""),
]


def solve(s: str) -> str:
    return decode_string(s)
