"""String Matching in an Array — LeetCode 1408."""

from __future__ import annotations

META = {
    "pattern": "string-algorithms",
    "insight": "Join the words with a sentinel: every word occurs once at its own slot, so a second occurrence means it sits inside another.",
    "time": "O(n · T) — n words, T total characters",
    "space": "O(T) for the join",
    "sections": [
        (
            "What it asks",
            """
Given a list of lowercase words, return every word that appears as a
**substring of some other word** in the list. Any order is accepted.

Two clarifiers, both of which change the code:

- **Is a word a substring of itself?** No — it has to sit inside a *different*
  word. This is the whole difficulty of an otherwise trivial problem.
- **Can words repeat?** LeetCode guarantees they are distinct. If they are not,
  say what you will do: two copies of `"xy"` are each inside the other, so both
  come back. Decide it out loud rather than discovering it in a failing test.
""",
        ),
        (
            "The insight",
            """
With n ≤ 100 and |word| ≤ 30, the double loop with `w in other` is 10⁴ pairs of
30-character strings. Write it, say it is 10⁴ operations, and move on — an
interviewer who asked an Easy is not trying to trick you.

The version worth *talking* about is what happens when n grows. Then you stop
treating this as n² independent searches and make it one text-search problem:

```
joined = "#".join(words)
```

`#` is outside the alphabet, so **no match can straddle a separator** — every
occurrence of a word lies entirely inside one slot. Each word therefore occurs
at least once, at its own slot, and exactly once there (its slot is the same
length as it). So:

> word occurs ≥ 2 times in the join  ⇔  word is inside some other word.

One KMP scan per word over the join gives the count. That is O(n · T), and the
counting formulation is what generalises: run **Aho–Corasick** over the join
and all n patterns are matched in a single O(T) pass, or build a suffix
automaton of the join and query each word in O(|word|).
""",
        ),
        (
            "The pitfall: excluding the word itself",
            """
The naive fix — `for i, for j, if i != j` — is right but only because the
words are distinct. The counting version encodes the same rule as `count >= 2`,
and that threshold is the entire correctness argument. `count >= 1` returns
everything; `count > 2` misses words that appear inside exactly one other word.

Two details that decide it:

- **The sentinel must be outside the alphabet.** Join with `""` and `["ab",
  "ba"]` manufactures a phantom `"ab"` across the seam, and `"ba"` is suddenly
  a substring of nothing that exists.
- **Overlaps must count.** After a match, KMP resets to `failure[k-1]`, not to
  0. `"aa"` occurs *twice* in `"aaa"`, and it is the overlap-aware count that
  keeps the ≥ 2 test honest for repeats — though here any count ≥ 2 is enough,
  so the reset only has to not *lose* matches.

Output order is unconstrained; returning input order costs nothing and makes
the function deterministic to test.
""",
        ),
    ],
}


def _count_occurrences(pattern: str, text: str) -> int:
    """KMP: how many times `pattern` occurs in `text`, overlaps included."""
    if not pattern or len(pattern) > len(text):
        return 0

    failure = [0] * len(pattern)
    k = 0
    for i in range(1, len(pattern)):
        while k and pattern[k] != pattern[i]:
            k = failure[k - 1]
        if pattern[k] == pattern[i]:
            k += 1
        failure[i] = k

    count = 0
    k = 0
    for character in text:
        while k and pattern[k] != character:
            k = failure[k - 1]
        if pattern[k] == character:
            k += 1
        if k == len(pattern):
            count += 1
            k = failure[k - 1]  # allow overlapping matches
    return count


def string_matching(words: list[str]) -> list[str]:
    # '#' is outside the alphabet, so no match crosses a slot boundary.
    joined = "#".join(words)

    # Every word matches its own slot exactly once; a second hit is elsewhere.
    return [word for word in words if _count_occurrences(word, joined) >= 2]


CASES = [
    ((["mass", "as", "hero", "superhero"],), ["as", "hero"]),
    ((["leetcode", "et", "code"],), ["et", "code"]),
    ((["blue", "green", "bu"],), []),
    ((["a"],), []),  # a word is not a substring of itself
    ((["ab", "abab", "aba"],), ["ab", "aba"]),  # overlapping occurrences
    ((["aaa", "aa", "a"],), ["aa", "a"]),  # nested repeats
    ((["xy", "xy"],), ["xy", "xy"]),  # duplicates: each is inside the other
    (([],), []),
]


def solve(words: list[str]) -> list[str]:
    return string_matching(words)
