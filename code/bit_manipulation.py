"""Bit manipulation.

Two facts do most of the work. **XOR cancels**: `a ^ a == 0` and `a ^ 0 == a`,
so anything appearing twice vanishes. And **an integer is a set**: bit i means
"element i is present", which is what makes subset enumeration a counting loop.
"""

from __future__ import annotations


def single_number(nums: list[int]) -> int:
    """The one value appearing once when every other appears twice.

    XOR everything. Pairs cancel and the loner survives. O(n) time, O(1)
    space, which is what the follow-up demands after you offer the hash map.
    """
    result = 0
    for value in nums:
        result ^= value
    return result


def single_number_ii(nums: list[int]) -> int:
    """The value appearing once when every other appears three times.

    XOR no longer works — three copies leave one behind. Count each bit
    position mod 3 instead: bits belonging to the triples vanish, and what
    remains is the answer. The sign fix-up is needed because Python integers
    are unbounded, so a "negative" 32-bit pattern must be interpreted.
    """
    result = 0
    for shift in range(32):
        total = sum((value >> shift) & 1 for value in nums)
        if total % 3:
            result |= 1 << shift

    # Reinterpret bit 31 as the sign, since Python has no 32-bit int.
    return result - (1 << 32) if result >= (1 << 31) else result


def count_bits(n: int) -> list[int]:
    """Popcount for every integer from 0 to n, in O(n).

    `i >> 1` is `i` with the last bit removed, and that value is already
    computed. So `bits[i] = bits[i >> 1] + (i & 1)`. Calling popcount n times
    would be O(n log n); this is the DP that removes the log.
    """
    bits = [0] * (n + 1)
    for i in range(1, n + 1):
        bits[i] = bits[i >> 1] + (i & 1)
    return bits


def missing_number(nums: list[int]) -> int:
    """The absent value in 0..n.

    XOR the indices and the values together: everything present cancels
    against its index, leaving the missing one. The Gauss-sum solution is
    equally valid and risks overflow in fixed-width languages — worth saying.
    """
    result = len(nums)
    for i, value in enumerate(nums):
        result ^= i ^ value
    return result


def get_sum(a: int, b: int) -> int:
    """Add two integers without `+`.

    `a ^ b` is the sum ignoring carries; `(a & b) << 1` is the carries.
    Repeat until nothing carries. The masking is Python-specific: integers
    are unbounded, so negatives must be forced into 32 bits by hand.
    """
    mask = 0xFFFFFFFF
    a, b = a & mask, b & mask

    while b:
        carry = ((a & b) << 1) & mask
        a = (a ^ b) & mask
        b = carry

    return a if a <= 0x7FFFFFFF else ~(a ^ mask)


def subsets_via_bits(nums: list[int]) -> list[list[int]]:
    """Every subset, by counting from 0 to 2^n - 1.

    Each integer *is* a subset: bit i means "include nums[i]". This is the
    concrete reason a constraint of n <= 20 signals bitmask — 2^20 is a
    million, which is fine, and 2^30 is not.
    """
    n = len(nums)
    result: list[list[int]] = []
    for mask in range(1 << n):
        result.append([nums[i] for i in range(n) if mask & (1 << i)])
    return result


CASES = [
    (([2, 2, 1],), 1),
    (([4, 1, 2, 1, 2],), 4),
    (([1],), 1),
    (([],), 0),
]


def solve(nums: list[int]) -> int:
    return single_number(nums)


def check() -> None:
    for args, expected in CASES:
        assert single_number(*args) == expected

    assert single_number_ii([2, 2, 3, 2]) == 3
    assert single_number_ii([0, 1, 0, 1, 0, 1, 99]) == 99
    assert single_number_ii([-2, -2, 1, -2]) == 1  # the sign fix-up

    assert count_bits(5) == [0, 1, 1, 2, 1, 2]
    assert count_bits(0) == [0]

    assert missing_number([3, 0, 1]) == 2
    assert missing_number([0, 1]) == 2
    assert missing_number([9, 6, 4, 2, 3, 5, 7, 0, 1]) == 8

    assert get_sum(1, 2) == 3
    assert get_sum(2, 3) == 5
    assert get_sum(-1, 1) == 0
    assert get_sum(-2, -3) == -5

    assert len(subsets_via_bits([1, 2, 3])) == 8
    assert sorted(subsets_via_bits([1, 2])) == [[], [1], [1, 2], [2]]
