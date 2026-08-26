"""UTF-8 Validation — LeetCode 393."""

from __future__ import annotations

META = {
    "pattern": "bit-manipulation",
    "insight": "A leading byte's high bits announce how many continuation bytes follow; carry that count and check every follower is 10xxxxxx.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Given a list of integers where only the low 8 bits of each matter, decide
whether the sequence is a valid UTF-8 encoding.

The encoding rules you need, and it is fair to write them on the board before
coding:

```
1 byte   0xxxxxxx
2 bytes  110xxxxx 10xxxxxx
3 bytes  1110xxxx 10xxxxxx 10xxxxxx
4 bytes  11110xxx 10xxxxxx 10xxxxxx 10xxxxxx
```

Ask whether entries can exceed 255. LeetCode caps them at 255, but the original
statement says "only the least significant 8 bits are used", so mask with
`& 0xFF` and the question stops mattering.
""",
        ),
        (
            "The insight",
            """
This is a two-state scanner, not a bit puzzle. The only state you carry is
`remaining`: how many continuation bytes are still owed.

- `remaining > 0` — this byte **must** match `10xxxxxx`, i.e. `byte >> 6 == 0b10`.
  Decrement and move on.
- `remaining == 0` — this is a leading byte. Count its leading ones: 0 means
  ASCII, 2/3/4 set `remaining` to 1/2/3. Anything else (a lone `10xxxxxx`, or
  five leading ones) is invalid immediately.

Test the leading byte by shifting, not by masking against a table:
`byte >> 5 == 0b110`, `byte >> 4 == 0b1110`, `byte >> 3 == 0b11110`. Each of
those pins down *all* the bits above the payload in one comparison, which is
why the order of the branches does not matter and why `11111000` cannot slip
through the 4-byte test.

At the end, `remaining` must be **0**. Forgetting that final check is the
single most common bug here — it accepts a stream that ends mid-character.
""",
        ),
        (
            "Edge cases",
            """
- `[]` — vacuously valid, and the `remaining == 0` return gives it.
- `[128]` — `10000000` with nothing owed: a continuation byte with no leader.
  Must be rejected, and the shift ladder rejects it because `128 >> 5` is
  `0b100`, not `0b110`.
- `[197]` alone — a 2-byte leader with its follower missing. This is exactly the
  case the trailing `remaining == 0` catches; a solution that returns `True`
  inside the loop fails it.
- `[255]` and `[248, 130, 130, 130, 130]` — five leading ones. UTF-8 stops at
  four bytes, so both are invalid.
- **Out of scope, worth naming**: this checks the *shape* only. Real UTF-8
  validation also rejects overlong encodings (`[192, 128]` encodes NUL in two
  bytes) and surrogate code points `U+D800`–`U+DFFF`. LeetCode does not ask for
  either, but knowing they exist is the difference between reciting the pattern
  and understanding the format.
""",
        ),
    ],
}


def valid_utf8(data: list[int]) -> bool:
    remaining = 0  # continuation bytes still owed

    for entry in data:
        byte = entry & 0xFF

        if remaining:
            if byte >> 6 != 0b10:
                return False
            remaining -= 1
            continue

        if byte >> 7 == 0:
            remaining = 0
        elif byte >> 5 == 0b110:
            remaining = 1
        elif byte >> 4 == 0b1110:
            remaining = 2
        elif byte >> 3 == 0b11110:
            remaining = 3
        else:
            return False

    return remaining == 0  # must not end mid-character


CASES = [
    (([197, 130, 1],), True),
    (([235, 140, 4],), False),
    (([240, 162, 138, 147],), True),
    (([],), True),
    (([197],), False),
    (([128],), False),
    (([255],), False),
    (([248, 130, 130, 130, 130],), False),
]


def solve(data: list[int]) -> bool:
    return valid_utf8(data)
