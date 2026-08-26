"""Find K Closest Elements — LeetCode 658."""

from __future__ import annotations

META = {
    "pattern": "binary-search",
    "insight": "The answer is a contiguous window, so binary search its left edge and compare only the two elements that fall off either end.",
    "time": "O(log(n − k) + k)",
    "space": "O(1) beyond the output slice",
    "sections": [
        (
            "What it asks",
            """
Given a sorted array, return the `k` elements closest to `x`, themselves in
sorted order. Ties go to the **smaller** element.

Ask two things before writing: is `x` guaranteed to be in the array (no — it
can sit outside the range entirely), and is the output order by distance or by
value (**by value**, which is what makes a slice a legal answer).

The tie rule is not decoration. `arr = [1, 2, 3, 4, 5], k = 4, x = 3` gives
`[1, 2, 3, 4]`, not `[2, 3, 4, 5]`, purely because of it.
""",
        ),
        (
            "The insight",
            """
The first answer most people give is "sort by `|a − x|`, take `k`, re-sort".
That is O(n log n), throws away the sortedness you were handed, and the
custom comparator has to encode the tie rule as `(abs(a - x), a)` or it
silently returns the wrong window.

The unlock is that **the answer is a contiguous window of length `k`**. If two
elements are in the answer, everything between them is at least as close as
the farther of the two, so it is in too. That reduces the problem from
"choose `k` elements" to "choose one integer": the window's left index, which
lives in `[0, n − k]`.

Now binary search that index. For a candidate left edge `mid`, the choice is
between keeping `arr[mid]` and sliding right to pick up `arr[mid + k]`:

```
x - arr[mid] > arr[mid + k] - x   →   the right neighbour is strictly closer, slide right
```

Note there is no `arr[mid + k]` out-of-bounds risk: `mid < high <= n − k`, so
`mid + k < n` on every comparison that runs.

The comparison is written as a subtraction rather than `abs`, and that is
deliberate — when `x` lies outside `[arr[mid], arr[mid + k]]` one side goes
negative, which is exactly the "stay put" or "run to the end" answer you want.
""",
        ),
        (
            "Edge cases, and the tie",
            """
- **The `>` must be strict.** On a tie the condition is false, so `high = mid`
  keeps the left window — the smaller elements. Flip it to `>=` and
  `([1,2,3,4,5], 4, 3)` returns `[2,3,4,5]`. This single character is the
  whole tie rule.
- **`x` outside the array.** `x = -1` collapses to the leftmost window,
  `x = 100` to the rightmost, with no special casing.
- **`k == n`** makes the search space `[0, 0]`: the loop never runs and you
  return the whole array.
- **Duplicates** (`[1,1,1,10,10,10]`) are fine — the window test only ever
  compares distances, never identities.
- The loop is `while low < high` with `high = mid` (not `mid − 1`), because
  `mid` is still a live candidate. Writing `low <= high` here is the classic
  infinite loop.
""",
        ),
    ],
}


def find_closest_elements(arr: list[int], k: int, x: int) -> list[int]:
    # Search the window's LEFT INDEX in [0, n - k], not a value in the array.
    low, high = 0, len(arr) - k

    while low < high:
        mid = (low + high) // 2
        # Keep arr[mid], or drop it and gain arr[mid + k]?
        if x - arr[mid] > arr[mid + k] - x:  # strict `>`: ties keep the left window
            low = mid + 1
        else:
            high = mid  # mid is still a candidate

    return arr[low : low + k]


CASES = [
    (([1, 2, 3, 4, 5], 4, 3), [1, 2, 3, 4]),  # the tie: not [2, 3, 4, 5]
    (([1, 2, 3, 4, 5], 4, -1), [1, 2, 3, 4]),  # x below the whole array
    (([1, 2, 3, 4, 5], 4, 4), [2, 3, 4, 5]),
    (([1, 2, 3, 4, 5], 5, 100), [1, 2, 3, 4, 5]),  # k == n, x far right
    (([0, 0, 1, 2, 3, 3, 4, 7, 7, 8], 3, 5), [3, 3, 4]),  # tie at distance 2
    (([1, 1, 1, 10, 10, 10], 1, 9), [10]),
    (([-5, -2, 0, 3], 2, -3), [-5, -2]),
    (([1, 2, 3], 0, 2), []),  # degenerate k
]


def solve(arr: list[int], k: int, x: int) -> list[int]:
    return find_closest_elements(arr, k, x)
