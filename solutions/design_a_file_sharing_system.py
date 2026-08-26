"""Design a File Sharing System — LeetCode 1500."""

from __future__ import annotations

import heapq

META = {
    "pattern": "ood",
    "symbol": "FileSharing",
    "insight": "Two problems wearing one costume: recycle the smallest free user id from a min-heap, and keep chunk ownership as a two-way index.",
    "time": "O(log u) to join or leave, O(k log k) to request a chunk owned by k users",
    "space": "O(total chunks owned)",
    "sections": [
        (
            "What it asks",
            """
This one is **premium**, so the statement is not public — described here in my
own words.

A file is split into `m` numbered chunks and users swarm it:

- `join(ownedChunks)` — a user arrives holding some chunks already; assign and
  return the **smallest unused positive integer** as their id.
- `leave(userId)` — the user departs and stops owning anything; their id
  becomes available again.
- `request(userId, chunkId)` — return the sorted ids of everyone who currently
  has that chunk. If that list is non-empty, the requester now owns the chunk
  too.

Ask what "smallest unused" means precisely, because it is the entire first
half of the problem: ids are recycled on leave, so after users 1, 2, 3 join and
1 and 2 leave, the next joiner is **1**, not 4. Also ask whether a request for a
chunk nobody holds still grants ownership (no — a peer-to-peer download that
found no seeder transferred nothing).
""",
        ),
        (
            "The insight",
            """
Two independent sub-problems, and interviews are lost by fusing them.

**Id allocation is a free-list.** Scanning `1, 2, 3, ...` for the first
unassigned id is O(u) per join and 10⁴ joins against 10⁴ users is 10⁸
comparisons. Instead keep a min-heap of *released* ids and a high-water mark:
pop the heap when it has anything, otherwise hand out `next_id` and increment.
The heap only ever holds ids below the mark, so "smallest free" is either the
heap's minimum or the mark itself — nothing else can be free. O(log u).

**Ownership is a two-way index.** `owners[chunk]` is the set of users holding a
chunk, `chunks_of[user]` the set a user holds. `request` needs the first
direction; `leave` needs the second, to know which owner-sets to erase the
departing user from without touching all `m` chunks. Maintaining both is the
price of both operations being cheap, and forgetting one is the usual bug —
`leave` that only drops `chunks_of[user]` leaves ghosts seeding forever.

The sort in `request` is genuine work, not laziness: the sets are unordered and
the contract asks for ascending ids.
""",
        ),
        (
            "Edge cases",
            """
- **A request that finds nobody** returns `[]` and grants nothing. Guard on the
  empty result *before* mutating, or you create an owner of a chunk that no
  longer exists anywhere in the swarm.
- **Requesting a chunk you already own** returns a list that includes you, and
  adding it again is a no-op on a set. Worth saying out loud, because with
  lists it would double-count.
- **`leave` on an id that never joined**, or twice in a row: it must not push a
  duplicate onto the free heap, or the same id gets handed to two users. The
  membership check is what keeps the heap's entries distinct.
- **A joiner owning zero chunks** — the common case, a fresh downloader. Their
  id still has to be allocated and recycled.
- **Chunk ids out of range** are excluded by the constraints; if they were not,
  validate in `join` rather than at every `request`.
- **Concurrency**, the follow-up that always comes: `join` is a
  read-modify-write on the allocator and needs a lock or an atomic counter. Ids
  handed out under contention must still be unique — that, not the ordering, is
  the property to defend.
""",
        ),
    ],
}


class FileSharing:
    """A recycling id allocator plus a user <-> chunk index."""

    def __init__(self, m: int) -> None:
        self.m = m
        self.released: list[int] = []  # min-heap of ids below the high-water mark
        self.next_id = 1
        self.chunks_of: dict[int, set[int]] = {}
        self.owners: dict[int, set[int]] = {chunk: set() for chunk in range(1, m + 1)}

    def join(self, ownedChunks: list[int]) -> int:
        if self.released:
            user = heapq.heappop(self.released)
        else:
            user = self.next_id
            self.next_id += 1

        self.chunks_of[user] = set(ownedChunks)
        for chunk in ownedChunks:
            self.owners[chunk].add(user)
        return user

    def leave(self, userId: int) -> None:
        chunks = self.chunks_of.pop(userId, None)
        if chunks is None:
            return  # never joined, or already left: do not free the id twice
        for chunk in chunks:
            self.owners[chunk].discard(userId)
        heapq.heappush(self.released, userId)

    def request(self, userId: int, chunkId: int) -> list[int]:
        holders = sorted(self.owners[chunkId])
        if holders and userId in self.chunks_of:
            # A transfer only happened if someone was seeding it.
            self.owners[chunkId].add(userId)
            self.chunks_of[userId].add(chunkId)
        return holders


def check() -> None:
    swarm = FileSharing(4)
    assert swarm.join([1, 2]) == 1
    assert swarm.join([2, 3]) == 2
    assert swarm.join([4]) == 3

    assert swarm.request(1, 3) == [2]  # user 1 downloads chunk 3 from user 2
    assert swarm.request(2, 2) == [1, 2]  # already an owner; still listed

    swarm.leave(1)
    assert swarm.request(2, 1) == []  # the only seeder of chunk 1 has gone

    assert swarm.join([]) == 1  # id 1 recycled, not 4

    # User 1 really did acquire chunk 3 before leaving; the new user 1 has not.
    assert swarm.request(3, 3) == [2]

    # Leaving twice must not release the id twice.
    reuse = FileSharing(3)
    assert reuse.join([1]) == 1
    assert reuse.join([2]) == 2
    reuse.leave(2)
    reuse.leave(2)
    reuse.leave(99)  # never joined
    assert reuse.join([]) == 2
    assert reuse.join([]) == 3  # the high-water mark, not a stale free id

    # Ids are handed back in ascending order, whatever order they were released.
    order = FileSharing(2)
    for _ in range(5):
        order.join([])
    order.leave(4)
    order.leave(2)
    order.leave(5)
    assert order.join([]) == 2
    assert order.join([]) == 4
    assert order.join([]) == 5
    assert order.join([]) == 6

    # A request grants ownership, so the next requester sees two seeders.
    seed = FileSharing(2)
    assert seed.join([1]) == 1
    assert seed.join([]) == 2
    assert seed.join([]) == 3
    assert seed.request(2, 1) == [1]
    assert seed.request(3, 1) == [1, 2]
    assert seed.request(3, 2) == []  # nobody has chunk 2, and now nobody does
    assert seed.request(1, 2) == []
