"""Design Log Storage System — LeetCode 635."""

from __future__ import annotations

import bisect

META = {
    "pattern": "ood",
    "symbol": "LogSystem",
    "insight": "Zero-padded timestamps sort lexicographically, so a granularity is just a prefix length and a range query is a string comparison.",
    "time": "O(n) to store (a sorted insert), O(log n + matches) to retrieve",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
This one is **premium**, so the statement is not public — described here in my
own words.

Logs arrive as `(id, timestamp)` where the timestamp is the fixed string form
`Year:Month:Day:Hour:Minute:Second`, e.g. `"2017:01:01:23:59:59"`, every field
zero-padded to its natural width.

- `put(id, timestamp)` — store one log.
- `retrieve(start, end, granularity)` — the ids of every log lying inside
  `[start, end]` **inclusive**, where the comparison ignores everything finer
  than `granularity` (one of `Year`, `Month`, `Day`, `Hour`, `Minute`,
  `Second`) on *all three* of start, end and the stored timestamps.

That last clause is the whole problem, and it is worth restating back to the
interviewer, because it is the part candidates assume rather than read: at
`Hour` granularity the query is over whole hours, so a log at `23:59:59` and a
bound of `23:00:00` are the *same* point.

Also ask whether ids are unique and whether output order matters. Neither is
constrained here — insertion order is accepted — but knowing that you may
return them in timestamp order changes the storage choice.
""",
        ),
        (
            "The insight",
            """
The format is doing the work, and noticing that is the answer.

Every field is zero-padded to a fixed width and the fields run coarsest-first,
so **lexicographic order on the raw string is chronological order**. No parsing,
no `datetime`, no comparison of six integers. `"2016:12:31" < "2017:01:01"` as
strings, and it stays true forever because widths never change.

Given that, granularity is nothing but a prefix length — `Year` is 4 characters,
`Month` is 7, each further field adding 3:

```
2017:01:01:23:59:59
^^^^                Year   (4)
^^^^^^^             Month  (7)
^^^^^^^^^^          Day    (10)
```

Truncate the two bounds and each candidate timestamp to that width, and the
whole query collapses to `lo <= ts[:cut] <= hi`.

That gives an O(n) scan per `retrieve`, which is fine at LeetCode's 500 calls
and not fine at a million logs. Keep the logs **sorted by timestamp** and the
truncated range becomes contiguous, so two binary searches find its boundaries
and you touch only matches. The trick that makes `bisect` usable: to bound the
end inclusively at a coarse granularity, pad the truncated `hi` with a
character above every digit and colon — `"~"` works — so `"2017:01" + "~"`
sorts after every timestamp in January 2017 and before February's.

The alternative design, and the one to mention for a write-heavy stream, is a
map per granularity from truncated prefix to a bucket of ids: O(1) exact-prefix
lookup, six times the memory, and no help at all for a range spanning many
prefixes. Ranges are what the API asks for, so ordering beats bucketing.
""",
        ),
        (
            "The boundary that catches people",
            """
Truncation widens the range at **both** ends, and the far end is the one that
surprises. With `end = "2017:01:01:23:00:00"` at `Hour` granularity, a log at
`"2017:01:01:23:59:59"` is included — its truncation is `"2017:01:01:23"`,
equal to the truncated bound. At `Second` granularity the same log is excluded.
An implementation that truncates the stored timestamps but compares them
against the *full* bounds gets the start right and the end wrong, and passes
every test where the end bound happens to fall on a boundary.

The rest:

- **Never build a `datetime`.** Beyond being slower it invites time zones,
  leap seconds and a February 30th that the string form simply never has to
  have an opinion about. The input is a sortable label, not an instant.
- **The padding is load-bearing.** `"2017:1:1"` would break lexicographic
  ordering outright (`"2017:10"` sorts before `"2017:2"`). If a caller might
  send unpadded fields, normalise in `put`, not in `retrieve`.
- **`start > end`** yields an empty result naturally; no branch needed.
- **Duplicate timestamps** are allowed, so the range search must find *all* of
  them — hence bisect-left on the low bound and bisect-right on the sentinel-
  padded high bound, never a single `index` call.
- **The cost of keeping it sorted.** `insort` binary-searches in O(log n) and
  then memmoves in O(n), which is fast in absolute terms but still linear;
  deletion has the same shape. Under a real write rate that is a balanced BST or
  a skip list, or — what log stores actually do — partition by day, append
  within a partition, and drop whole partitions on expiry.
""",
        ),
    ],
}

# Prefix length that isolates each granularity in "Year:Month:Day:Hour:Minute:Second".
CUT = {"Year": 4, "Month": 7, "Day": 10, "Hour": 13, "Minute": 16, "Second": 19}


class LogSystem:
    """Logs kept sorted by timestamp; granularity is a prefix length."""

    def __init__(self) -> None:
        self.logs: list[tuple[str, int]] = []  # (timestamp, id), ordered

    def put(self, id: int, timestamp: str) -> None:
        bisect.insort(self.logs, (timestamp, id))

    def retrieve(self, start: str, end: str, granularity: str) -> list[int]:
        cut = CUT[granularity]
        low = start[:cut]
        # "~" outranks every digit and ":", so this sits just past the last
        # timestamp sharing the truncated end prefix — an inclusive upper bound.
        high = end[:cut] + "~"

        left = bisect.bisect_left(self.logs, (low,))
        right = bisect.bisect_left(self.logs, (high,))
        return [log_id for _, log_id in self.logs[left:right]]


def check() -> None:
    system = LogSystem()
    system.put(1, "2017:01:01:23:59:59")
    system.put(2, "2017:01:01:22:59:59")
    system.put(3, "2016:01:01:00:00:00")

    assert system.retrieve("2016:01:01:01:01:01", "2017:01:01:23:00:00", "Year") == [3, 2, 1]
    # Hour granularity keeps log 1 even though 23:59:59 is past the 23:00:00 bound.
    assert system.retrieve("2016:01:01:01:01:01", "2017:01:01:23:00:00", "Hour") == [2, 1]
    # Second granularity applies the bound literally, and log 1 falls outside it.
    assert system.retrieve("2016:01:01:01:01:01", "2017:01:01:23:00:00", "Second") == [2]
    # The start bound widens too: log 3 sits before 01:01:01 to the second,
    # but inside the same day, so coarsening the granularity pulls it in.
    assert system.retrieve("2016:01:01:01:01:01", "2016:12:31:23:59:59", "Second") == []
    assert system.retrieve("2016:01:01:01:01:01", "2016:12:31:23:59:59", "Day") == [3]

    # Every granularity across one boundary, and exact-point queries.
    edge = LogSystem()
    edge.put(10, "2016:12:31:23:59:59")
    edge.put(20, "2017:01:01:00:00:00")
    assert edge.retrieve("2016:12:31:23:59:59", "2016:12:31:23:59:59", "Second") == [10]
    assert edge.retrieve("2017:01:01:00:00:00", "2017:01:01:00:00:00", "Minute") == [20]
    assert edge.retrieve("2016:01:01:00:00:00", "2016:12:31:00:00:00", "Month") == [10]
    assert edge.retrieve("2016:12:31:23:59:59", "2017:01:01:00:00:00", "Second") == [10, 20]

    # Padding matters: "2017:10" must sort after "2017:02", not before.
    padded = LogSystem()
    padded.put(1, "2017:02:01:00:00:00")
    padded.put(2, "2017:10:01:00:00:00")
    assert padded.retrieve("2017:01:01:00:00:00", "2017:09:30:23:59:59", "Month") == [1]
    assert padded.retrieve("2017:01:01:00:00:00", "2017:12:31:23:59:59", "Month") == [1, 2]

    # Duplicate timestamps must all come back; an inverted range must not.
    dupes = LogSystem()
    dupes.put(7, "2020:05:05:05:05:05")
    dupes.put(8, "2020:05:05:05:05:05")
    dupes.put(9, "2020:05:05:05:05:06")
    assert dupes.retrieve("2020:05:05:05:05:05", "2020:05:05:05:05:05", "Second") == [7, 8]
    assert dupes.retrieve("2020:05:05:05:05:05", "2020:05:05:05:05:06", "Second") == [7, 8, 9]
    assert dupes.retrieve("2020:05:05:05:05:06", "2020:05:05:05:05:05", "Second") == []

    # Nothing stored, and a window that misses everything.
    empty = LogSystem()
    assert empty.retrieve("2000:01:01:00:00:00", "2099:12:31:23:59:59", "Year") == []
