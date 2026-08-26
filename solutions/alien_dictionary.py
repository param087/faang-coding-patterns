"""Alien Dictionary — LeetCode 269."""

from __future__ import annotations

from collections import deque

META = {
    "pattern": "topological-sort",
    "insight": "Only the first position where two adjacent words differ carries information; a longer word before its own prefix is a contradiction.",
    "time": "O(total characters)",
    "space": "O(1) — at most 26 nodes and 26² edges",
    "sections": [
        (
            "What it asks",
            """
Premium, so the statement is not public — in my own words: you are handed a
list of lowercase words that is sorted according to some unknown permutation of
the English alphabet. Recover a letter ordering consistent with that sorting, as
a string. Return `""` if the input is self-contradictory.

Three clarifications worth raising before writing anything:

- **Is the order unique?** Usually not. `["ab", "adc"]` pins `b < d` and says
  nothing about `a` or `c`, so several answers are valid. Confirm that *any*
  valid order is accepted — otherwise you are solving Sequence Reconstruction
  instead, and the extra work is asserting the ready set is a singleton at every
  step.
- **Must every letter that appears in the words show up in the output?** Yes,
  including letters under no constraint at all.
- **What counts as invalid?** Two things: a cyclic constraint set, and the
  prefix violation described below. Only those.
""",
        ),
        (
            "Brute force, and why it fails",
            """
Enumerate permutations of the alphabet and test each against the word list.
26! ≈ 4·10²⁶ candidates. Even at a billion checks a second that is 10¹⁰ years,
so this is not a "slow but acceptable fallback" — it is not an algorithm.

More usefully: the brute force also fails to *find the structure*. The list of
words is not 26! degrees of freedom, it is a sparse set of pairwise "this letter
comes before that one" facts, and once you say that sentence the answer is a
topological sort.
""",
        ),
        (
            "The insight",
            """
Compare **adjacent word pairs only**. Transitivity does the rest: if
`words[0] < words[1]` and `words[1] < words[2]`, the pair `(words[0],
words[2])` adds nothing, so `n - 1` comparisons suffice rather than `n²/2`.

Within one pair, walk both words together and stop at the **first differing
character**. That position gives exactly one edge, `a → b`, and every position
after it is meaningless — in `["wrt", "wrf"]` the fact that `t` and `f` differ
tells you `t < f`, and nothing at all about characters that would follow. This
is the single most common bug: continuing the loop and emitting spurious edges
from later positions.

Then Kahn's algorithm over the ≤ 26 letters that actually appear. Nodes with
indegree 0 are letters nothing must precede; pop them in any order.

If the emitted order is shorter than the node set, some letters are stuck in a
cycle — the constraints contradict — so return `""`.

Cost is O(total characters) to build the graph and O(26 + 26²) to sort it, i.e.
linear in the input and constant in the alphabet. Say **O(1) space**: the graph
never exceeds 26 nodes no matter how many words arrive.
""",
        ),
        (
            "The prefix trap",
            """
This is the detail that decides the question, and it is what the interviewer is
actually watching for.

If you scan a pair and find **no differing character** in the shared prefix,
there is no edge — but you are not done. If the first word is *longer*, e.g.
`["abc", "ab"]`, the input claims `"abc"` sorts before `"ab"`. No alphabet
ordering makes that true: in any lexicographic order a proper prefix comes
first. That is an immediate `""`, not a silent skip.

In Python the clean way to express "the inner loop never broke" is `for ... else`
— the `else` runs precisely when no differing character was found:

```
for a, b in zip(first, second, strict=False):
    if a != b:
        ...; break
else:
    if len(first) > len(second):
        return ""
```

The mirror case, `["ab", "abc"]`, is perfectly legal and contributes no edge.
Getting the inequality direction backwards rejects valid inputs.

Second, quieter trap: **deduplicate edges**. `["ab","ad","ab","ad"]` derives
`b → d` twice; without a `set` (or a membership check before incrementing)
`indegree[d]` reaches 2, only one decrement fires, and `d` never becomes ready.
You then return `""` for an input that is fine.
""",
        ),
        (
            "Dry run",
            """
`["wrt", "wrf", "er", "ett", "rftt"]`

- `wrt` vs `wrf` → agree on `w`, `r`; differ at index 2 → **t → f**.
- `wrf` vs `er` → differ at index 0 → **w → e**.
- `er` vs `ett` → agree on `e`; differ at index 1 → **r → t**.
- `ett` vs `rftt` → differ at index 0 → **e → r**.

Letters `{w, r, t, f, e}`. Indegrees: `w` 0, `e` 1, `r` 1, `t` 1, `f` 1.

Kahn starts with `w` alone → `e` → `r` → `t` → `f`, giving **`"wertf"`**. Note
that `wrf` vs `er` produced only the `w → e` edge; had you kept comparing you
would have wrongly emitted `r → r` and `f → ...`.

Now change the input to `["z", "x", "z"]`: edges `z → x` and `x → z`. Every
indegree is 1, the queue starts empty, the emitted order has length 0 < 2 →
`""`.
""",
        ),
        (
            "Follow-ups",
            """
- **"Return the lexicographically smallest valid order."** Swap the `deque` for
  a `heapq` and pop the smallest ready letter each time. Same O(total
  characters), plus a log-26 factor that rounds to nothing.
- **"How many valid orders are there?"** Counting linear extensions of a DAG is
  #P-complete in general; on 26 nodes a bitmask DP over subsets — 2²⁶ ≈ 6.7·10⁷
  states — is the honest answer.
- **"Verify a given order instead of producing one."** Now you only need to
  check adjacent word pairs directly against a position map: O(total characters)
  with no graph at all.
- **"The order is unique — prove it or reject."** That is Sequence
  Reconstruction: assert the ready queue holds exactly one letter at every step.
- The returned string is not unique here, so the tests below **verify** the
  output against the derived constraints rather than comparing to a fixed
  answer.
""",
        ),
    ],
}


