"""Word Break II — LeetCode 140."""

from __future__ import annotations

from functools import cache

META = {
    "pattern": "tries",
    "insight": "Memoise on the suffix, not the path: the set of sentences for s[i:] never depends on how you reached i.",
    "time": "O(n² + total output) after memoisation — n² prefix walks in the trie",
    "space": "O(n·output) for the memo, O(total dictionary characters) for the trie",
    "sections": [
        (
            "What it asks",
            """
Return **every** way to insert spaces into `s` so that each piece is a
dictionary word. Words may be reused.

The clarifying question that changes the answer: **how many sentences can there
be?** `s = "aaaaaaaaaaaaaaaaaaaa"` with `wordDict = ["a","aa","aaa","aaaa"]`
has tens of thousands. The output itself can be exponential, so no algorithm is
polynomial in `n` alone — the honest bound is polynomial *plus* the size of the
output. Say that out loud; it is the difference between "I memoised" and "I
understand what memoisation can and cannot buy here".
""",
        ),
        (
            "The insight",
            """
Two separate ideas, and interviewers want both.

**The trie** replaces "is `s[start:end]` in the dictionary?" — a fresh substring
slice and hash per candidate, O(n) work each — with a single walk from `start`
that extends one character at a time and stops the instant the path leaves the
trie. On a dictionary of short words that early break is most of the win: you
never look at prefixes no word could start with.

**The memo** is what stops the exponential blow-up on failure. `sentences(i)`
— the list of ways to break `s[i:]` — depends only on `i`, never on the pieces
chosen before it. Cache it and the killer case `"aaa…aab"` with
`["a","aa","aaa"]` collapses from 2ⁿ paths to n cached calls that each return
the empty list. Without the memo that input at n = 30 is ~10⁹ explorations for
an answer of `[]`.

Base case: `sentences(len(s))` returns `("",)` — one way to break nothing,
namely the empty sentence. Returning `()` instead makes every recursion return
`()` and the whole thing answers "no solutions".
""",
        ),
        (
            "The pruning everyone forgets, and the ones that matter",
            """
The memo alone still builds full strings for suffixes that lead nowhere, because
it only caches *after* the recursion. If the interviewer asks for the classic
speed-up: precompute a boolean `can_break[i]` with plain Word Break I (O(n²),
no output), then refuse to recurse into any `i` where it is false. On the
adversarial "aaa…b" family that turns the expensive pass into a no-op. With the
memo already in place it is a constant-factor win, not an asymptotic one — say
which it is rather than presenting it as a fix.

Two smaller things that decide correctness:

- **Concatenate with a separator, not `" ".join` on a shared list.** Building
  each sentence as `s[start:end] + " " + rest` keeps the cached tuples immutable;
  a shared mutable list that you append to and pop from is where the "extra
  trailing space" and "sentences leak between branches" bugs come from.
- **Clear the cache before returning.** `functools.cache` on a closure keeps the
  results — and the closed-over `s` — alive for the process. Harmless in an
  interview, a leak in a service, and it makes repeated calls with different
  inputs correct only by accident of the closure being fresh each time.
""",
        ),
    ],
}


class _Node:
    __slots__ = ("children", "is_word")

    def __init__(self) -> None:
        self.children: dict[str, _Node] = {}
        self.is_word = False


def word_break(s: str, word_dict: list[str]) -> list[str]:
    if not s:
        return []

    root = _Node()
    for word in word_dict:
        if not word:  # an empty "word" would allow infinitely many sentences
            continue
        node = root
        for char in word:
            node = node.children.setdefault(char, _Node())
        node.is_word = True

    @cache
    def sentences(start: int) -> tuple[str, ...]:
        if start == len(s):
            return ("",)  # exactly one way to break nothing

        found: list[str] = []
        node = root
        for end in range(start, len(s)):
            child = node.children.get(s[end])
            if child is None:
                break  # no dictionary word starts with s[start:end + 1]
            node = child
            if node.is_word:
                head = s[start : end + 1]
                found.extend(head + (" " + rest if rest else "") for rest in sentences(end + 1))
        return tuple(found)

    result = list(sentences(0))
    sentences.cache_clear()  # do not keep `s` alive behind a module-level closure
    return result


CASES = [
    (("catsanddog", ["cat", "cats", "and", "sand", "dog"]), ["cat sand dog", "cats and dog"]),
    (
        ("pineapplepenapple", ["apple", "pen", "applepen", "pine", "pineapple"]),
        ["pine apple pen apple", "pine applepen apple", "pineapple pen apple"],
    ),
    (("catsandog", ["cats", "dog", "sand", "and", "cat"]), []),
    (("a", ["a"]), ["a"]),
    (("aaaa", ["a", "aa"]), ["a a a a", "a a aa", "a aa a", "aa a a", "aa aa"]),
    # The case that hangs an unmemoised backtracker: 2^24 dead paths for [].
    (("a" * 24 + "b", ["a", "aa", "aaa", "aaaa"]), []),
    (("abc", ["d"]), []),
    (("", ["a"]), []),
]


def solve(s: str, word_dict: list[str]) -> list[str]:
    return sorted(word_break(s, word_dict))  # any order is accepted; sort to compare
