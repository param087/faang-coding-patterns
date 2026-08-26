"""Single-Threaded CPU — LeetCode 1834."""

from __future__ import annotations

from heapq import heappop, heappush

META = {
    "pattern": "heaps",
    "insight": "Arrival order decides what is visible; a min-heap on (duration, original index) decides what runs, and the clock leaps over idle gaps.",
    "time": "O(n log n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Each task is `[enqueueTime, processingTime]`. One CPU, no preemption. Whenever
the CPU is free it takes the **shortest** task among those already enqueued,
breaking ties by smallest **original index**; if nothing has arrived it idles
until something does. Return the order in which tasks run, as original indices.

Worth asking up front:

- **Can a running task be interrupted by a shorter arrival?** No — this is
  non-preemptive shortest-job-first. If it were preemptive the whole shape of
  the answer changes.
- **Ties broken by index in the input, or by arrival order?** Input index. That
  distinction is the difference between a correct heap key and a wrong one once
  you have sorted the array.
- **A task arriving at exactly the instant the CPU frees up — eligible?** Yes.
  So the admission test is `enqueue <= now`, not `<`.
""",
        ),
        (
            "The insight",
            """
Two orderings are in play and they are not the same one, which is why a single
sort cannot do it:

- **arrival order** decides *when* a task becomes visible;
- **duration order** decides *which* visible task runs.

So run a pointer and a heap side by side. Sort tasks by enqueue time and keep an
index `i` into that sorted array. At every decision point, admit everything with
`enqueue <= now` into a min-heap keyed by `(processingTime, originalIndex)`, then
pop one and advance the clock by its duration.

The wrong first answer is to sort by `(processingTime, index)` and emit that.
It fails the moment a short task arrives *after* a long one has already been
forced to start: `[[0,1],[1,1000],[2,1]]`. The global sort says `[0, 2, 1]`, but
at time 1 the only enqueued task is the 1000-unit one, so the CPU is committed
to it and the true answer is `[0, 1, 2]`.

Each task is pushed once and popped once, so the heap work is O(n log n) and
the sort is the same — total **O(n log n)**, O(n) space.
""",
        ),
        (
            "The index you push and the clock you forget",
            """
Three bugs account for nearly every failed submission here.

**1. Pushing the sorted position instead of the original index.** After sorting,
position in the array is meaningless — both the tie-break rule and the required
output are stated in terms of the original index. Carry it through the sort:
`(enqueue, processing, i)`.

**2. Not jumping the clock over idle time.** When the heap empties but tasks
remain, `now` must leap to the next enqueue time. Ticking `now += 1` instead is
correct but with enqueue times up to 10⁹ that is a billion-iteration loop that
times out on a single-task gap.

**3. `<` instead of `<=` when admitting.** A task enqueued at exactly the
moment the CPU frees is available, and LeetCode's own test data leans on it.

Two more worth a sentence in an interview: the clock is a running sum, so with
10⁵ tasks × 10⁹ processing time it reaches ~10¹⁴ — fine in Python, but it
overflows 32-bit `int` in Java or C++, so use `long`. And starting `now` at 0
rather than the earliest enqueue time is harmless only because the idle jump
handles the first gap for you.
""",
        ),
    ],
}


def get_order(tasks: list[list[int]]) -> list[int]:
    # (enqueue, processing, original index) — the original index must survive the sort.
    arrivals = sorted((enqueue, processing, i) for i, (enqueue, processing) in enumerate(tasks))

    n = len(arrivals)
    order: list[int] = []
    ready: list[tuple[int, int]] = []  # (processing, original index)
    now = 0
    i = 0

    while len(order) < n:
        while i < n and arrivals[i][0] <= now:  # <= : arrives exactly as the CPU frees
            _, processing, index = arrivals[i]
            heappush(ready, (processing, index))
            i += 1

        if not ready:
            now = arrivals[i][0]  # idle: leap to the next arrival, never tick by 1
            continue

        processing, index = heappop(ready)
        now += processing  # non-preemptive: committed until it finishes
        order.append(index)

    return order


CASES = [
    (([[1, 2], [2, 4], [3, 2], [4, 1]],), [0, 2, 3, 1]),
    (([[7, 10], [7, 12], [7, 5], [7, 4], [7, 2]],), [4, 3, 2, 0, 1]),
    (([[0, 1], [1, 1000], [2, 1]],), [0, 1, 2]),  # global sort by duration says [0, 2, 1]
    (([[1, 2], [10, 1]],), [0, 1]),  # idle jump
    (([[3, 1], [1, 1], [2, 1]],), [1, 2, 0]),  # all durations equal, arrival decides
    (([[0, 2], [0, 2], [0, 1]],), [2, 0, 1]),  # duplicate durations, tie-break on index
    (([[100, 5]],), [0]),
    (([],), []),
]


def solve(tasks: list[list[int]]) -> list[int]:
    return get_order([list(task) for task in tasks])
