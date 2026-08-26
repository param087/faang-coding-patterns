"""The k-th Lexicographical String of All Happy Strings of Length n — LeetCode 1415."""

from __future__ import annotations

META = {
    "pattern": "math-geometry",
    "insight": "Every prefix has exactly 2 continuations, so the sorted list is a balanced tree and k picks the branch by division, not by enumeration.",
    "time": "O(n)",
    "space": "O(n) for the answer",
    "sections": [
        (
            "What it asks",
            """
A *happy string* uses only `a`, `b`, `c` and never repeats a character
adjacently. List every happy string of length `n` in lexicographic order and
return the k-th (1-indexed), or `""` if there are fewer than `k`.

Count them first, because the count is the solution: 3 choices for the first
character and exactly **2** for each of the rest, so there are
`3 · 2^(n-1)` — for n = 10 that is 1536, and `k <= 100`, so a DFS that
generates all of them and indexes is accepted here.

Generate-and-index is worth *saying* — it is the correct answer to the problem
as stated and it takes 6 lines. Then offer the counting version, because the
follow-up "now n = 60" is where the interview is actually going: 3·2⁵⁹ is
1.7·10¹⁸ strings and enumeration is dead, while the counting version does not
notice.
""",
        ),
        (
            "The insight",
            """
Because every prefix has the *same* number of completions, the sorted list has
no ragged edges: it is a perfectly balanced tree, and you can walk down it
choosing the branch by arithmetic.

At depth 0 there are three subtrees of `2^(n-1)` strings each, so with `k`
made 0-indexed:

```
index, k = divmod(k, block)   # which subtree, and how far into it
```

`index` selects the character, `k` becomes the rank *within* that subtree, and
`block` halves. At every later depth there are only two children — the two
letters that differ from the previous one — and crucially, filtering `"abc"` in
order keeps them **sorted**, which is what makes lexicographic order and
divmod order the same thing.

That is one pass, O(n), with no recursion and no candidate strings ever built.
""",
        ),
        (
            "Edge cases",
            """
- **The 1-indexing.** `k` arrives 1-indexed; every division below assumes
  0-indexed. Subtract 1 exactly once, immediately after the bounds check, and
  never think about it again. Doing it inside the loop is the classic bug and
  it only shows up at block boundaries — `n = 3, k = 9` returns `"cab"`
  correctly but `k = 4` and `k = 5` straddle a subtree edge.
- **k out of range** returns `""`, not an exception. Compare against
  `3 · 2^(n-1)` *before* touching `k`, or the first `divmod` silently produces
  an index of 3 and an `IndexError` on `"abc"`.
- **n = 1.** `block` is `2⁰ = 1`, the loop body never runs, and the first
  divmod degenerates to `index = k`. No special case needed — but check it,
  because a `1 << (n - 1)` written as `1 << n` breaks exactly here.
- **The largest string** is `"cbcbcb…"` and the smallest `"abab…"`, which is
  the cheapest sanity check on the whole construction: k = 1 and
  k = 3·2^(n-1).
""",
        ),
    ],
}


def get_happy_string(n: int, k: int) -> str:
    if k > 3 * (1 << (n - 1)):  # 3 first characters, 2 choices thereafter
        return ""

    k -= 1  # 1-indexed in, 0-indexed arithmetic from here on
    block = 1 << (n - 1)  # strings under each first character

    index, k = divmod(k, block)
    result = ["abc"[index]]

    for _ in range(n - 1):
        block >>= 1  # two children per node from now on
        index, k = divmod(k, block)
        options = [letter for letter in "abc" if letter != result[-1]]  # stays sorted
        result.append(options[index])

    return "".join(result)


CASES = [
    ((1, 3), "c"),
    ((1, 4), ""),  # only 3 exist
    ((3, 9), "cab"),
    ((3, 1), "aba"),  # the smallest
    ((3, 12), "cbc"),  # the largest
    ((2, 7), ""),  # 3 * 2 = 6 exist
    ((4, 16), "bcbc"),
    ((10, 100), "abacbabacb"),
]


def solve(n: int, k: int) -> str:
    return get_happy_string(n, k)
