"""Substring with Concatenation of All Words — LeetCode 30."""

from __future__ import annotations

from collections import Counter, defaultdict

META = {
    "pattern": "sliding-window",
    "insight": "All words share one length, so the string is a tape of fixed-size tokens — run a word-level window once per starting offset.",
    "time": "O(n · L) where L is the word length",
    "space": "O(m · L) for the word counts",
    "sections": [
        (
            "What it asks",
            """
Every word in `words` has the **same length**. Find all starting indices in
`s` where some concatenation of all the words, in any order, appears — each
word used exactly as many times as it occurs in `words`.

Ask: **can `words` contain duplicates?** (Yes, and that is the case that
breaks a set-based solution.) Is the output order significant? (No — return
them in any order; sorting them just makes the tests deterministic.)

The uniform word length is not decoration. It is the constraint that turns a
string problem into an array problem.
""",
        ),
        (
            "The insight",
            """
Because every word has length `L`, any valid answer starts at some index `i`
and is a sequence of `L`-aligned chunks from `i` onwards. Indices that differ
by a multiple of `L` share the same chunk boundaries — so there are only `L`
distinct ways to slice `s` into tokens.

Run the ordinary "window over a multiset" algorithm `L` times, once per offset
`0 .. L-1`, treating each `L`-character chunk as a single symbol. Within an
offset the window moves in steps of `L`, holds a count map, and:

- token not in `need` → nothing containing it can work: clear the window and
  restart `left` past it;
- token over its required count → advance `left` by whole tokens until it is
  not;
- window holds all `m` tokens → record `left`, then slide off one token so
  the scan continues.

Each offset touches `n/L` tokens and there are `L` offsets, so O(n) token
operations, each costing O(L) to slice and hash: **O(n · L)** overall, versus
the naive "test every index" at O(n · m · L).

At n = 10⁴, m = 5000, L = 30 the naive version is on the order of 10⁹
character comparisons; this is around 3·10⁵.
""",
        ),
        (
            "The pitfall: duplicates, and why the window is per-offset",
            """
Two mistakes account for nearly every wrong submission.

**Using a set of words.** With `words = ["word","good","best","good"]` a set
accepts a window holding one `good` and something else. Counts, not sets — and
the check is `window[token] > need[token]`, an over-count, not membership.

**Sharing one window across offsets.** The window's `left` must stay on the
same residue class mod `L` as `right`, otherwise you are comparing tokens
that were never aligned. Re-initialise `window`, `used` and `left` at the top
of every offset. A single stray carry-over produces answers that look almost
right — usually a superset of the truth — which is the worst kind of bug to
debug under time pressure.

One more: after recording a hit, you must **shrink by exactly one token**
before continuing, not clear the window. `("aaaaaa", ["aa","aa"])` returns
`[0, 1, 2]`; clearing loses the overlapping hits.
""",
        ),
    ],
}


def find_substring(s: str, words: list[str]) -> list[int]:
    if not s or not words:
        return []

    word_len = len(words[0])
    total = len(words)
    if word_len == 0 or word_len * total > len(s):
        return []

    need = Counter(words)
    found: list[int] = []

    for offset in range(word_len):
        window: defaultdict[str, int] = defaultdict(int)
        used = 0  # tokens currently inside the window
        left = offset

        for right in range(offset, len(s) - word_len + 1, word_len):
            token = s[right : right + word_len]

            if token not in need:  # nothing spanning this token can work
                window.clear()
                used = 0
                left = right + word_len
                continue

            window[token] += 1
            used += 1

            while window[token] > need[token]:  # drop whole tokens from the left
                window[s[left : left + word_len]] -= 1
                left += word_len
                used -= 1

            if used == total:
                found.append(left)
                window[s[left : left + word_len]] -= 1  # slide by one token, do not clear
                left += word_len
                used -= 1

    return sorted(found)  # the problem allows any order; sorted is reproducible


CASES = [
    (("barfoothefoobarman", ["foo", "bar"]), [0, 9]),
    (("wordgoodgoodgoodbestword", ["word", "good", "best", "word"]), []),
    (("wordgoodgoodgoodbestword", ["word", "good", "best", "good"]), [8]),
    (("barfoofoobarthefoobarman", ["bar", "foo", "the"]), [6, 9, 12]),
    (("aaaaaa", ["aa", "aa"]), [0, 1, 2]),
    (("aaa", ["a", "a"]), [0, 1]),
    (("a", ["a"]), [0]),
    (("", ["a"]), []),
]


def solve(s: str, words: list[str]) -> list[int]:
    return find_substring(s, list(words))
