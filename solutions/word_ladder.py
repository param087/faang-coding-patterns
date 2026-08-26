"""Word Ladder — LeetCode 127."""

from __future__ import annotations

from collections import defaultdict, deque

META = {
    "pattern": "graph-traversal",
    "insight": "Words are nodes and one-letter changes are edges — but building those edges via wildcard patterns is the real problem.",
    "time": "O(N · L²)",
    "space": "O(N · L)",
    "sections": [
        (
            "What it asks",
            """
Transform `beginWord` into `endWord`, changing one letter at a time, with
every intermediate word in the dictionary. Return the number of words in the
shortest sequence, or 0.

Ask: is `endWord` guaranteed in the list (**no** — return 0 if absent); are all
words the same length (yes); is `beginWord` in the list (not necessarily); is
the answer the count of **words** or of transformations? (Words — so it is
edges + 1, an off-by-one that bites everyone once.)
""",
        ),
        (
            "The reframing",
            """
This is the problem that teaches **any state space is a graph**.

Words are nodes. Two words are adjacent if they differ in exactly one letter.
"Shortest transformation" is then "shortest path in an unweighted graph",
which is **BFS**.

Once said, the algorithm is standard. The difficulty moves entirely into
building the edges.
""",
        ),
        (
            "Building the edges is the actual problem",
            """
Comparing every pair of words is O(N² · L). At N = 5000 that is 25 million
comparisons of strings — too slow.

Instead build a map from **wildcard patterns** to the words matching them:
`hot` generates `*ot`, `h*t`, `ho*`. Two words are adjacent exactly when they
share a pattern.

That is O(N · L) to build and turns neighbour lookup into a dict access. This
preprocessing step is what the question is really testing.
""",
        ),
        (
            "The off-by-one",
            """
LeetCode wants the number of **words in the sequence**, including both ends.
So a single transformation (`hit → hot`) is length 2, not 1.

Start the BFS distance at 1, not 0.
""",
        ),
        (
            "Mark on enqueue",
            """
As always with BFS: add to `visited` when you **push**, not when you pop.
Otherwise a word can be queued many times before it is first processed, and
the frontier explodes.
""",
        ),
        (
            "Follow-ups",
            """
- **Bidirectional BFS.** Search from both ends and stop when the frontiers
  meet, roughly halving the explored space from `b^d` to `2·b^(d/2)`. It is
  the standard optimisation for this shape and worth naming even if you do not
  implement it.
- **Word Ladder II** — return every shortest path, which needs a parent map
  built during the BFS and a backtracking reconstruction afterwards. Much
  harder.
""",
        ),
    ],
}


def ladder_length(begin_word: str, end_word: str, word_list: list[str]) -> int:
    words = set(word_list)
    if end_word not in words:
        return 0  # unreachable by definition

    # Wildcard buckets: "hot" -> "*ot", "h*t", "ho*". O(N*L) instead of O(N^2*L).
    buckets: dict[str, list[str]] = defaultdict(list)
    length = len(begin_word)
    for word in words:
        for i in range(length):
            buckets[word[:i] + "*" + word[i + 1 :]].append(word)

    visited = {begin_word}
    queue: deque[tuple[str, int]] = deque([(begin_word, 1)])  # 1: words, not edges

    while queue:
        word, steps = queue.popleft()
        for i in range(length):
            for neighbour in buckets[word[:i] + "*" + word[i + 1 :]]:
                if neighbour == end_word:
                    return steps + 1
                if neighbour not in visited:
                    visited.add(neighbour)  # on enqueue, not on dequeue
                    queue.append((neighbour, steps + 1))

    return 0


CASES = [
    (("hit", "cog", ["hot", "dot", "dog", "lot", "log", "cog"]), 5),
    (("hit", "cog", ["hot", "dot", "dog", "lot", "log"]), 0),
    (("a", "c", ["a", "b", "c"]), 2),
    (("hot", "dog", ["hot", "dog"]), 0),
    (("hit", "hot", ["hot"]), 2),
]


def solve(begin_word: str, end_word: str, word_list: list[str]) -> int:
    return ladder_length(begin_word, end_word, word_list)
