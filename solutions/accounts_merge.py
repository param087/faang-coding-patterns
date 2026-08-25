"""Accounts Merge — LeetCode 721."""

from __future__ import annotations

META = {
    "pattern": "union-find",
    "insight": "Union on emails, never on names — two different people can share a name, but a shared email means the same person.",
    "time": "O(N · α + N log N) for N emails",
    "space": "O(N)",
    "sections": [
        (
            "What it asks",
            """
Each account is a name followed by emails. Two accounts belong to the same
person if they share **any** email. Merge them, and return each person's name
with their emails sorted.

Ask: can the same name belong to different people (**yes** — that is the
trap); do two accounts merge on any shared email (yes); must the output emails
be sorted (yes).
""",
        ),
        (
            "The trap",
            """
Grouping by name is wrong. Two people called "John" are two people, and
merging them silently produces a wrong answer that looks plausible.

**Emails are the identity.** Names are labels attached to them.
""",
        ),
        (
            "The insight",
            """
Emails are the nodes. Within one account, union every email with the first
one. Accounts that share any email end up in the same set **transitively**,
without you ever comparing accounts pairwise.

That transitivity is the reason to reach for union-find rather than a nested
loop: A shares with B, B shares with C, so A and C merge even though they have
nothing directly in common.
""",
        ),
        (
            "The mapping step",
            """
Emails are strings and the DSU is indexed by integers, so half the code is
bookkeeping: `email → index` for the DSU, and `email → name` for the output.

Building those cleanly up front is what keeps the merge loop short.
""",
        ),
        (
            "Why not DFS",
            """
You could build a graph of email adjacencies and flood-fill it — same
complexity, equally correct.

DSU is shorter and expresses "these are the same person" more directly. Being
able to say which you would pick, **and why**, is the answer they want; the
question is not really about the data structure.
""",
        ),
        (
            "Follow-ups",
            """
- **Redundant Connection** — the first union that returns `False` is the edge
  closing a cycle.
- **Number of Provinces** — count the components.
- **Sentence Similarity II** — the same transitive-equivalence shape on words.
""",
        ),
    ],
}


class UnionFind:
    def __init__(self, n: int) -> None:
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x: int) -> int:
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:  # path compression
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a: int, b: int) -> bool:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True


def accounts_merge(accounts: list[list[str]]) -> list[list[str]]:
    index: dict[str, int] = {}
    owner: dict[str, str] = {}

    for account in accounts:
        name = account[0]
        for email in account[1:]:
            if email not in index:
                index[email] = len(index)
            owner[email] = name

    dsu = UnionFind(len(index))
    for account in accounts:
        emails = account[1:]
        for email in emails[1:]:
            # Union every email in an account with the first one.
            dsu.union(index[emails[0]], index[email])

    groups: dict[int, list[str]] = {}
    for email, i in index.items():
        groups.setdefault(dsu.find(i), []).append(email)

    return [[owner[emails[0]], *sorted(emails)] for emails in groups.values()]


CASES = [
    (
        (
            [
                ["John", "johnsmith@mail.com", "john_newyork@mail.com"],
                ["John", "johnsmith@mail.com", "john00@mail.com"],
                ["Mary", "mary@mail.com"],
                ["John", "johnnybravo@mail.com"],
            ],
        ),
        [
            ["John", "john00@mail.com", "john_newyork@mail.com", "johnsmith@mail.com"],
            ["Mary", "mary@mail.com"],
            ["John", "johnnybravo@mail.com"],
        ],
    ),
    (([["Alex", "a@m.co"]],), [["Alex", "a@m.co"]]),
    (([],), []),
]


def solve(accounts: list[list[str]]) -> list[list[str]]:
    return accounts_merge(accounts)


def check() -> None:
    for args, expected in CASES:
        actual = accounts_merge(*args)
        # Group order is not specified, so compare as sets of tuples.
        assert sorted(map(tuple, actual)) == sorted(map(tuple, expected))

    # Two different people sharing a name must NOT merge.
    result = accounts_merge([["John", "a@m.co"], ["John", "b@m.co"]])
    assert len(result) == 2
