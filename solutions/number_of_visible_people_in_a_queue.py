"""Number of Visible People in a Queue — LeetCode 1944."""

from __future__ import annotations

META = {
    "pattern": "monotonic-stack",
    "insight": "Walking right to left, everyone you pop is someone you can see, and the one person who stops the popping is visible too.",
    "time": "O(n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
People stand in a line facing right. Person `i` can see person `j > i` only if
everyone strictly between them is shorter than **both** of them:

```
min(heights[i], heights[j]) > max(heights[i+1 … j-1])
```

Return, for each person, how many people they can see.

Ask: are the heights distinct? On LeetCode yes — but ask anyway, because the
comparison you write depends on the answer, and a good version of the code
does not care either way. Also confirm the direction: nobody looks left.

The rating says Hard; the code is eight lines. The difficulty is entirely in
translating that visibility rule into a stack invariant.
""",
        ),
        (
            "The insight",
            """
Turn the rule around. Walking **right to left**, the only people anyone can
ever see are the *running maxima* to their right — the skyline: the first
person, then the first person taller than them, and so on. Hold that chain on
a stack, heights decreasing bottom to top.

Person `i` then sees a **prefix** of that chain:

- every person on top of the stack shorter than `i` — each one is visible,
  since the taller people that would have hidden them are further back;
- then the first person at least as tall as `i`, who is visible *and* blocks
  everything behind them.

So the loop is: pop while shorter, counting each pop; add one more if anything
survives; push yourself. Everyone you popped is now hidden behind you forever,
which is exactly why the stack stays a valid skyline for the next person left.

Every person is pushed once and popped at most once, so the total pop count
across the whole scan is at most `n` — **O(n)**, even though a single person
may see many.

Contrast with [Daily Temperatures](../daily-temperatures/): there the answer is
a *distance*, so the stack must hold indices. Here it is a *count*, so heights
alone suffice.
""",
        ),
        (
            "The +1, and what the distinct-heights guarantee hides",
            """
**The `+1` is the whole problem.** Returning just the number of pops gives 0
for anyone standing directly in front of someone taller — on
`[10, 6, 8, 5, 11, 9]` the person of height 5 pops nobody but still sees the
11 right in front of them. The expected answer there is `[3, 1, 2, 1, 1, 0]`;
drop the `+1` and you get `[2, 0, 1, 0, 1, 0]`, wrong nearly everywhere.

**Ties are not a one-character fix.** The distinct-heights guarantee is doing
real work, so it is worth knowing what it hides. The rule uses a strict `>`,
so someone of *your exact height* blocks you: popping on `<=` lets a person
see straight past their twin. But plain `<` is not enough either — two equal
heights can then sit on the stack together, and a taller person on the left
pops **both** and counts two people they cannot see. On
`[6, 6, 1, 1, 6, 6, 3, 6]` that returns 3 for index 1 where the answer is 2.

The repair is one line: after counting the first person at least as tall as
you, if their height *equals* yours, drop them from the stack — you now block
them from everyone further left. With distinct heights that branch never
fires, which is why the plain version passes on LeetCode.

Left-to-right is the other trap. It can be made to work by counting how many
people each pop is responsible for, but it is fiddlier and buys nothing —
right-to-left is the natural direction when the question is "what is ahead of
me".
""",
        ),
    ],
}


def can_see_persons_count(heights: list[int]) -> list[int]:
    answer = [0] * len(heights)
    stack: list[int] = []  # heights of the skyline to the right, decreasing bottom -> top

    for i in range(len(heights) - 1, -1, -1):
        height = heights[i]

        while stack and stack[-1] < height:  # strict: an equal height still blocks
            stack.pop()
            answer[i] += 1  # each shorter person ahead is visible

        if stack:
            answer[i] += 1  # the first person at least as tall: seen, then blocking
            if stack[-1] == height:  # only reachable if heights may tie
                stack.pop()  # nobody further left can see past i to an equal height

        stack.append(height)

    return answer


CASES = [
    (([10, 6, 8, 5, 11, 9],), [3, 1, 2, 1, 1, 0]),
    (([5, 1, 2, 3, 10],), [4, 1, 1, 1, 0]),  # one person sees the entire rest
    (([9, 1, 8, 2, 7, 3],), [2, 1, 2, 1, 1, 0]),  # alternating: nobody sees far
    (([1, 2, 3, 4],), [1, 1, 1, 0]),  # increasing: blocked immediately
    (([4, 3, 2, 1],), [1, 1, 1, 0]),  # decreasing: hidden behind the next one
    (([5, 5, 3, 6],), [1, 2, 1, 0]),  # ties block — breaks a `<=` pop
    (([6, 6, 1, 1, 6, 6, 3, 6],), [1, 2, 1, 1, 1, 2, 1, 0]),  # ties beyond the guarantee
    (([7],), [0]),
    (([],), []),
]


def solve(heights: list[int]) -> list[int]:
    return can_see_persons_count(heights)
