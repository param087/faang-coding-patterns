"""Web Crawler Multithreaded — LeetCode 1242."""

from __future__ import annotations

import queue
import threading
import time
from collections import Counter

META = {
    "pattern": "concurrency",
    "symbol": "crawl",
    "insight": "A fixed worker pool over a shared queue, with the visited check and the insert done under one lock so a URL is claimed exactly once.",
    "time": "O(V + E) fetches, wall clock divided by the worker count",
    "space": "O(V)",
    "sections": [
        (
            "What it asks",
            """
*(Premium, so described in my own words rather than quoted.)* You are given a
starting URL and a parser object with one blocking method — hand it a URL, get
back the list of URLs that page links to. Return every URL reachable from the
start whose **hostname is identical** to the start's, in any order. Use
multiple threads: the fetch is slow, so the point is overlapping I/O.

Two clarifying questions do real work. **What counts as the same hostname?** —
exact string match on the `host` part, so `http://a.com` and `http://sub.a.com`
are different sites, and `http://a.com.evil.com` is not `a.com`. And **how many
threads?** — a fixed pool sized to the I/O, not one thread per URL; a graph
with 10⁴ pages would otherwise mean 10⁴ OS threads.
""",
        ),
        (
            "The insight",
            """
This is BFS where the frontier is a `queue.Queue` and the workers are a fixed
pool. The only shared mutable state is the `visited` set, and the entire
correctness of the thing sits in three lines:

```python
with lock:
    if candidate in visited:
        continue
    visited.add(candidate)     # test and insert are ONE atomic step
tasks.put(candidate)
```

Reading `visited`, deciding, and writing must be a **single critical section**.
Split them — check the set, release, then add — and two workers that pull the
same link from two different pages both see it as unvisited, both enqueue it,
and the page gets fetched twice. On a cyclic graph that is not just wasted work:
it is how a crawler ends up looping.

Do the host filter *before* taking the lock. It costs nothing and keeps the
critical section to a hash lookup.
""",
        ),
        (
            "Termination is the hard half",
            """
The bug that fails this question is not the visited set — it is knowing when
you are done. "Workers exit when the queue is empty" is wrong, and it is wrong
in a way that passes small tests: on a **chain** `a → b → c → …`, the queue is
empty for a moment after every single fetch, because the one worker holding a
URL has not produced its children yet. Seven of your eight workers exit inside
the first millisecond, and on a linear graph of 200 pages you have silently
degraded to single-threaded — or, if the main thread also checks emptiness, you
return after crawling one page.

`Queue.join()` is the right primitive: it blocks until every item has been
matched by a `task_done()`, so "empty **and** nothing in flight". Call
`task_done()` in a `finally`, or one raised exception from the parser hangs the
whole crawl. Then push one `None` sentinel per worker to retire the pool —
daemon threads that are never retired keep the interpreter's thread table
growing across calls.

The alternative — an atomic in-flight counter plus a condition variable — is
the same idea written out longhand, and worth naming if the interviewer wants
to see you not reach for the standard library.
""",
        ),
    ],
}


class HtmlParser:
    """The interface the judge supplies; here it is backed by a fixed graph."""

    def __init__(self, edges: dict[str, list[str]], latency: float = 0.0) -> None:
        self._edges = edges
        self._latency = latency  # stands in for the network round trip
        self._lock = threading.Lock()
        self.fetches: Counter[str] = Counter()

    def get_urls(self, url: str) -> list[str]:
        with self._lock:
            self.fetches[url] += 1
        if self._latency:
            time.sleep(self._latency)
        return list(self._edges.get(url, []))


def _hostname(url: str) -> str:
    # "http://news.yahoo.com/us" -> ["http:", "", "news.yahoo.com", "us"]
    parts = url.split("/")
    return parts[2] if len(parts) > 2 else ""


