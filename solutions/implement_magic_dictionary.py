"""Implement Magic Dictionary — LeetCode 676."""

from __future__ import annotations

META = {
    "pattern": "string-algorithms",
    "symbol": "MagicDictionary",
    "insight": "Index every word under each of its one-character wildcards; a query is then a hash lookup per position, not a walk over the dictionary.",
    "time": "O(L²) per word to build and per query, L = word length",
    "space": "O(total characters × L)",
    "sections": [
        (
            "What it asks",
            """
Build a dictionary once, then answer queries: can you change **exactly one**
character of the query word to obtain a word in the dictionary?

The word "exactly" is the whole problem. `search("hello")` with `"hello"` in
the dictionary returns `False` — zero changes is not one change. Confirm that,
and confirm that lengths must match (they must; you may substitute, not insert
or delete).

Also worth asking: how many queries relative to dictionary size? The answer
below pays a build cost to make each query independent of dictionary size,
which is only worth it when queries dominate — which they do here.
""",
        ),
        (
            "The insight",
            """
The naive query compares the word against every dictionary entry of the same
length, counting mismatches and stopping at 2. O(N·L) per query, which for a
dictionary of 100 words is genuinely fine and is a perfectly acceptable first
answer — say it, then improve it.

The improvement: **precompute the wildcards.** For each dictionary word,
generate the `L` keys formed by blanking one position:

```
"hello"  ->  "*ello", "h*llo", "he*lo", "hel*o", "hell*"
```

Store, against each key, the *set of characters that were blanked out*. A query
is then: for each position `i`, look up the query's own wildcard key, and ask
whether any stored character at that position differs from the query's. One
dict lookup per position, independent of dictionary size.

Keeping the **set of blanked characters** rather than a count is what makes
"exactly one" fall out for free — `stored - {query[i]}` is non-empty precisely
when some dictionary word differs from the query at position `i` and agrees
everywhere else. The length is baked into the key, so mismatched lengths can
never collide.
""",
        ),
        (
            "The trap: near-duplicates in the dictionary",
            """
The shortcut everyone writes is `if word in self.words: return False` to
enforce "exactly one change", then fall through to a looser search.

It is wrong. Dictionary `["hello", "hallo"]`, query `"hello"`: the query *is*
in the dictionary, but `"hallo"` is one substitution away, so the answer is
**True**. Any check that keys off the query's own presence gets this backwards.

The wildcard version never has the problem, because it compares characters at
the blanked position rather than comparing whole words. On `"h*llo"` the stored
set is `{"e", "a"}`; removing the query's own `"e"` leaves `{"a"}`, so it
returns True — for the right reason.

Second trap in the same family: an interviewer who then asks for *at most* one
change. That is `stored` being non-empty rather than `stored - {query[i]}`, a
one-character edit — and being able to point at exactly which character changes
is the sign you understood the invariant rather than memorised it.
""",
        ),
    ],
}


class MagicDictionary:
    def __init__(self) -> None:
        # wildcard key -> the set of characters that were blanked out to form it
        self.buckets: dict[str, set[str]] = {}

    def buildDict(self, dictionary: list[str]) -> None:
        self.buckets = {}
        for word in dictionary:
            for i, character in enumerate(word):
                key = word[:i] + "*" + word[i + 1 :]
                self.buckets.setdefault(key, set()).add(character)

    def search(self, searchWord: str) -> bool:
        for i, character in enumerate(searchWord):
            key = searchWord[:i] + "*" + searchWord[i + 1 :]
            blanked = self.buckets.get(key)
            # Non-empty after removing our own character => some word differs
            # here and matches everywhere else. Exactly one change.
            if blanked and blanked - {character}:
                return True
        return False


CASES = [
    (
        (["hello", "leetcode"], ["hello", "hhllo", "hell", "leetcoded"]),
        [False, True, False, False],
    ),
    (
        # "hello" is in the dictionary and still True, via "hallo".
        (["hello", "hallo", "leetcode"], ["hello", "hhllo", "hell", "leetcoded"]),
        [True, True, False, False],
    ),
    (
        (["abc", "abd"], ["abc", "abe", "aec", "xbc", "abcd", ""]),
        [True, True, True, True, False, False],
    ),
    ((["a"], ["a", "b", "aa", ""]), [False, True, False, False]),
    ((["a", "b"], ["a", "b", "c"]), [True, True, True]),
    (([], ["a", ""]), [False, False]),
    ((["aaa", "aab"], ["aaa", "aac", "aa"]), [True, True, False]),
]


def solve(dictionary: list[str], queries: list[str]) -> list[bool]:
    magic = MagicDictionary()
    magic.buildDict(dictionary)
    return [magic.search(query) for query in queries]


def check() -> None:
    for args, expected in CASES:
        assert solve(*args) == expected, args

    # Driven as an object, the way the judge does it: rebuilding replaces state.
    magic = MagicDictionary()
    magic.buildDict(["hello", "leetcode"])
    assert magic.search("hello") is False
    assert magic.search("hhllo") is True

    magic.buildDict(["zzz"])
    assert magic.search("hhllo") is False  # old dictionary is gone
    assert magic.search("zzz") is False
    assert magic.search("azz") is True
