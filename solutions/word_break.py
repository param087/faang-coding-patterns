"""Word Break — LeetCode 139."""

from __future__ import annotations

META = {
    "pattern": "dp-1d",
    "insight": "A prefix is breakable if some earlier breakable prefix is followed by a dictionary word — one boolean per cut position.",
    "time": "O(n · L²) with L the longest dictionary word",
    "space": "O(n + total dictionary length)",
    "sections": [
        (
            "What it asks",
            """
Can `s` be cut into a sequence of dictionary words, reusing words freely? Yes
or no — you are not asked for the segmentation.

Ask: **can words repeat** (yes, and that removes any "used" bookkeeping); is
the dictionary large or the words long (it decides whether you bound the inner
loop or build a trie); are we told the alphabet (rarely matters here).
""",
        ),
        (
            "The insight",
            """
State it as a cut, not as a word:

> `dp[i]` = can `s[:i]` be segmented?

Then `dp[i]` is true when there exists a `j < i` with `dp[j]` true and
`s[j:i]` in the dictionary. `dp[0] = True` — the empty prefix is trivially
segmented — and the answer is `dp[n]`.

The subtlety worth voicing: **the dictionary word is the last piece**, not the
first. Anchoring on the last word means everything to its left is a smaller
instance of the same question, which is what makes the recurrence 1-D. Trying
to anchor on the first word gives a suffix DP that works but reads backwards.

Two implementation notes that turn an accepted solution into a good one:

- put the dictionary in a **set**, so membership is O(word length) hashing
  rather than a scan of the list;
- start `j` no earlier than `i - max_word_length`. Without that bound the inner
  loop is O(n) per position and you slice substrings that could never match.
""",
        ),
        (
            "The case that kills naive recursion",
            """
Recursion without memoisation is exponential, and the adversarial input is
easy to write: `s = "aaa…aab"` (say 40 a's then a b) with dictionary
`["a", "aa", "aaa", "aaaa"]`. Every prefix splits four ways, nothing ever
matches the trailing `b`, and the search explores on the order of **4⁴⁰**
compositions before returning false. Memoising the cut position collapses it
to 40 states.

That input is also the one to offer unprompted — it shows you know *why* the
memo is load-bearing rather than decorative.

Other cases worth a moment:

- **Empty `s`** → true by convention (zero words). Say the convention aloud.
- **Empty dictionary** → false for any non-empty `s`.
- `"catsandog"` with `["cats","dog","sand","and","cat"]` → **false**, the
  standard trap: `cats` + `and` leaves `og`.
- `"cars"` with `["car","ca","rs"]` → **true**, and a greedy longest-match-first
  walk gets it wrong: it commits to `car` and gives up on the leftover `s`.
  Greedy is not merely slower here, it is incorrect.
- **Word Break II** asks for every segmentation. The answer count can be
  exponential, so it is backtracking with this same `dp` array used as a
  reachability filter to prune dead branches.
""",
        ),
    ],
}


def word_break(s: str, word_dict: list[str]) -> bool:
    words = set(word_dict)
    if not words:
        return not s

    longest = max(len(word) for word in words)
    n = len(s)

    breakable = [False] * (n + 1)
    breakable[0] = True  # the empty prefix

    for i in range(1, n + 1):
        # the last word can start no earlier than i - longest
        for j in range(max(0, i - longest), i):
            if breakable[j] and s[j:i] in words:
                breakable[i] = True
                break

    return breakable[n]


CASES = [
    (("leetcode", ["leet", "code"]), True),
    (("applepenapple", ["apple", "pen"]), True),
    (("catsandog", ["cats", "dog", "sand", "and", "cat"]), False),
    (("cars", ["car", "ca", "rs"]), True),
    (("aaaaaaaaaaaaaaaaaaaab", ["a", "aa", "aaa", "aaaa"]), False),
    (("", ["a"]), True),
    (("a", []), False),
    (("abcd", ["a", "abc", "b", "cd"]), True),
]


def solve(s: str, word_dict: list[str]) -> bool:
    return word_break(s, word_dict)
