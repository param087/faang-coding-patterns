"""Combination Sum — LeetCode 39."""

from __future__ import annotations

META = {
    "pattern": "backtracking",
    "insight": "Recurse on `i` rather than `i + 1` to allow reuse, which still fixes a non-decreasing order and kills the permutation duplicates.",
    "time": "O(n^(T/m + 1)), where T is the target and m the smallest candidate",
    "space": "O(T/m) recursion depth, excluding the output",
    "sections": [
        (
            "What it asks",
            """
Given distinct positive `candidates` and a `target`, return every **multiset**
of candidates summing to the target. Each candidate may be used **unlimited**
times. `[2,2,3]` and `[2,3,2]` are the same answer and must appear once.

Two questions worth asking before writing:

- **Are the candidates distinct?** LeetCode says yes. If they are not, this is
  Combination Sum II's dedup problem grafted onto unbounded reuse, and the
  skip rule changes.
- **Are they positive?** Also yes, and it matters more than it sounds: with a
  zero or a negative in the list, "unlimited reuse" means infinitely many
  answers and the recursion never terminates. Say this out loud — it is the
  fastest way to show you understand why the recursion is well founded.
""",
        ),
        (
            "Brute force, and why it fails",
            """
The naive reading is "build sequences": at each step pick any of the n
candidates, stop when you hit or overshoot the target. With the LeetCode
bounds — up to 30 candidates, each ≥ 2, target ≤ 40 — a sequence can be 20 long
and the search tree is 30²⁰ ≈ **3 × 10²⁹ nodes**. Not slow; never finishing.

And it is wasted work on top of that. A combination of length k gets generated
in up to k! different orders, so a 6-element answer arrives 720 times and you
would then need a set of sorted tuples to squeeze it back down to one.

Both problems have the same fix, which is the nice part.
""",
        ),
        (
            "The insight",
            """
Enumerate each multiset in exactly one canonical form: **non-decreasing
order**. Impose it by never looking left — the recursion carries a `start`
index and the loop begins there.

To allow reuse, recurse on **`i`**, not `i + 1`:

```python
explore(i, remaining - candidates[i])
```

`i + 1` gives Combination Sum II's "each element once"; `i` says "you may take
this one again, but you may never go back to an earlier one". That single
character is the entire difference between the two problems, and it
simultaneously permits repetition and forbids reorderings.

Termination is now easy to argue: every candidate is ≥ 1, so `remaining`
strictly decreases on every call and the depth is bounded by
`target / min(candidates)`.
""",
        ),
        (
            "Subtract, do not accumulate",
            """
Track `remaining` and compare against zero rather than keeping a running sum
and comparing against `target`. It is the same arithmetic, but the base cases
become `remaining == 0` (record) and `remaining < 0` (dead), which read
directly and never leave you wondering whether the check is `>` or `>=`.

Better still, do the check **before** you recurse — `if candidate > remaining`
— so you never push a doomed frame. That turns "generate then reject" into
"never generate", which is the definition of pruning and cuts a large chunk of
the tree on inputs with big candidates.
""",
        ),
        (
            "Sorting buys you a `break`",
            """
The input is not sorted, and the naive fix is `continue` past any candidate
that exceeds `remaining`. Sort first and it becomes `break`.

If `candidates` is ascending and `candidates[i] > remaining`, then every
candidate after it is too big as well, so the rest of the loop at this level is
dead. On `candidates = [2, 3, 6, 7], target = 7`, the sorted `break` prunes the
whole 6- and 7-branch the moment the remainder falls to 3.

This is not asymptotic — the bound is still exponential — but it is the
difference between an answer that reads as "I enumerated everything" and one
that reads as "I enumerated only what could win", and it is the sort of thing
that decides a borderline hire/no-hire.
""",
        ),
        (
            "Dry run",
            """
`candidates = [2, 3, 6, 7]`, `target = 7`.

- Take 2 → remaining 5. Take 2 again (still `start = 0`) → remaining 3. Take 2
  a third time → remaining 1; the loop opens with 2 > 1 and **breaks**.
- Back at remaining 3, move to 3 → remaining 0 → record **`[2, 2, 3]`**. Then 6
  > 3, break.
- Back at remaining 5: 3 → remaining 2, and 3 > 2 breaks immediately; 6 > 5
  breaks.
- Back at the root: 3 → remaining 4, which yields nothing (3 again leaves 1,
  then break). 6 → remaining 1, break. **7 → remaining 0 → record `[7]`.**

Answer: `[[2, 2, 3], [7]]`. Notice `[3, 2, 2]` never appears — not because it
is filtered out, but because `start` made it unreachable.
""",
        ),
        (
            "Follow-ups",
            """
- **"Just the count, not the lists."** Now it is unbounded-knapsack DP:
  `dp[t] += dp[t - c]` with the candidate loop **outside** the target loop.
  That ordering counts combinations; swapping the loops counts permutations,
  which is Combination Sum IV. Being able to state which loop order gives
  which is the payoff for having understood `start` here.
- **Combination Sum II** — duplicate candidates, each usable once: sort, pass
  `i + 1`, and skip equal siblings with `if i > start and c[i] == c[i-1]`.
- **Combination Sum III** — exactly k numbers drawn from 1..9: same skeleton
  with a second bound on `len(path)`, plus the prune "the k smallest remaining
  already exceed the target".
- **Negative candidates allowed, with a length cap.** The unbounded version is
  ill-posed; with a cap it becomes plain bounded search, and the `break`
  optimisation disappears because monotonicity is gone.
""",
        ),
    ],
}


def combination_sum(candidates: list[int], target: int) -> list[list[int]]:
    ordered = sorted(candidates)  # a copy, and it enables the `break` below
    result: list[list[int]] = []
    path: list[int] = []

    def explore(start: int, remaining: int) -> None:
        if remaining == 0:
            result.append(path[:])
            return
        for i in range(start, len(ordered)):
            if ordered[i] > remaining:
                break  # ascending: every later candidate is too big too
            path.append(ordered[i])
            explore(i, remaining - ordered[i])  # `i`, not `i + 1`: reuse allowed
            path.pop()

    explore(0, target)
    return result


CASES = [
    (([2, 3, 6, 7], 7), [[2, 2, 3], [7]]),
    (([7, 3, 2, 6], 7), [[2, 2, 3], [7]]),
    (([2, 3, 5], 8), [[2, 2, 2, 2], [2, 3, 3], [3, 5]]),
    (([8, 7, 4, 3], 11), [[3, 4, 4], [3, 8], [4, 7]]),
    (([2, 4], 7), []),
    (([2], 1), []),
    (([1], 3), [[1, 1, 1]]),
]


def solve(candidates: list[int], target: int) -> list[list[int]]:
    return combination_sum(candidates, target)
