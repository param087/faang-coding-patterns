"""Math and geometry.

Mostly a set of small facts you either have or do not. The ones that actually
recur: fast exponentiation, the sieve, gcd, and the observation that comparing
slopes with division loses precision so you should compare with cross products
or normalised fractions instead.
"""

from __future__ import annotations

from collections import defaultdict
from math import gcd


def my_pow(base: float, exponent: int) -> float:
    """x^n by binary exponentiation, O(log n).

    Squaring halves the exponent each round, so 2^30 takes 30 multiplications
    rather than a billion. The negative case inverts once at the start —
    doing it at the end loses precision.
    """
    if exponent < 0:
        base, exponent = 1 / base, -exponent

    result = 1.0
    while exponent:
        if exponent & 1:
            result *= base
        base *= base
        exponent >>= 1

    return result


def count_primes(n: int) -> int:
    """Primes strictly below n — sieve of Eratosthenes, O(n log log n).

    Two optimisations worth stating: start crossing out at `p*p`, because
    every smaller multiple already has a smaller factor; and stop the outer
    loop at sqrt(n) for the same reason.
    """
    if n < 3:
        return 0

    is_prime = [True] * n
    is_prime[0] = is_prime[1] = False

    p = 2
    while p * p < n:
        if is_prime[p]:
            for multiple in range(p * p, n, p):
                is_prime[multiple] = False
        p += 1

    return sum(is_prime)


def max_points_on_a_line(points: list[tuple[int, int]]) -> int:
    """Most points sharing a straight line.

    Fix one point, group the rest by slope. The important part is **not**
    using `dy / dx`: floating point makes 1/3 and 2/6 unequal, and vertical
    lines divide by zero. Normalising `(dy, dx)` by their gcd, with a fixed
    sign convention, is exact.
    """
    if len(points) <= 2:
        return len(points)

    best = 0
    for i, (x1, y1) in enumerate(points):
        slopes: dict[tuple[int, int], int] = defaultdict(int)
        for x2, y2 in points[i + 1 :]:
            dy, dx = y2 - y1, x2 - x1
            divisor = gcd(dy, dx) or 1
            dy, dx = dy // divisor, dx // divisor
            if dx < 0 or (dx == 0 and dy < 0):
                dy, dx = -dy, -dx  # one canonical direction per line
            slopes[(dy, dx)] += 1
            best = max(best, slopes[(dy, dx)])

    return best + 1  # plus the fixed point itself


def reverse_integer(x: int) -> int:
    """Reverse the digits, returning 0 on 32-bit overflow.

    The overflow check is the entire question — the reversal is trivial.
    Python will not overflow on its own, so the bound must be applied by
    hand, and the same is true of the sign handling.
    """
    limit = 2**31
    sign = -1 if x < 0 else 1
    reversed_digits = int(str(abs(x))[::-1]) * sign
    return 0 if reversed_digits < -limit or reversed_digits >= limit else reversed_digits


def is_happy(n: int) -> bool:
    """Does repeatedly summing squared digits reach 1?

    Any non-happy number enters a cycle, so this is cycle detection wearing a
    number-theory hat — Floyd's tortoise and hare works, and so does a seen
    set. Recognising the cycle is what makes it terminate.
    """
    seen: set[int] = set()

    while n != 1 and n not in seen:
        seen.add(n)
        n = sum(int(digit) ** 2 for digit in str(n))

    return n == 1


CASES = [
    ((2.0, 10), 1024.0),
    ((2.0, -2), 0.25),
    ((2.0, 0), 1.0),
    ((1.0, 1000000), 1.0),
]


def solve(base: float, exponent: int) -> float:
    return my_pow(base, exponent)


def check() -> None:
    for args, expected in CASES:
        assert abs(my_pow(*args) - expected) < 1e-9

    assert count_primes(10) == 4  # 2, 3, 5, 7
    assert count_primes(0) == 0
    assert count_primes(2) == 0
    assert count_primes(100) == 25

    assert max_points_on_a_line([(1, 1), (2, 2), (3, 3)]) == 3
    assert max_points_on_a_line([(1, 1), (3, 2), (5, 3), (4, 1), (2, 3), (1, 4)]) == 4
    assert max_points_on_a_line([(0, 0), (0, 1), (0, 2)]) == 3  # vertical
    assert max_points_on_a_line([(1, 1)]) == 1

    assert reverse_integer(123) == 321
    assert reverse_integer(-123) == -321
    assert reverse_integer(120) == 21
    assert reverse_integer(1534236469) == 0  # overflows

    assert is_happy(19) is True
    assert is_happy(2) is False
    assert is_happy(1) is True
