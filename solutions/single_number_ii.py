"""Single Number II — LeetCode 137."""

from __future__ import annotations

META = {
    "pattern": "bit-manipulation",
    "insight": "Count each bit column mod 3 instead of mod 2 — XOR is only the k=2 case of a much more general construction.",
    "time": "O(32n) = O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Every element appears **three times** except one, which appears once. Return
it, in linear time and constant extra space.

The trap is that people arrive having memorised "single number means XOR" and
try it anyway. XOR fails immediately: `a ^ a ^ a = a`, so a triple does not
cancel — it survives as one copy and pollutes the accumulator. The fold gives
you the XOR of every *distinct* value, which is not the answer.

Ask: **can the values be negative?** (Yes — LeetCode's range is ±2³¹, and the
answer itself may be negative. That single fact decides whether your solution
is correct in Python, as the fourth section shows.) Ask also whether O(1)
space is really required; if not, `Counter` is 30 seconds of work and you can
spend the rest of the interview on the real version.
""",
        ),
        (
            "Brute force, and why it fails",
            """
Two honest baselines:

- **Count occurrences by re-scanning** for each element: O(n²). LeetCode caps
  `n` at 3·10⁴, so that is **9·10⁸ comparisons** — a few seconds in Python,
  and a wrong answer in an interview.
- **`Counter(nums)`**: O(n) time, but O(n) space. Fast enough, and it fails
  the constraint that is the entire point of the question.

Sorting and checking triples is O(n log n) and mutates the input. Also
acceptable to *mention*, never to stop at.

The binding constraint here is space, not time. Say that before you write a
line, because it tells the interviewer you read the follow-up.
""",
        ),
        (
            "The insight",
            """
Bits are independent. Look at a single bit position across the whole array:
every element that appears three times contributes either 0 or 3 ones to that
column; the loner contributes 0 or 1.

So **count the 1s in each column and take the total mod 3**. Multiples of 3
vanish; what remains is the loner's bit at that position:

```
column count mod 3  ==  the answer's bit at that position
```

32 columns, one pass each — 32n operations, and 32 counters of state, which is
O(1). At n = 3·10⁴ that is under 10⁶ operations.

This is the generalisation that makes the whole family click:

| every element repeats | isolate the loner with |
| --- | --- |
| 2 times | count mod 2 — which *is* XOR |
| 3 times | count mod 3 |
| k times | count mod k |

XOR is not a special trick; it is per-column addition mod 2, done 32 lanes at
a time by one CPU instruction.
""",
        ),
        (
            "The detail that decides it: sign",
            """
You rebuild the answer by setting bit `b` whenever column `b` has a non-zero
count mod 3. In C++ or Java you rebuild it into a 32-bit `int` and the sign
comes back for free — bit 31 *is* the sign bit.

**In Python it does not.** Python integers are unbounded, so setting bit 31 of
a fresh `0` yields 2 147 483 648, not −2 147 483 648. Your answer for `-4`
comes back as `4294967292` and every test with a negative loner fails.

The fix is explicit sign extension — if bit 31 is set, subtract 2³²:

```python
if result & (1 << 31):
    result -= 1 << 32
```

This is the single most common reason a correct-looking 137 solution fails,
and it is worth calling out before you run the code rather than after.

The **two-register automaton** avoids the issue entirely:

```python
ones = twos = 0
for num in nums:
    ones = (ones ^ num) & ~twos
    twos = (twos ^ num) & ~ones
return ones
```

`(twos, ones)` is a **2-bit counter mod 3 per column**, running all 32 columns
in parallel: states 00 → 01 → 10 → 00. A bit enters `ones` on first sight,
moves to `twos` on second, and is cleared from both on third. `ones` at the
end holds the bits seen a number of times ≡ 1 mod 3.

Two things to get right: `twos` must be computed with the **already-updated**
`ones` (swap the lines and it breaks), and `& ~twos` is what forbids the
"seen 3" state 11 from ever occurring. And because Python's `~` behaves as
infinite two's complement, every sign lane is handled by the same recurrence —
so this version needs no masking and returns negatives correctly.
""",
        ),
        (
            "Dry run",
            """
`[2, 2, 3, 2]` — columns, low bit first (2 = `10`, 3 = `11`):

- column 0: values contribute `0,0,1,0` → count 1, 1 mod 3 = **1**
- column 1: `1,1,1,1` → count 4, 4 mod 3 = **1**
- all higher columns: 0

Answer = `0b11` = **3**. ✓

Note that column 1 has count **4**, not 3 — the loner's own high bit lives
there too. Mod 3 does not care.

Now the automaton on the same input:

| num | ones | twos |
| --- | --- | --- |
| — | 000 | 000 |
| 2 | 010 | 000 |
| 2 | 000 | 010 |
| 3 | 001 | 000 |
| 2 | 011 | 000 |

Read column 1 down the table: `1 → 0 → 0 → 1`, i.e. states 01, 10, 00, 01 — a
mod-3 counter that wrapped once and is now back at "seen once". Column 0 was
touched only by the 3, so it sits at 01 from step three onward. The two
columns never interact, which is exactly why one pair of registers does the
work of 32 independent counters.
""",
        ),
        (
            "Follow-ups",
            """
- **"Every element appears k times except one, which appears once."** Count
  mod k — the code below is already that solution with `k = 3` hard-coded.
  The automaton generalises to ⌈log₂ k⌉ registers, which is why people write
  the counting version when k is arbitrary.
- **"…except one which appears m times, m < k."** Same column counts; the
  remainder is `m` rather than 1, so set the bit when `count % k != 0`.
- **[Single Number III](../single-number-iii/)** — two loners, everything else
  twice. Different technique: XOR everything, then split on a differing bit.
- **"Do it without the 32-iteration loop."** That is the automaton, and it is
  the answer they are fishing for.
""",
        ),
    ],
}


def single_number(nums: list[int]) -> int:
    """Count each bit column mod 3, then sign-extend the 32-bit result."""
    result = 0

    for bit in range(32):
        count = sum((num >> bit) & 1 for num in nums)
        if count % 3:
            result |= 1 << bit

    # Python ints are unbounded: bit 31 means negative, so extend the sign.
    if result & (1 << 31):
        result -= 1 << 32

    return result


def single_number_automaton(nums: list[int]) -> int:
    """(twos, ones) is a mod-3 counter per bit column, 32 lanes at once."""
    ones = twos = 0

    for num in nums:
        ones = (ones ^ num) & ~twos
        twos = (twos ^ num) & ~ones  # note: uses the *updated* ones

    return ones


CASES = [
    (([2, 2, 3, 2],), 3),
    (([0, 1, 0, 1, 0, 1, 99],), 99),
    (([7],), 7),
    (([5, 5, 5, 0],), 0),  # the loner is zero
    (([-2, -2, 1, 1, -3, 1, -3, -3, -4, -2],), -4),  # negative loner
    (([-1, -1, -1, -9],), -9),
    (([2147483647, 3, 3, 3],), 2147483647),  # INT_MAX, bit 30 set
]


def solve(nums: list[int]) -> int:
    return single_number(nums)


def check() -> None:
    for args, expected in CASES:
        assert single_number(*args) == expected
        assert single_number_automaton(*args) == expected

    # Both must survive INT_MIN, where naive reconstruction loses the sign.
    edge = [-2147483648, 4, 4, 4]
    assert single_number(edge) == -2147483648
    assert single_number_automaton(edge) == -2147483648