def crawl(start_url: str, html_parser: HtmlParser, workers: int = 8) -> list[str]:
    host = _hostname(start_url)
    visited = {start_url}
    lock = threading.Lock()
    tasks: queue.Queue[str | None] = queue.Queue()
    tasks.put(start_url)

    def worker() -> None:
        while True:
            url = tasks.get()
            try:
                if url is None:
                    return
                for candidate in html_parser.get_urls(url):
                    if _hostname(candidate) != host:
                        continue  # filter outside the lock: it is free
                    with lock:
                        if candidate in visited:
                            continue
                        visited.add(candidate)  # test-and-insert, atomically
                    tasks.put(candidate)
            finally:
                tasks.task_done()  # finally, or one bad page hangs join()

    pool = [threading.Thread(target=worker, daemon=True) for _ in range(workers)]
    for thread in pool:
        thread.start()

    tasks.join()  # empty AND nothing in flight — not the same as empty
    for _ in pool:
        tasks.put(None)
    for thread in pool:
        thread.join(timeout=10)

    return sorted(visited)  # any order is accepted; sorted makes it testable


_CHAIN = {f"http://a.com/{i}": [f"http://a.com/{i + 1}"] for i in range(40)}

CASES = [
    # Cycle back to the start, plus an off-host link that must be dropped.
    (
        (
            {
                "http://news.yahoo.com/news/topics/": [
                    "http://news.yahoo.com",
                    "http://news.yahoo.com/us",
                ],
                "http://news.yahoo.com": ["http://news.yahoo.com/news/topics/"],
                "http://news.yahoo.com/us": ["http://news.google.com"],
                "http://news.google.com": ["http://news.yahoo.com"],
            },
            "http://news.yahoo.com/news/topics/",
        ),
        [
            "http://news.yahoo.com",
            "http://news.yahoo.com/news/topics/",
            "http://news.yahoo.com/us",
        ],
    ),
    # Self-loop and a duplicate link: the visited set must absorb both.
    (
        ({"http://a.com": ["http://a.com", "http://a.com", "http://a.com/x"]}, "http://a.com"),
        ["http://a.com", "http://a.com/x"],
    ),
    # Hostname is an exact match, not a prefix and not a suffix.
    (
        (
            {
                "http://a.com": [
                    "http://sub.a.com/x",
                    "http://a.com.evil.com/y",
                    "http://a.com/ok",
                ]
            },
            "http://a.com",
        ),
        ["http://a.com", "http://a.com/ok"],
    ),
    # Every link is off-host.
    (
        ({"http://a.com": ["http://b.com/x", "http://b.com/y"]}, "http://a.com"),
        ["http://a.com"],
    ),
    # The start URL is not even in the graph: the parser returns nothing.
    (({}, "http://a.com/lonely"), ["http://a.com/lonely"]),
    # A chain 40 deep with 8 workers: the queue is momentarily empty after every
    # fetch, so anything that returns on "queue is empty" stops after one page.
    ((_CHAIN, "http://a.com/0"), sorted(f"http://a.com/{i}" for i in range(41))),
]


def solve(edges: dict[str, list[str]], start_url: str) -> list[str]:
    return crawl(start_url, HtmlParser(edges))


def check() -> None:
    for index, (args, expected) in enumerate(CASES):
        assert solve(*args) == expected, f"case {index}"

    # A page must be fetched exactly once, however the diamond is traversed.
    diamond = {
        "http://a.com": ["http://a.com/l", "http://a.com/r"],
        "http://a.com/l": ["http://a.com/end"],
        "http://a.com/r": ["http://a.com/end"],
        "http://a.com/end": ["http://a.com"],
    }
    for _ in range(20):
        parser = HtmlParser(diamond)
        result = crawl("http://a.com", parser)
        assert result == sorted(diamond)
        assert set(parser.fetches.values()) == {1}, parser.fetches

    # The pool must actually overlap the I/O — a correct-but-serial crawler
    # returns the right answer, which is why this needs a clock and not an
    # equality check. 33 fetches at 2 ms is 66 ms serially, ~10 ms on 8 workers.
    star = {"http://a.com": [f"http://a.com/{i}" for i in range(32)]}
    slow = HtmlParser(star, latency=0.002)
    started = time.perf_counter()
    assert len(crawl("http://a.com", slow, workers=8)) == 33
    elapsed = time.perf_counter() - started
    assert elapsed < 0.035, f"{elapsed:.3f}s — the workers are not running concurrently"
