"""Wiggle Sort II — LeetCode 324."""

from __future__ import annotations

META = {
    "pattern": "sorting",
    "insight": "Split the sorted array at the median and interleave the halves from their far ends, so equal medians can never land side by side.",
    "time": "O(n log n) — O(n) average with quickselect",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Rearrange the array so it strictly alternates: `nums[0] < nums[1] > nums[2] <
nums[3] > ...`. Any valid arrangement is accepted, and the input is guaranteed
to admit one.

The word that decides everything is **strictly**. Wiggle Sort I (280) allows
`<=`, which is why the greedy answer to that problem exists at all. Confirm the
strictness and confirm duplicates are allowed — those two facts together are
the entire difficulty.
""",
        ),
        (
            "The wrong first answer",
            """
Wiggle Sort I is solved by a single pass: whenever an adjacent pair violates
the required direction, swap it. That greedy works there because `a <= b` can
be repaired locally.

Here it does not. Run it on `[1, 5, 1, 1, 6, 4]`: the first three positions are
already fine, then index 3 needs `nums[3] > nums[2]` and both are 1 — swapping
two equal values changes nothing, and no adjacent swap anywhere else helps
either. The greedy is stuck, yet `[1, 6, 1, 5, 1, 4]` is a perfectly good
answer.

Strictness makes the problem **global**: equal values must be kept at distance
≥ 2, and only a view of the whole multiset can guarantee that. Local repair
cannot see it.
""",
        ),
        (
            "The insight",
            """
Sort the array and cut it at the median: `small = sorted[:⌈n/2⌉]`,
`large = sorted[⌈n/2⌉:]`. Every element of `large` is ≥ every element of
`small`. Put `small` on the even indices and `large` on the odd ones and the
alternation is automatic — *provided* the two halves are laid down
**backwards**, largest of each half first:

```
nums[0], nums[2], nums[4], ... <- small reversed
nums[1], nums[3], nums[5], ... <- large reversed
```

Giving the larger half the odd (peak) positions and taking the extra element
for `small` when `n` is odd keeps the counts right: `⌈n/2⌉` even slots and
`⌊n/2⌋` odd slots.
""",
        ),
        (
            "Why reversed, and not ascending",
            """
This is the detail that decides the problem, and the one interviewers probe.

Duplicates of the **median** value sit at the end of `small` and the start of
`large`. Laying both halves down ascending puts exactly those two neighbours
next to each other:

`[4, 5, 5, 6]` → `small = [4, 5]`, `large = [5, 6]` → ascending interleave gives
`4, 5, 5, 6`, and `nums[1] > nums[2]` fails because both are 5.

Reversing pushes them as far apart as the layout allows: `small` reversed is
`[5, 4]`, `large` reversed is `[6, 5]`, giving `5, 6, 4, 5` — the two 5s are now
three positions apart. That is the correctness argument: the reversed interleave
spreads a run of equal values by the maximum the index parity permits, so if any
strict arrangement exists for this multiset, this one is strict too.

Do not over-claim the guarantee, though. "No value occurs more than `⌈n/2⌉`
times" is **necessary but not sufficient** — six 2s in an array of 11 must take
all six valley slots, which then forces all five peaks to exceed 2, so
`[0, 1, 1, 2, 2, 2, 2, 2, 2, 3, 3]` has no answer at all despite satisfying the
count bound. The problem hands you the existence guarantee; rely on that rather
than on a frequency test.
""",
        ),
        (
            "Dry run",
            """
`[1, 5, 1, 1, 6, 4]` → sorted `[1, 1, 1, 4, 5, 6]`, cut at index 3.

- `small = [1, 1, 1]` reversed → even indices 0, 2, 4.
- `large = [4, 5, 6]` reversed → `6, 5, 4` at odd indices 1, 3, 5.
- Result `[1, 6, 1, 5, 1, 4]`: 1 < 6 > 1 < 5 > 1 < 4.

The hostile version is `[1, 1, 1, 2, 2, 2]`, where the median duplicates
straddle the cut. Reversed layout gives `[1, 2, 1, 2, 1, 2]`; ascending layout
gives `[1, 2, 1, 2, 1, 2]` too here — which is exactly why `[4, 5, 5, 6]`, not
this one, belongs in your test list.
""",
        ),
        (
            "Follow-ups",
            """
- **O(n) time, O(1) space** — the sort only exists to find the median, so
  replace it with quickselect (O(n) average) plus a Dutch-flag three-way
  partition around it, then apply the same interleave *virtually* via the index
  map `(1 + 2*i) % (n | 1)`. That mapping walks the odd slots first and then
  the even ones, which reproduces the reversed layout without a second array.
  It is famously fiddly; know it exists, and reach for it only when asked.
- **Wiggle Sort I (280)** — non-strict, so the adjacent-swap greedy is O(n) and
  correct. Confirm which variant you have been handed before writing anything.
- **Wiggle Subsequence (376)** — different problem entirely (longest
  alternating subsequence, a two-state DP), but it comes up in the same
  interview loop and the names are close enough to cause a bad five minutes.
""",
        ),
    ],
}


def wiggle_sort(nums: list[int]) -> list[int]:
    ordered = sorted(nums)
    mid = (len(nums) + 1) // 2  # the smaller half keeps the odd element

    # Backwards, so duplicates straddling the median end up far apart.
    nums[::2] = ordered[:mid][::-1]
    nums[1::2] = ordered[mid:][::-1]
    return nums


CASES = [
    (([1, 5, 1, 1, 6, 4],), [1, 6, 1, 5, 1, 4]),
    (([1, 3, 2, 2, 3, 1],), [2, 3, 1, 3, 1, 2]),
    (([4, 5, 5, 6],), [5, 6, 4, 5]),
    (([1, 1, 2, 2, 2, 1],), [1, 2, 1, 2, 1, 2]),
    (([2, 1],), [1, 2]),
    (([1],), [1]),
    (([],), []),
]


def solve(nums: list[int]) -> list[int]:
    # Written in place, so copy — CASES are reused across runs.
    return wiggle_sort(list(nums))


def _is_wiggle(values: list[int]) -> bool:
    return all(
        values[i] < values[i + 1] if i % 2 == 0 else values[i] > values[i + 1]
        for i in range(len(values) - 1)
    )


def check() -> None:
    for args, expected in CASES:
        assert solve(*args) == expected, args

    # Any valid arrangement is accepted, so verify the property itself on the
    # inputs where the median duplicates straddle the cut.
    hostile = [
        [4, 5, 5, 6],
        [1, 1, 2, 2, 2, 1],
        [1, 3, 2, 2, 3, 1],
        [1, 2, 2, 1, 2, 1, 1, 1, 1, 2, 2, 2, 1],
        [5, 5, 5, 1, 1, 6, 6],
    ]
    for nums in hostile:
        out = solve(nums)
        assert sorted(out) == sorted(nums), nums
        assert _is_wiggle(out), (nums, out)
