"""Number of Longest Increasing Subsequence — LeetCode 673."""

from __future__ import annotations

META = {
    "pattern": "dp-1d",
    "insight": "Carry a count beside every LIS length: a strictly longer predecessor resets it, a tied one adds into it.",
    "time": "O(n²)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Not the length of the longest strictly increasing subsequence — **how many**
of them there are.

Two clarifying questions that change the answer:

- **Strict or non-decreasing?** Strict on LeetCode. It is the `<` in the inner
  loop and nothing else.
- **Are subsequences distinguished by index or by value?** By **index**. On
  `[2, 2]` the answer is 2, not 1: two different positions, same values. If you
  assume "distinct sequences of values" you will write a set-based solution and
  fail the first duplicate test.

Counts can exceed 32 bits on adversarial inputs, which matters in Java/C++ and
not in Python — worth saying out loud anyway.
""",
        ),
        (
            "The insight",
            """
Start from the O(n²) LIS DP, where `lengths[i]` is the length of the LIS
**ending at** `i`. Add a second array, `counts[i]`, for how many LIS of that
length end at `i`.

When you look at a predecessor `j` with `nums[j] < nums[i]`, exactly one of
two things happens:

- `lengths[j] + 1 > lengths[i]` — you have found a **strictly better** route.
  Everything you had counted so far is now too short, so `counts[i] = counts[j]`
  (overwrite, not add).
- `lengths[j] + 1 == lengths[i]` — a **tie**, so it is another set of ways in.
  `counts[i] += counts[j]`.

Every longest subsequence ends somewhere, so the answer is the sum of `counts[i]`
over all `i` with `lengths[i] == max(lengths)`.

The `tails` + binary search trick from LIS does **not** extend here: `tails`
throws away exactly the multiplicity you now need. Say that rather than trying
to patch it.
""",
        ),
        (
            "The two mistakes that decide it",
            """
**Adding instead of overwriting on the longer branch.** `counts[i] += counts[j]`
in both cases silently double-counts the shorter routes. It still passes
`[1, 3, 5, 4, 7]`, which is why the bug survives to the interview.

**Returning `counts[argmax]`.** The longest subsequence rarely ends at one
index. On `[1, 1, 1, 2, 2, 2, 3, 3, 3]` the LIS length is 3 and the answer is
**27** — 3 choices at each level — spread over the last three indices. Reading
one entry gives 9.

Dry run `[1, 3, 5, 4, 7]`: `lengths = [1, 2, 3, 3, 4]`, `counts = [1, 1, 1, 1, 2]`.
Index 4 first learns length 4 from index 2 (`counts = 1`), then ties from
index 3 and accumulates to 2. Max length 4 occurs once → **2**.
""",
        ),
    ],
}


def find_number_of_lis(nums: list[int]) -> int:
    if not nums:
        return 0

    n = len(nums)
    lengths = [1] * n  # length of the LIS ending at i
    counts = [1] * n  # how many such LIS end at i

    for i in range(n):
        for j in range(i):
            if nums[j] >= nums[i]:
                continue
            if lengths[j] + 1 > lengths[i]:
                lengths[i] = lengths[j] + 1
                counts[i] = counts[j]  # strictly better: discard the old tally
            elif lengths[j] + 1 == lengths[i]:
                counts[i] += counts[j]  # a tie: another way in

    longest = max(lengths)
    # A longest subsequence can end anywhere, so sum every index that reaches it.
    return sum(total for size, total in zip(lengths, counts, strict=True) if size == longest)


CASES = [
    (([1, 3, 5, 4, 7],), 2),
    (([2, 2, 2, 2, 2],), 5),
    (([1, 1, 1, 2, 2, 2, 3, 3, 3],), 27),
    (([1, 2, 4, 3, 5, 4, 7, 2],), 3),
    (([5, 4, 3, 2, 1],), 5),
    (([1, 2, 3, 4, 5],), 1),
    (([7],), 1),
    (([],), 0),
]


def solve(nums: list[int]) -> int:
    return find_number_of_lis(nums)
