"""Count Triplets That Can Form Two Arrays of Equal XOR — LeetCode 1442."""

from __future__ import annotations

META = {
    "pattern": "bit-manipulation",
    "insight": "a == b collapses to prefix[i] == prefix[k+1], so j is free: every matching prefix pair contributes k - i triplets.",
    "time": "O(n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Count triples `i < j <= k` where the XOR of `arr[i..j-1]` equals the XOR of
`arr[j..k]`.

Note the index ranges: `j` may equal `k`, so the right side can be a single
element, but `j > i`, so the left side is never empty. That asymmetry is in the
constraints for a reason — it is what makes the counting formula come out to
`k - i` rather than something with a `+1`.
""",
        ),
        (
            "The insight",
            """
Let `P[m]` be the XOR of the first `m` elements, `P[0] = 0`. Then
`a = P[j] ^ P[i]` and `b = P[k+1] ^ P[j]`.

XOR is its own inverse, so `a == b` becomes:

```
P[j] ^ P[i] == P[k+1] ^ P[j]
       P[i] == P[k+1]
```

`P[j]` cancels out entirely. **`j` does not appear in the condition at all** —
which means once you fix a pair `i < k+1` with equal prefix XOR, *every* `j`
strictly between them works. There are `(k + 1) - i - 1 = k - i` of them.

That is the entire problem. It reduces to: for each pair of equal values in the
prefix-XOR array, add the gap minus one.

The O(n²) version — group indices by prefix value and sum over pairs — is
already a fine answer at n = 300. To get O(n), sweep once and keep two maps per
prefix value: how many indices have seen it, and the sum of those indices. At
index `e` the new contribution is

```
count[P] * (e - 1) - index_sum[P]
```

because `Σ (e - i - 1)` over stored indices `i` is `count·(e-1) - Σ i`. Insert
`e` **after** taking the contribution, or an index pairs with itself and you add
a spurious `-1`.
""",
        ),
        (
            "Edge cases",
            """
- **`[]` and `[1]`** — no valid triple (you need at least two elements), answer
  0. The sweep produces 0 without a guard.
- **`[2, 2]`** — the smallest non-zero answer: `i = 0, j = 1, k = 1`, both sides
  equal 2. If your loop assumes `k > j` you return 0 here. This is the case that
  catches an off-by-one in the index constraints.
- **`[1, 1, 1, 1, 1]` → 10** — the prefix array alternates `0,1,0,1,0,1`, giving
  two groups of three equal values. Dense repeats are where an O(n²) pair scan
  degrades and where the running-sum trick pays.
- **`P[0] = 0` must be in the map before the sweep.** Drop it and you lose every
  triple whose window starts at index 0 — `[1, 3, 5, 7, 9]` silently returns 0
  instead of 3.
- **Zeros in the input** are harmless: `arr[i] = 0` just means two consecutive
  prefixes are equal, and the formula counts that pair as `k - i = 0`. No
  special case needed.
""",
        ),
    ],
}


def count_triplets(arr: list[int]) -> int:
    prefix = 0
    counts = {0: 1}  # prefix value -> how many indices produced it
    index_sums = {0: 0}  # prefix value -> sum of those indices
    total = 0

    for k, value in enumerate(arr):
        prefix ^= value
        end = k + 1

        if prefix in counts:
            # Every earlier index i with the same prefix contributes end - i - 1.
            total += counts[prefix] * (end - 1) - index_sums[prefix]

        counts[prefix] = counts.get(prefix, 0) + 1
        index_sums[prefix] = index_sums.get(prefix, 0) + end

    return total


CASES = [
    (([2, 3, 1, 6, 7],), 4),
    (([1, 1, 1, 1, 1],), 10),
    (([2, 3],), 0),
    (([2, 2],), 1),
    (([1],), 0),
    (([],), 0),
    (([1, 3, 5, 7, 9],), 3),
    (([7, 11, 12, 9, 5, 2, 7, 17, 22],), 8),
]


def solve(arr: list[int]) -> int:
    return count_triplets(arr)
