"""Exclusive Time of Functions — LeetCode 636."""

from __future__ import annotations

META = {
    "pattern": "stack",
    "insight": "Only the function on top of the call stack is running, so every log line closes an interval for whoever is on top and opens the next one.",
    "time": "O(n) over the log lines",
    "space": "O(d) for the call stack, plus O(n) for the result",
    "sections": [
        (
            "What it asks",
            """
A single-threaded CPU runs functions that call each other recursively. You get
the log as strings `"id:start:ts"` and `"id:end:ts"`, in chronological order.
Return, per function id, the total time it spent **executing itself** — time
spent inside a callee belongs to the callee, not the caller.

Two questions decide the code:

- **Is an `end` timestamp inclusive?** Yes. `"0:start:5"` followed by
  `"0:end:5"` means function 0 occupied unit 5, so it used **1** unit, not 0.
  This single fact is what the problem is testing.
- **Single-threaded?** Yes — so the calls nest perfectly and a stack is valid.
  On multiple threads the log would interleave and you would need per-thread
  stacks.

You can assume the log is well-formed: every start has a matching end, and the
first line is a start.
""",
        ),
        (
            "The insight",
            """
Because execution is single-threaded and properly nested, at any instant
**exactly one** function is running: the one on top of the call stack. So you
never need to attribute time to more than one id at a time.

Keep a stack of ids and one variable, `prev`, meaning "the first time unit not
yet accounted for". Each log line closes the interval `[prev, ts)` or
`[prev, ts]` for the current top, then moves `prev` forward:

- **start at `ts`** — whoever is on top has been running since `prev`, so give
  them `ts - prev`, push the new id, set `prev = ts`.
- **end at `ts`** — the top ran through `ts` inclusive, so give them
  `ts - prev + 1`, pop, set `prev = ts + 1`.

Recursion needs no special handling at all: the same id can appear twice on the
stack, and `result[id]` simply accumulates from both frames. That is why the
stack holds ids rather than a set.

Parsing is `log.split(":")` into three fields — do not regex it, and do not
assume the id is a single character.
""",
        ),
        (
            "The +1, and how to check you got it right",
            """
The asymmetry is the whole problem, and it is easy to state wrongly under
pressure:

| line | credited | new `prev` |
|---|---|---|
| `start` at `ts` | `ts - prev` | `ts` |
| `end` at `ts` | `ts - prev + 1` | `ts + 1` |

Drop the `+1` and every function loses one unit per completed call. Forget
`prev = ts + 1` and the *next* function is credited with a unit that has
already been spent — double counting, which is worse because the totals still
look plausible.

The self-check to run in your head, and to say out loud: **the sum of the
result must equal the wall clock**, `last_end - first_start + 1`. For
`n = 2, ["0:start:0", "1:start:2", "1:end:5", "0:end:6"]` the answer is
`[3, 4]`, summing to 7, and the clock ran 0 through 6 — 7 units. If those two
numbers disagree, your `+1` is in the wrong place. It costs five seconds and
catches the only bug this problem has.
""",
        ),
    ],
}


def exclusive_time(n: int, logs: list[str]) -> list[int]:
    result = [0] * n
    stack: list[int] = []  # ids; the same id may appear twice under recursion
    prev = 0  # first time unit not yet accounted for

    for log in logs:
        raw_id, kind, raw_ts = log.split(":")
        function_id, timestamp = int(raw_id), int(raw_ts)

        if kind == "start":
            if stack:
                result[stack[-1]] += timestamp - prev  # caller pauses here
            stack.append(function_id)
            prev = timestamp
        else:
            result[stack.pop()] += timestamp - prev + 1  # `end` is inclusive
            prev = timestamp + 1

    return result


CASES = [
    ((2, ["0:start:0", "1:start:2", "1:end:5", "0:end:6"]), [3, 4]),
    ((1, ["0:start:0", "0:start:2", "0:end:5", "0:start:6", "0:end:6", "0:end:7"]), [8]),
    ((2, ["0:start:0", "0:start:2", "0:end:5", "1:start:6", "1:end:6", "0:end:7"]), [7, 1]),
    ((1, ["0:start:0", "0:end:0"]), [1]),  # the +1: one unit, not zero
    ((3, ["0:start:0", "1:start:1", "2:start:2", "2:end:3", "1:end:4", "0:end:5"]), [2, 2, 2]),
    ((2, ["0:start:0", "0:end:4", "1:start:5", "1:end:9"]), [5, 5]),  # no nesting
    ((2, ["1:start:0", "1:end:3"]), [0, 4]),  # a function that never runs
    ((1, []), [0]),
]


def solve(n: int, logs: list[str]) -> list[int]:
    return exclusive_time(n, list(logs))