def alien_order(words: list[str]) -> str:
    adjacency: dict[str, set[str]] = {letter: set() for word in words for letter in word}
    indegree = dict.fromkeys(adjacency, 0)

    for first, second in zip(words, words[1:], strict=False):
        for a, b in zip(first, second, strict=False):
            if a != b:
                if b not in adjacency[a]:  # dedupe, or indegree over-counts
                    adjacency[a].add(b)
                    indegree[b] += 1
                break  # only the FIRST difference carries information
        else:
            if len(first) > len(second):  # "abc" before "ab" is impossible
                return ""

    queue = deque(letter for letter, degree in indegree.items() if degree == 0)
    order: list[str] = []

    while queue:
        letter = queue.popleft()
        order.append(letter)
        for successor in adjacency[letter]:
            indegree[successor] -= 1
            if indegree[successor] == 0:
                queue.append(successor)

    return "".join(order) if len(order) == len(indegree) else ""


def _letters(words: list[str]) -> set[str]:
    return {letter for word in words for letter in word}


def _constraints(words: list[str]) -> list[tuple[str, str]] | None:
    """Re-derive the pairwise facts independently, for verification."""
    pairs: list[tuple[str, str]] = []
    for first, second in zip(words, words[1:], strict=False):
        for a, b in zip(first, second, strict=False):
            if a != b:
                pairs.append((a, b))
                break
        else:
            if len(first) > len(second):
                return None
    return pairs


def check() -> None:
    solvable = [
        ["wrt", "wrf", "er", "ett", "rftt"],
        ["z", "x"],
        ["ab", "adc"],
        ["z", "z"],
        ["a"],
        ["ac", "ab", "zc", "zb"],
        ["ab", "abc"],
        ["abc", "abd", "b"],
    ]
    for words in solvable:
        order = alien_order(words)
        letters = _letters(words)
        assert set(order) == letters, (words, order)
        assert len(order) == len(letters), (words, order)  # no repeats

        position = {letter: index for index, letter in enumerate(order)}
        pairs = _constraints(words)
        assert pairs is not None, words
        for earlier, later in pairs:
            assert position[earlier] < position[later], (words, order, earlier, later)

    impossible = [
        ["z", "x", "z"],
        ["abc", "ab"],
        ["ba", "ab", "ba"],
        ["wrtkj", "wrt"],
    ]
    for words in impossible:
        assert alien_order(words) == "", words

    assert alien_order([]) == ""
