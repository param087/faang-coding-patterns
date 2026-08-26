"""Design Browser History — LeetCode 1472."""

from __future__ import annotations

META = {
    "pattern": "design",
    "symbol": "BrowserHistory",
    "insight": "One array plus a cursor: back and forward are clamped index arithmetic, and visiting simply shortens the array.",
    "time": "O(1) for visit, O(1) for back and forward",
    "space": "O(visited pages)",
    "sections": [
        (
            "What it asks",
            """
A browser tab starting on a homepage, with `visit(url)`, `back(steps)` and
`forward(steps)`. Both movements are **clamped**: asking to go back further
than the history allows lands you on the oldest page rather than failing, and
each returns the URL you end up on.

The clarifying question that decides the design: **what does `visit` do to the
forward history?** It clears it — after going back and then visiting, the pages
you had gone back from are unreachable. Confirm that out loud; a candidate who
does not will write a `forward` that resurrects dead pages.
""",
        ),
        (
            "The insight",
            """
The reflex answer is two stacks — a back stack and a forward stack, moving one
URL across on each step. It is correct, and `visit` is a one-liner
(`forward.clear()`), but `back(steps)` becomes a loop of `steps` pops and
pushes, and the bookkeeping around "which stack holds the current page" is
where people lose five minutes.

**One array and a cursor is strictly better.** The history is a line; back and
forward are moves along it:

```
index = max(0, index - steps)
index = min(last, index + steps)
```

Both are O(1) regardless of `steps`, which matters because `steps` can be 100
in the constraints and unbounded in the follow-up. Clamping is `max`/`min`, not
an `if` chain.

`visit` truncates: everything after the cursor is gone. Rather than deleting a
suffix, keep a `last` marker and **overwrite in place**, so a long forward
history is discarded in O(1) and the array is reused:

```
index += 1
if index < len(pages): pages[index] = url
else: pages.append(url)
last = index
```

That is the difference between an O(n) `visit` and an O(1) one, and it is the
same trick a real browser uses — the entries are still there, they are just no
longer addressable.
""",
        ),
        (
            "Where it goes wrong",
            """
- **Clamping to the wrong bound.** `forward` must stop at `last`, the newest
  *live* page, not at `len(pages) - 1` — otherwise a stale entry left over from
  a truncated branch comes back to life. This is the single bug that this
  problem exists to catch, and it only shows up in the sequence
  visit → back → visit → forward.
- **`back(0)` and `forward(0)`** must return the current page, not move.
- **Back past the homepage** returns the homepage. No exception, no `None`.
- **Repeated visits to the same URL** are distinct history entries; do not
  deduplicate.
- Follow-up worth naming: real browsers cap history depth, which turns the array
  into a **deque with a maximum length** — and then the cursor has to be
  adjusted every time the oldest entry is dropped.
""",
        ),
    ],
}


class BrowserHistory:
    def __init__(self, homepage: str) -> None:
        self.pages = [homepage]
        self.index = 0  # cursor: the page currently displayed
        self.last = 0  # newest *live* entry; entries beyond it are dead

    def visit(self, url: str) -> None:
        self.index += 1
        if self.index < len(self.pages):
            self.pages[self.index] = url  # overwrite instead of truncating
        else:
            self.pages.append(url)
        self.last = self.index  # forward history is now unreachable

    def back(self, steps: int) -> str:
        self.index = max(0, self.index - steps)  # clamp, do not fail
        return self.pages[self.index]

    def forward(self, steps: int) -> str:
        self.index = min(self.last, self.index + steps)  # `last`, not len - 1
        return self.pages[self.index]


def check() -> None:
    history = BrowserHistory("leetcode.com")
    history.visit("google.com")
    history.visit("facebook.com")
    history.visit("youtube.com")
    assert history.back(1) == "facebook.com"
    assert history.back(1) == "google.com"
    assert history.forward(1) == "facebook.com"
    history.visit("linkedin.com")  # kills youtube.com
    assert history.forward(2) == "linkedin.com"  # clamped: nothing ahead
    assert history.back(2) == "google.com"
    assert history.back(7) == "leetcode.com"  # clamped at the homepage

    # The bug this problem exists to catch: a truncated entry must stay dead.
    stale = BrowserHistory("a")
    stale.visit("b")
    stale.visit("c")
    assert stale.back(2) == "a"
    stale.visit("d")
    assert stale.forward(5) == "d"  # not "c", which is still in the array
    assert stale.back(1) == "a"
    assert stale.forward(1) == "d"

    # Zero steps and movement on a fresh tab.
    fresh = BrowserHistory("home")
    assert fresh.back(0) == "home"
    assert fresh.forward(0) == "home"
    assert fresh.back(10) == "home"
    assert fresh.forward(10) == "home"

    # Repeat visits are distinct entries, not deduplicated.
    repeats = BrowserHistory("x")
    repeats.visit("y")
    repeats.visit("y")
    assert repeats.back(1) == "y"
    assert repeats.back(1) == "x"
    assert repeats.forward(2) == "y"

    # Large step counts are O(1), not a loop.
    deep = BrowserHistory("p0")
    for page in range(1, 1001):
        deep.visit(f"p{page}")
    assert deep.back(10**9) == "p0"
    assert deep.forward(10**9) == "p1000"
