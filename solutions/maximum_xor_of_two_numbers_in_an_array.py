"""Maximum XOR of Two Numbers in an Array — LeetCode 421."""

from __future__ import annotations

META = {
    "pattern": "tries",
    "insight": "A trie keyed by bit, walked high bit first, lets each number greedily demand the opposite bit — a high bit outweighs all lower ones.",
    "time": "O(32n)",
    "space": "O(32n) for the trie",
    "sections": [
        (
            "What it asks",
            """
Return the largest `nums[i] XOR nums[j]` over all pairs.

Two clarifications that shape the code:

- **How wide are the numbers?** LeetCode says `0 <= nums[i] < 2³¹`, so 31 bits.
  That constant is the whole complexity, and if the interviewer says 64-bit,
  nothing changes but the loop bound. Guard against inventing a 32nd bit for
  the sign — these are non-negative.
- **May `i == j`?** It does not matter: `x XOR x == 0`, which can never beat a
  genuine pair unless every element is equal, in which case 0 is the answer
  anyway. That is why the code can insert everything first and then query
  everything without excluding self-pairs.
""",
        ),
        (
            "Brute force, and why it fails",
            """
Every pair: `max(a ^ b for a, b in combinations(nums, 2))`. That is n²/2
XORs — at `n = 2 × 10⁵` about **2 × 10¹⁰ operations**, roughly a minute of
pure CPU in C and far worse in Python.

The instinct to sort first is wrong, and worth killing early: XOR is not
monotone in either argument. `8 ^ 7 = 15` while `8 ^ 9 = 1`, so the two
largest values need not be the best pair, nor need adjacent values in sorted
order. There is no ordering of the array that makes the answer local.
""",
        ),
        (
            "The insight",
            """
Build the answer **bit by bit, from the top**, because bit 30 is worth more
than every lower bit put together: 2³⁰ > 2²⁹ + 2²⁸ + … + 2⁰. So if any pair can
set bit 30, the answer sets bit 30, full stop — there is nothing the lower bits
could do to compensate. Greed is not a heuristic here, it is exact.

That turns "find the best partner for `x`" into a walk. Put every number into a
binary trie, most significant bit at the root, each node having children `0`
and `1`. To maximise `x XOR partner`, at each level ask for the child equal to
`1 - bit(x)`; take it if it exists, otherwise take the only child there is and
concede that bit. 31 steps per number, `n` numbers: **O(31n) ≈ 6 × 10⁶** at the
same input size that killed the brute force.

The trie is not storing numbers so much as answering "does a number exist with
this exact 31-bit prefix?" — which is precisely the question greedy needs at
each level, and precisely what a hash set cannot answer without enumerating.
""",
        ),
        (
            "The details that decide it",
            """
- **High bit first, always.** Iterating `range(31)` instead of
  `range(30, -1, -1)` builds a trie keyed by the *least* significant bit and
  the greedy choice becomes meaningless — you will get an answer, it will be
  wrong, and no small test case catches it. Write the loop bound before you
  write the body.
- **Fixed width, not `bit_length()`.** Every number must occupy the same number
  of trie levels or the paths do not line up; `5` has to be `0…0101`, not
  `101`. Deriving the width from `max(nums).bit_length()` is a legitimate
  optimisation, but it must be *one* width shared by every insert and query.
- **`(x >> bit) & 1`**, not `x & (1 << bit)`, unless you normalise — the second
  yields `0` or `2^bit`, which is fine for a truth test and fatal as a dict
  key.
- **Insert-then-query, or interleave?** Both work. Interleaving (insert `x`,
  then immediately query for `x`) is a common trick and is correct because XOR
  is symmetric: the pair `{a, b}` is evaluated when the later of the two is
  processed, and the first element merely queries an empty-ish trie and finds
  itself. Insert-all-first is easier to defend out loud.
- **Empty or single-element input** must return 0 without an index error. One
  element queries the trie, finds only itself, and yields `0` — no special case
  needed, but check it.
""",
        ),
        (
            "Dry run",
            """
`[3, 10, 5, 25, 2, 8]`, shown on 5 bits for legibility:

```
 3  00011
10  01010
 5  00101
25  11001
 2  00010
 8  01000
```

Query with `5 = 00101`:

- bit 4: `5` has 0, so ask for a `1`. Present — only `25` goes that way. Take
  it, answer bit set, and **the branch is now committed to 25**.
- bit 3: `5` has 0, ask for `1`. Under `25` the next bit is `1`. Take it. Set.
- bit 2: `5` has 1, ask for `0`. `25` has `0`. Set.
- bit 1: `5` has 0, ask for `1`. `25` has `0`. **Concede** — the only child is
  a `0`, so this bit stays 0.
- bit 0: `5` has 1, ask for `0`. `25` has `1`. Concede.

Result `11100 = 28`, which is `5 ^ 25`. The two conceded bits are the point:
greed does not mean every bit is winnable, it means you never trade a high bit
for lower ones.

The two largest values pair to `25 ^ 10 = 19`, and the closest neighbours in
sorted order do worse still. Sorting would never have found 28.
""",
        ),
        (
            "Follow-ups",
            """
- **"Do it without a trie."** There is a slick O(31n) hash-set version: build
  the answer prefix bit by bit, and at each step mask every number to its top
  `k` bits into a set, then test whether some `p` in the set has
  `p ^ candidate` also in the set — using `a ^ b = c ⇔ a ^ c = b`. Same
  complexity, a third of the code, much harder to derive live. Know it exists.
- **Maximum XOR With an Element From Array (1707)**, where each query caps the
  partner at `m`: sort queries by `m`, sort `nums`, and insert into the trie
  incrementally — the trie is the same, the offline ordering is the new idea.
- **Maximum XOR of two numbers in a subtree / on a path** (tree problems) reuse
  the same trie with DFS insert-and-remove, which is why the node should carry
  a count rather than a boolean if you expect deletion.
- **Minimum XOR pair** is the opposite question and does *not* need a trie —
  sort, and check adjacent elements only, because for minimum XOR the sorted
  neighbours really are optimal.
""",
        ),
    ],
}

