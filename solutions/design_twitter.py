"""Design Twitter — LeetCode 355."""

from __future__ import annotations

import heapq
from collections import defaultdict

META = {
    "pattern": "heaps",
    "symbol": "Twitter",
    "insight": "Store tweets per author with one global clock, then a feed is a k-way merge that only ever touches the last 10 tweets of each followee.",
    "time": "O(1) post/follow/unfollow, O(f log f + 10 log f) per feed",
    "space": "O(tweets + follow edges)",
    "sections": [
        (
            "What it asks",
            """
Four operations: `postTweet(user, tweet)`, `getNewsFeed(user)` — the **10 most
recent** tweets from the user and everyone they follow, newest first —
`follow(a, b)` and `unfollow(a, b)`.

The clarifications that shape the design:

- **How many followees can one user have, and how often is the feed read?**
  Real systems answer this with fan-out on write vs fan-out on read; LeetCode
  caps operations at 3·10⁴, so read-time merge is right here. Naming the
  tradeoff is what the "design" in the title is asking for.
- **Is a user's own tweet in their feed?** Yes — and they need not follow
  themselves for it to appear.
- **Exactly 10**, newest first, and fewer if that is all there is.
""",
        ),
        (
            "The insight",
            """
The wrong first design is one global list of tweets scanned backwards, filtered
by "is this author followed". It is O(total tweets) per feed read and degrades
as the service grows — a user following nobody still walks every tweet ever
posted.

Instead store tweets **per author**, newest at the end, and stamp each with a
counter from a single global clock. Then each followee's tweet list is already
sorted by recency, and the feed is the classic **k-way merge**: seed a max-heap
with the newest tweet of each of the f followees, pop, push that author's
previous tweet, stop after 10.

The bound is what makes it cheap. You never look at more than 10 tweets per
author and never pop more than 10 times, so a user with 10⁶ tweets costs the
same as one with 11. Cost is O(f) to seed plus O(10 log f) to drain — dependent
on how many people you follow, not on how much they have written.

The global counter, not a timestamp, is what makes ordering total: two tweets
posted in the same millisecond still have a strict order, and there are no
clock-skew ties to break.
""",
        ),
        (
            "The details that decide it",
            """
- **Merge, do not concatenate-and-sort.** Gathering the last 10 of every
  followee and sorting is O(10f log(10f)) and reads fine — but it loses the
  early exit, and the heap version is the one that generalises to "merge k
  sorted streams you cannot materialise".
- **Self-follow must not double-post.** `following[user] | {user}` is a set
  union, so a user who explicitly follows themselves still contributes one copy
  of each tweet. A list would give two — a bug that only shows up in the
  test that calls `follow(1, 1)`.
- **Unfollow yourself must be a no-op.** `discard` on a set that never held the
  self-edge is silent; but if you implemented self-inclusion by adding a real
  self-edge on construction, `unfollow(1, 1)` would erase the user's own tweets
  from their feed. That is the trap in this problem.
- **`unfollow` of someone never followed** must not raise — `set.discard`, not
  `set.remove`.
- **The heap entry needs the author and the index**, not just the tweet, or you
  cannot walk backwards to that author's previous tweet.
- **Follow-up — celebrity fan-out.** At 10⁸ followers, read-time merge is
  right for celebrities and write-time fan-out (push into each follower's
  materialised feed) is right for ordinary users; production systems run both
  and merge at read time. Say that; it is what separates this from a coding
  question.
""",
        ),
    ],
}


class Twitter:
    """Tweets stored per author, feed built as a bounded k-way merge."""

    FEED_SIZE = 10

    def __init__(self) -> None:
        self._clock = 0  # a counter, not a timestamp: no ties, no skew
        self._tweets: dict[int, list[tuple[int, int]]] = defaultdict(list)  # user -> [(t, id)]
        self._following: dict[int, set[int]] = defaultdict(set)

    def post_tweet(self, user_id: int, tweet_id: int) -> None:
        self._clock += 1
        self._tweets[user_id].append((self._clock, tweet_id))

    def get_news_feed(self, user_id: int) -> list[int]:
        # Union, not append: an explicit self-follow must not duplicate tweets.
        sources = self._following[user_id] | {user_id}

        # (-time, tweet, author, index) — negated because heapq is min-only.
        heap: list[tuple[int, int, int, int]] = []
        for author in sources:
            tweets = self._tweets.get(author)
            if not tweets:
                continue
            index = len(tweets) - 1  # newest
            time, tweet = tweets[index]
            heap.append((-time, tweet, author, index))
        heapq.heapify(heap)

        feed: list[int] = []
        while heap and len(feed) < self.FEED_SIZE:
            _, tweet, author, index = heapq.heappop(heap)
            feed.append(tweet)
            if index:  # walk backwards in that author's list only
                time, previous = self._tweets[author][index - 1]
                heapq.heappush(heap, (-time, previous, author, index - 1))
        return feed

    def follow(self, follower_id: int, followee_id: int) -> None:
        self._following[follower_id].add(followee_id)

    def unfollow(self, follower_id: int, followee_id: int) -> None:
        self._following[follower_id].discard(followee_id)  # discard, not remove


CASES: list[tuple[tuple, object]] = []


def check() -> None:
    twitter = Twitter()
    twitter.post_tweet(1, 5)
    assert twitter.get_news_feed(1) == [5]  # own tweets without following self
    twitter.follow(1, 2)
    twitter.post_tweet(2, 6)
    assert twitter.get_news_feed(1) == [6, 5]
    twitter.unfollow(1, 2)
    assert twitter.get_news_feed(1) == [5]

    # Explicit self-follow must not duplicate anything.
    twitter.follow(1, 1)
    assert twitter.get_news_feed(1) == [5]
    twitter.unfollow(1, 1)
    assert twitter.get_news_feed(1) == [5]  # own tweets survive unfollowing self

    # Unfollowing someone never followed is a no-op, not a KeyError.
    twitter.unfollow(1, 99)

    # Interleaved authors: the feed is globally ordered, not grouped by author.
    interleaved = Twitter()
    interleaved.follow(3, 1)
    interleaved.follow(3, 2)
    interleaved.post_tweet(1, 100)
    interleaved.post_tweet(2, 200)
    interleaved.post_tweet(1, 101)
    interleaved.post_tweet(2, 201)
    assert interleaved.get_news_feed(3) == [201, 101, 200, 100]

    # A silent user and an unknown user both yield an empty feed.
    assert interleaved.get_news_feed(3241) == []
    quiet = Twitter()
    quiet.follow(1, 2)
    assert quiet.get_news_feed(1) == []

    # Exactly 10, newest first, out of far more than 10 — and the bound holds
    # even though one author posted 50 times.
    prolific = Twitter()
    prolific.follow(1, 2)
    for i in range(50):
        prolific.post_tweet(2, i)
    prolific.post_tweet(1, 999)
    assert prolific.get_news_feed(1) == [999, 49, 48, 47, 46, 45, 44, 43, 42, 41]

    # Following a user retroactively exposes their older tweets.
    retro = Twitter()
    retro.post_tweet(2, 7)
    assert retro.get_news_feed(1) == []
    retro.follow(1, 2)
    assert retro.get_news_feed(1) == [7]

    # A tweet id may repeat; ordering is by the clock, not by id.
    repeated = Twitter()
    repeated.post_tweet(1, 4)
    repeated.post_tweet(1, 4)
    assert repeated.get_news_feed(1) == [4, 4]
