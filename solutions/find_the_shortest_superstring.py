"""Find the Shortest Superstring — LeetCode 943."""

from __future__ import annotations

META = {
    "pattern": "dp-advanced",
    "insight": "It is travelling salesman on n ≤ 12 words: maximise total pairwise overlap, with a bitmask DP on (visited set, last word).",
    "time": "O(n²·2ⁿ) for the DP, plus O(n²·L) to build the overlap table",
    "space": "O(n·2ⁿ)",
    "sections": [
        (
            "What it asks",
            """
Given words, produce the shortest string containing every one of them as a
substring. LeetCode guarantees the words are distinct and that **no word is a
substring of another** — check that guarantee out loud, because without it you
must first discard the contained words, and the pairwise-overlap model below
silently under-counts.

Two observations fix the shape of the answer. Each word appears in the result
starting at some position, and sorting those start positions gives an
**ordering** of the words. Given an ordering, the shortest string that realises
it is: write the first word, then append each next word minus its longest
prefix that is already a suffix of what you have. Because no word contains
another, that suffix comes entirely from the immediately preceding word, so

```
length(ordering) = sum(len(word)) - sum(overlap(consecutive pairs))
```

Total length is fixed; minimising it means **maximising total pairwise
overlap** over all n! orderings. That is the travelling salesman path problem,
on a complete directed graph with `overlap(i, j)` as the edge weight.
""",
        ),
        (
            "The insight",
            """
n ≤ 12, and 12! = 479,001,600 — too many orderings, but 2¹² = 4096 subsets is
nothing. That gap is the entire signal for **bitmask DP**: the future of a
partial ordering depends only on *which words are already placed* and *which
one is last*, not on the order they were placed in.

```
dp[mask][last] = max total overlap of a chain that uses exactly the words in
                 `mask` and ends at `last`
dp[mask][last] = max over prev in mask \\ {last} of
                     dp[mask ^ (1<<last)][prev] + overlap[prev][last]
```

Seed every singleton at 0 and read the answer off `max(dp[full][last])`.

Precompute `overlap[i][j]` as the largest `k` with `words[i][-k:] ==
words[j][:k]` — a naive O(L²) per pair is fine at these sizes; mention that
KMP or Z-function makes it O(L) per pair if the interviewer pushes.

**Reconstruction is the half people forget.** Keep `parent[mask][last]` and
walk it backwards from the best final state, clearing one bit at a time, then
reverse. Emitting the string is then `words[first]` plus, for each consecutive
pair, `words[cur][overlap[prev][cur]:]`.
""",
        ),
        (
            "Pitfalls, and how the tests are written",
            """
- **The answer is not unique.** Several orderings can tie on length, and
  LeetCode's judge accepts any minimal superstring. So `CASES` here pin the
  **length**, and `check()` additionally asserts every input word really is a
  substring of what the function returns — the two properties that actually
  define correctness.
- **A zero-initialised table silently breaks reconstruction.** If every
  overlap is 0 — `["alex", "loves", "leetcode"]` — then `dp[mask][last]` is 0
  everywhere and the strict `>` never fires, so no `parent` is ever written and
  the walk-back returns a single word. Seed unreachable states at −1 (or write
  the parent on the first relaxation). The *length* is right and the *string*
  is wrong, which is the worst kind of bug to find in an interview.
- **Maximise overlap, do not minimise length directly.** Both work, but the
  overlap formulation keeps every DP value a small non-negative integer.
- **`overlap[i][i]` must be 0** and self-transitions excluded, or a word
  chains to itself and the mask logic breaks.
- **Cap the overlap scan at `min(len(a), len(b))`, exclusive of full
  containment**: if `a.endswith(b)` entirely, `b` is a substring of `a` and the
  problem said that cannot happen — but a defensive implementation should drop
  contained words up front rather than produce a chain that repeats them.
- **Iterate masks in increasing order.** `dp[mask]` reads `dp[mask ^ bit]`,
  which has strictly fewer bits and therefore a smaller value, so a plain
  `for mask in range(1 << n)` is already a valid topological order.
- **Why not greedy?** "Repeatedly merge the pair with the largest overlap" is
  the classic approximation and it is genuinely wrong here: on
  `["catg", "ctaagt", "gcta", "ttca", "atgcatc"]` the optimum is 16 characters
  and greedy merging can miss it. Shortest common superstring is NP-hard in
  general; n ≤ 12 is what makes exact search affordable.
""",
        ),
    ],
}


def _overlap_table(words: list[str]) -> list[list[int]]:
    n = len(words)
    table = [[0] * n for _ in range(n)]
    for i, a in enumerate(words):
        for j, b in enumerate(words):
            if i == j:
                continue  # a word never chains to itself
            for k in range(min(len(a), len(b)), 0, -1):
                if a.endswith(b[:k]):
                    table[i][j] = k
                    break
    return table


def shortest_superstring(words: list[str]) -> str:
    n = len(words)
    if n <= 1:
        return words[0] if words else ""

    overlap = _overlap_table(words)
    size = 1 << n
    # dp[mask][last] = max total overlap of a chain over `mask` ending at `last`;
    # -1 means "not yet reached", so a genuine 0-overlap chain still beats it.
    dp = [[-1] * n for _ in range(size)]
    parent = [[-1] * n for _ in range(size)]
    for i in range(n):
        dp[1 << i][i] = 0  # singleton chain: no pairs, no overlap

    for mask in range(size):  # increasing popcount order comes free
        for last in range(n):
            if not mask >> last & 1:
                continue
            rest = mask ^ (1 << last)
            if rest == 0:
                continue  # seeded above
            for prev in range(n):
                if not rest >> prev & 1 or dp[rest][prev] < 0:
                    continue
                gained = dp[rest][prev] + overlap[prev][last]
                if gained > dp[mask][last]:
                    dp[mask][last] = gained
                    parent[mask][last] = prev

    full = size - 1
    last = max(range(n), key=lambda i: dp[full][i])

    order: list[int] = []
    mask = full
    while last != -1:
        order.append(last)
        previous = parent[mask][last]
        mask ^= 1 << last
        last = previous
    order.reverse()

    pieces = [words[order[0]]]
    for prev, cur in zip(order, order[1:], strict=False):
        pieces.append(words[cur][overlap[prev][cur]:])  # drop the shared prefix
    return "".join(pieces)


CASES = [
    ((["alex", "loves", "leetcode"],), 17),
    ((["catg", "ctaagt", "gcta", "ttca", "atgcatc"],), 16),
    ((["abcd", "cdef", "fghi", "efgh"],), 9),
    ((["gcta", "catg", "ttca"],), 9),
    ((["ab", "ba"],), 3),
    ((["abc"],), 3),
    (([],), 0),
]


def solve(words: list[str]) -> int:
    return len(shortest_superstring(words))


def check() -> None:
    for (words,), expected in CASES:
        result = shortest_superstring(words)
        assert len(result) == expected, (words, result, expected)
        for word in words:  # any minimal superstring is accepted, so verify
            assert word in result, (words, word, result)
        assert solve(words) == expected
