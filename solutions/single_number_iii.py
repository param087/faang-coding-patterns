"""Single Number III — LeetCode 260."""

from __future__ import annotations

META = {
    "pattern": "bit-manipulation",
    "insight": "XOR everything to get x ^ y, then any set bit of that is a position where x and y disagree — split the array on it and XOR twice.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Exactly **two** elements appear once; every other element appears twice.
Return both, in any order, in linear time and constant extra space.

Ask: is any order really accepted? (Yes — so no sorting is needed. The
implementation below returns them sorted anyway, purely so the tests are
deterministic; say that out loud rather than letting it look like you thought
sorting was required.) Can values be negative? (Yes, and it costs you nothing
— see the last section.)

The naive fold is the wrong first answer and worth stating so you can kill it:
XOR over everything gives `x ^ y`, a single number that mixes both answers
together. You cannot un-mix it without another idea.
""",
        ),
        (
            "The insight",
            """
Two steps.

**Step 1 — fold.** Every duplicate cancels, so `d = x ^ y`. Since `x != y`,
`d != 0`, which means **at least one bit is set in `d`**.

**Step 2 — that bit is a discriminator.** A set bit in `d` is a position where
`x` and `y` *differ*: one has a 1 there, the other a 0. Partition the whole
array by that bit and you get two independent Single Number problems:

- every duplicate pair has identical bits, so both copies land in the *same*
  bucket and cancel there;
- `x` and `y` land in **different** buckets, one each.

XOR each bucket and you have both answers. Two passes, two accumulators.

Pick the bit with `d & -d`, which isolates the **lowest set bit**. In two's
complement, `-d` is `~d + 1`: it flips everything above the lowest 1 and
leaves that 1 in place, so the AND keeps exactly that bit. `Integer.lowestOneBit`
in Java, `x & (~x + 1)` if you want it without a unary minus.

Any differing bit works — the highest, the third one, whichever. The lowest is
just the cheapest to extract.

You can also fold the second pass into one accumulator: XOR everything in the
"bit set" bucket to get one number, then recover the other as `d ^ first`.
That halves the work and is a nice thing to offer.
""",
        ),
        (
            "Negatives, zero, and the language traps",
            """
- **Negative values.** `d & -d` is a two's-complement identity, so it works
  unchanged for negative `d`. In Python, integers behave as if two's
  complement runs infinitely to the left, so `-5 & 5 == 1` gives the correct
  lowest set bit and `num & bit` classifies negative numbers correctly. No
  masking needed — unusual for this pattern, and worth knowing.
- **`d` is never 0**, because the two loners are guaranteed distinct. If they
  could be equal the whole approach collapses — that is a good clarifying
  question, and the answer is that "appears exactly once" makes it impossible.
- **C/C++ pitfall:** `-d` when `d` is `INT_MIN` is undefined behaviour for
  signed types. Use `d & (unsigned)(-d)`, or take the highest set bit instead.
- **Zero as an answer** is fine: it simply contributes nothing to the fold and
  falls into the "bit clear" bucket like any other value.
- **Follow-up: three loners?** The trick does not extend — one XOR no longer
  isolates a usable discriminator. Fall back to counting bit columns mod 2 with
  a smarter partition, or accept O(n) space. Being able to say *why* it breaks
  is worth more than a memorised extension.
""",
        ),
    ],
}


def single_number(nums: list[int]) -> list[int]:
    xor_all = 0
    for num in nums:
        xor_all ^= num  # duplicates cancel; leaves x ^ y

    # Lowest bit where x and y differ. Two's complement: -d == ~d + 1.
    discriminator = xor_all & -xor_all

    first = 0
    for num in nums:
        if num & discriminator:
            first ^= num  # one bucket holds exactly one of the loners

    second = xor_all ^ first
    return sorted((first, second))  # any order is accepted; sort for testing


CASES = [
    (([1, 2, 1, 3, 2, 5],), [3, 5]),
    (([-1, 0],), [-1, 0]),
    (([0, 1],), [0, 1]),  # zero is a legal answer
    (([1, 2, 3, 4, 1, 2],), [3, 4]),
    (([-1, -1, -2, -3],), [-3, -2]),  # both loners negative
    (([2, 2, -4, 7],), [-4, 7]),  # mixed signs, discriminator bit 0
    (([8, 8, 12, 4],), [4, 12]),  # differ only in a high bit
]


def solve(nums: list[int]) -> list[int]:
    return single_number(nums)