BITS = 31  # 0 <= nums[i] < 2**31


class BitTrieNode:
    __slots__ = ("children",)

    def __init__(self) -> None:
        self.children: list[BitTrieNode | None] = [None, None]


def find_maximum_xor(nums: list[int]) -> int:
    if not nums:
        return 0

    root = BitTrieNode()
    for number in nums:
        node = root
        for bit in range(BITS - 1, -1, -1):  # high bit first, or it is meaningless
            digit = (number >> bit) & 1
            child = node.children[digit]
            if child is None:
                child = BitTrieNode()
                node.children[digit] = child
            node = child

    best = 0
    for number in nums:
        node = root
        current = 0
        for bit in range(BITS - 1, -1, -1):
            digit = (number >> bit) & 1
            wanted = 1 - digit
            child = node.children[wanted]
            if child is not None:
                current |= 1 << bit  # the opposite bit exists: take it
            else:
                child = node.children[digit]
            assert child is not None  # every level was populated on insert
            node = child
        best = max(best, current)

    return best


CASES = [
    (([3, 10, 5, 25, 2, 8],), 28),  # 5 ^ 25, neither of them the two largest
    (([14, 70, 53, 83, 49, 91, 36, 80, 92, 51, 66, 70],), 127),
    (([0],), 0),
    (([8, 8, 8],), 0),  # every pair XORs to 0
    (([],), 0),
    (([0, 2147483647],), 2147483647),  # the full 31-bit range
    (([2147483647, 2147483646],), 1),
    (([8, 10, 2],), 10),  # 8 ^ 2 = 10 beats 8 ^ 10 = 2, so sorted order misleads
    (([1, 2, 3, 4, 5, 6, 7],), 7),
]


def solve(nums: list[int]) -> int:
    return find_maximum_xor(nums)
