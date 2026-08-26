"""Encode and Decode Strings — LeetCode 271."""

from __future__ import annotations

META = {
    "pattern": "arrays-hashing",
    "insight": "Any separator can also appear inside the data, so prefix each string with its length rather than trusting a delimiter.",
    "time": "O(total length) to encode and to decode",
    "space": "O(total length)",
    "sections": [
        (
            "What it asks",
            """
LeetCode 271 is premium, so its statement is not public — this is the task in
my own words.

Design a pair of functions that survive a channel which can carry exactly one
string:

```
encode(list[str]) -> str
decode(str)       -> list[str]
```

with `decode(encode(xs)) == xs` for **every** list of strings. The strings may
contain any characters at all, including whatever you were hoping to use as a
separator, and the list may be empty or contain empty strings.

The clarifying question is precisely that last point: *is the alphabet
restricted?* If the interviewer says "ASCII printable, no control characters",
a sentinel byte becomes legal and the problem collapses. If they say "any
characters", you need the real answer.
""",
        ),
        (
            "The insight",
            """
The naive answer is `"#".join(strs)` and `data.split("#")`. It fails the moment
a payload contains `#`, and it also cannot tell `[]` from `[""]` — both encode
to the empty string.

The fix is to stop *searching* for a boundary and start *computing* it. Write
each string as its length, a marker, then the bytes:

```
["lint", "code"]  ->  "4#lint4#code"
["3#a", ""]       ->  "3#3#a0#"
```

The decoder scans forward to the first `#` to read a length — that prefix is
guaranteed to be digits only — then takes exactly that many characters
verbatim, whatever they are, and resumes. The `#` inside `"3#a"` is never
examined as a delimiter, because the decoder is already positioned past it.

That is the general principle behind every length-prefixed wire format, from
netstrings to HTTP's `Content-Length` to protobuf: **self-delimiting beats
self-describing.** Say the name; it is the point of the question.
""",
        ),
        (
            "What it has to survive",
            """
- **The empty list versus `[""]`.** `[]` encodes to `""`, `[""]` encodes to
  `"0#"`. A delimiter-join cannot distinguish them, and this is the first case
  an interviewer will try.
- **A payload that is itself a valid encoding**, like `"5#hello"`. The length
  prefix is immune; a `split` is not.
- **Multi-digit lengths.** A 300-character string writes `300#`, so the decoder
  must read digits until the marker, not a fixed number of them.
- **Non-ASCII.** In Python `len` and slicing both work in code points, so the
  round trip holds for emoji and CJK. If you move to bytes — the realistic
  version of this problem — encode `len(s.encode())` and slice the bytes, or a
  four-byte character will shift every subsequent offset.

The alternative that also works is **escaping**: double every `#` in the
payload and use `##` as the separator. It is correct, but decoding needs a
character-by-character state machine instead of a slice, and the encoded form
can double in size. Length prefixing is O(1) per boundary and never expands.
""",
        ),
    ],
}


def encode(strs: list[str]) -> str:
    return "".join(f"{len(s)}#{s}" for s in strs)


def decode(data: str) -> list[str]:
    out: list[str] = []
    i = 0

    while i < len(data):
        marker = data.index("#", i)  # the prefix before it is digits only
        length = int(data[i:marker])
        start = marker + 1
        out.append(data[start : start + length])  # verbatim, delimiters included
        i = start + length

    return out


CASES = [
    ((["lint", "code", "love", "you"],), ["lint", "code", "love", "you"]),
    (([],), []),
    (([""],), [""]),  # must not collapse to the empty list
    ((["", ""],), ["", ""]),
    ((["#", "##", "###"],), ["#", "##", "###"]),
    ((["5#hello", "x"],), ["5#hello", "x"]),  # a payload that looks like an encoding
    ((["a" * 300, "b"],), ["a" * 300, "b"]),  # multi-digit length prefix
    ((["  ", "\n", "🙂"],), ["  ", "\n", "🙂"]),
]


def solve(strs: list[str]) -> list[str]:
    return decode(encode(list(strs)))


def check() -> None:
    for args, expected in CASES:
        assert solve(*args) == expected, f"round trip failed for {args!r}"

    # The wire format itself, not just the round trip: lengths are computed,
    # so the '#' inside a payload is never read as a boundary.
    assert encode(["3#a", ""]) == "3#3#a0#"
    assert decode("3#3#a0#") == ["3#a", ""]
    assert encode([]) == ""
    assert encode([""]) == "0#"
