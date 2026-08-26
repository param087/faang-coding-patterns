"""Asteroid Collision — LeetCode 735."""

from __future__ import annotations

META = {
    "pattern": "stack",
    "insight": "A left-moving asteroid only ever meets the right-movers behind it, most recent first — which is precisely a stack pop loop.",
    "time": "O(n)",
    "space": "O(n) for the output; O(1) beyond it",
    "sections": [
        (
            "What it asks",
            """
An array where the sign is direction (positive → right, negative → left) and
the magnitude is size. All asteroids move at the **same speed**, so two of them
meet only when a right-mover sits immediately to the left of a left-mover. The
larger survives; equal sizes annihilate each other. Return the survivors, in
their original relative order.

Three clarifications worth spending ten seconds on:

- **Can a value be zero?** No — which is why sign alone determines direction.
- **Do same-direction asteroids ever collide?** No, same speed. This is the
  fact the whole solution rests on: `[-2, -1]` and `[1, 2]` are already stable.
- **Is the output order the input order?** Yes, so build the answer in place
  rather than sorting anything at the end.
""",
        ),
        (
            "The simulation you would write first",
            """
Scan the array for an adjacent `(+, -)` pair, resolve it, and start over
because the deletion may have created a new pair. Each round removes at least
one asteroid, so at most n rounds of an O(n) scan: **O(n²)**.

At n = 10⁴ that is 10⁸ comparisons, and worse, every removal from a Python list
is itself an O(n) memmove — so the real constant is far uglier than the
exponent suggests. `[1, 1, 1, ..., 1, -2]` is the shape that hits it: one
enormous left-mover chewing through the whole array, one restart per bite.

It is a correct answer and worth naming in ten seconds. Then throw it away.
""",
        ),
        (
            "The insight",
            """
That restart is doing no new work. When an asteroid explodes, the only pair
that can newly become adjacent is the one **just behind** it — the most recent
surviving right-mover. "Most recent survivor" is a stack.

So keep a stack of asteroids that are still alive, in order. For each incoming
asteroid:

- if it is moving **right**, nothing behind it can ever catch it — push;
- if it is moving **left**, it collides with the top of the stack for exactly
  as long as that top is a **right**-mover.

The second condition is the load-bearing one. A negative on top of the stack is
already flying away to the left, so it can never be hit, and the loop stops
there. That single `stack[-1] > 0` test is why the answer is linear: every
asteroid is pushed once and popped at most once.
""",
        ),
        (
            "The three outcomes, and the flag",
            """
Inside the collision loop the comparison has three branches and they do *not*
all end the loop:

| top vs incoming | what happens | loop continues? |
|---|---|---|
| top smaller | top explodes | **yes** — the incoming one keeps going |
| equal | both explode | no |
| top larger | incoming explodes | no |

That asymmetry is the bug factory. The incoming asteroid can survive several
collisions and *still* end up on the stack, so you cannot decide whether to
push it before the loop finishes — hence an explicit `alive` flag (or a
`for ... else`, or a `break` plus checking why you left). Two failures show up
constantly in interviews:

- pushing the incoming asteroid unconditionally after the loop, which
  resurrects one that just exploded;
- treating "equal" as "top explodes", which leaves the incoming one alive.

Also note the loop guard tests `alive` first: once the incoming asteroid is
dead it must stop popping, even if more right-movers remain beneath.
""",
        ),
        (
            "Dry run",
            """
`[5, 10, -5, -10, -20]`

- `5`, `10` → both positive, stack is `[5, 10]`.
- `-5` → top `10` is positive and 10 > 5, so `-5` explodes. Stack `[5, 10]`.
- `-10` → top `10` is positive and 10 == 10, **both** explode. Stack `[5]`.
- `-20` → top `5` is positive and 5 < 20, so `5` explodes and the loop
  *continues*; now the stack is empty, so `-20` survives and is pushed.

Result `[-20]`. Every one of the three branches fires, and the last step is the
one that catches a solution which pushes or drops the incoming asteroid too
early.

Contrast `[10, 2, -5]`: `-5` pops `2`, then meets `10`, loses, and is never
pushed → `[10]`.
""",
        ),
        (
            "Follow-ups",
            """
- **Different speeds.** The stack argument collapses, because a fast asteroid
  can catch one ahead of it. Now you compute collision *times* and process them
  in order — a heap, not a stack. Say this if asked; it is the standard probe
  for whether you understood *why* the stack worked.
- **A stream rather than an array.** The algorithm is already online: the stack
  is the entire state, and it is exactly the set of asteroids that could still
  be hit.
- **Same family:** Car Fleet (735's cousin, where the stack holds arrival
  times) and Remove K Digits — both are "a new element destroys some suffix of
  the survivors".
""",
        ),
    ],
}


def asteroid_collision(asteroids: list[int]) -> list[int]:
    stack: list[int] = []

    for asteroid in asteroids:
        alive = True
        # Only a left-mover collides, and only with right-movers behind it.
        while alive and asteroid < 0 and stack and stack[-1] > 0:
            if stack[-1] < -asteroid:
                stack.pop()  # top explodes; the incoming one keeps going
            elif stack[-1] == -asteroid:
                stack.pop()  # both explode
                alive = False
            else:
                alive = False  # the incoming one explodes
        if alive:
            stack.append(asteroid)

    return stack


CASES = [
    (([5, 10, -5],), [5, 10]),
    (([8, -8],), []),  # equal sizes annihilate
    (([10, 2, -5],), [10]),  # survives one collision, loses the next
    (([5, 10, -5, -10, -20],), [-20]),  # all three branches
    (([-2, -1, 1, 2],), [-2, -1, 1, 2]),  # nothing ever meets
    (([1, -2, -2, -2],), [-2, -2, -2]),  # a negative on top is never hit
    (([-2, -2, 1, -1],), [-2, -2]),
    (([],), []),
]


def solve(asteroids: list[int]) -> list[int]:
    return asteroid_collision(list(asteroids))
