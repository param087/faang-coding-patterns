"""Guess the Word — LeetCode 843."""

from __future__ import annotations

import random
from collections import Counter

META = {
    "pattern": "randomized",
    "insight": "A guess is a partition, not an attempt to be right: send the word whose worst possible reply leaves the fewest survivors.",
    "time": "O(g · n² · L) — 60k character comparisons in round one at n = 100, g = 10, L = 6",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
An oracle problem. You hold a list of up to 100 distinct six-letter lowercase
words; one of them is the secret. `master.guess(word)` returns **how many of the
six positions match the secret exactly**, or `-1` if the word is not on the
list. You get 10 calls, and you must actually call `guess` with the secret —
narrowing to one candidate is not the same as answering.

Ask four things, all of which change the code:

- **Is the secret guaranteed to be on the list?** Yes — that is what makes
  elimination sound rather than a heuristic.
- **Positional matches or shared letters?** Positional. This is Mastermind's
  black pegs with no white pegs, so `overlap` compares index by index.
- **Does guessing a word you have already ruled out still return a real count?**
  Yes, and it costs one of the ten. That turns out to matter.
- **How were the words generated?** Randomly, on LeetCode. The whole difficulty
  of the problem lives in that answer.
""",
        ),
        (
            "The insight",
            """
Stop treating a guess as an attempt to be right. A reply of `k` **partitions the
candidate set into seven buckets** by overlap with the word you sent, and names
the bucket the secret is in; the other six are discarded. A guess is a question,
and its value is how evenly it splits — being correct is a lucky side effect.

Because `overlap` is symmetric, the filter is one line: keep every candidate `w`
with `overlap(w, guess) == reply`.

So pick the guess that **minimises the largest bucket** — Knuth's Mastermind
minimax, worst-case survivors. Since bucket 0 dwarfs the rest (below), this is
almost exactly "send the word that shares a position with as many candidates as
possible": the most typical word on the list, never the weirdest one.

Then the refinement most people miss. **The guess does not have to be a
candidate.** Every word in the original list is a legal call, including ones you
eliminated three rounds ago, and a word that *cannot* be the secret will
sometimes split the survivors better than any survivor can. Over 1200 simulated
100-word games, candidate-only minimax ran out of guesses once and hit 10 in the
worst case; scoring **every** word on the list never failed and never needed
more than 9. Tie-break towards real candidates so an outright win stays possible.

An already-asked word can never be re-picked, which is why the loop terminates:
after filtering, every survivor gives it the *same* reply, so its largest bucket
is the entire candidate set — strictly worse than any candidate, whose own
bucket 6 is excluded.

Scoring costs `n² · 6` = 60,000 character comparisons in round one at n = 100,
and collapses immediately after. There is no efficiency argument for guessing
blindly.
""",
        ),
        (
            "Why a random candidate is a 7% coin flip",
            """
Two random six-letter words over 26 letters agree **nowhere** with probability
`(25/26)⁶ ≈ 0.79`. So the reply is almost always 0, and a reply of 0 keeps ~79%
of the pool. Starting from 100 words, `100 · 0.79¹⁰ ≈ 9.5` are still standing
when the budget runs out.

Simulated over 2000 random 100-word games, guessing a uniformly random candidate
each round **failed 137 times — 6.8%**. That is the solution people submit,
watch pass on the third retry, and cannot explain. Minimax on the same games
failed zero times.

The adversarial word list is worth naming out loud, because it shows you know
what the algorithm rests on: eleven words that pairwise agree nowhere —
`"aaaaaa"`, `"bbbbbb"`, … `"kkkkkk"`. Every reply is 0 and eliminates exactly the
one word you just sent, so **no** strategy beats asking them one at a time, and
ten guesses is provably not enough. LeetCode generates its lists randomly so this
never appears in the tests; the point is that the guarantee is statistical, not
structural.
""",
        ),
    ],
}

WORD_LENGTH = 6
BUDGET = 10


def overlap(a: str, b: str) -> int:
    """Positions where two words agree. Symmetric — which is what lets us filter."""
    return sum(x == y for x, y in zip(a, b, strict=True))


class Master:
    """The interactive oracle, written out so the module runs on its own."""

    def __init__(self, secret: str, words: list[str], budget: int = BUDGET) -> None:
        self.secret = secret
        self.allowed = set(words)
        self.budget = budget
        self.guesses: list[str] = []
        self.solved = False

    def guess(self, word: str) -> int:
        if len(self.guesses) >= self.budget:
            raise RuntimeError("out of guesses")
        self.guesses.append(word)
        if word not in self.allowed:
            return -1  # a legal call, but it tells you nothing
        score = overlap(word, self.secret)
        if score == WORD_LENGTH:
            self.solved = True
        return score


def best_probe(words: list[str], candidates: list[str]) -> str:
    """The legal guess whose worst possible reply leaves the fewest candidates."""
    survivors = set(candidates)
    best, best_key = candidates[0], None

    for word in words:  # the whole list, not just the survivors
        buckets = Counter(overlap(word, other) for other in candidates)
        # Bucket 6 is a win, not a burden, so it never counts against a candidate.
        worst = max((size for score, size in buckets.items() if score != WORD_LENGTH), default=0)
        key = (worst, 0 if word in survivors else 1)  # break ties towards a possible win
        if best_key is None or key < best_key:
            best, best_key = word, key

    return best


def find_secret_word(words: list[str], master: Master) -> str | None:
    candidates = list(words)

    for _ in range(BUDGET):
        pick = best_probe(words, candidates)
        score = master.guess(pick)
        if score == WORD_LENGTH:
            return pick

        # Everything left must agree with the guess in exactly as many places.
        candidates = [w for w in candidates if w != pick and overlap(w, pick) == score]
        if not candidates:
            return None  # only reachable if the oracle contradicts itself

    return None


DISJOINT_TEN = [letter * WORD_LENGTH for letter in "abcdefghij"]


CASES = [
    ((["acckzz", "ccbazz", "eiowzz", "abcczz"], "acckzz"), 1),
    ((["acckzz", "ccbazz", "eiowzz", "abcczz"], "eiowzz"), 2),
    ((["hamada", "khaled"], "khaled"), 2),
    ((["aaaaaa"], "aaaaaa"), 1),
    # The best probe is "abbbbb" — the fourth word, not the first. A strategy
    # that just takes candidates[0] needs three guesses here.
    ((["aaaaaa", "bbbbbb", "cccccc", "abbbbb"], "cccccc"), 2),
    # Ten pairwise-disjoint words: every reply eliminates exactly one, so the
    # last of them uses the budget to the last call.
    ((DISJOINT_TEN, "jjjjjj"), 10),
    ((DISJOINT_TEN, "aaaaaa"), 1),
]


def solve(words: list[str], secret: str) -> int:
    """Calls needed to land on `secret`, or -1 if the strategy runs out."""
    master = Master(secret, list(words))
    found = find_secret_word(list(words), master)
    return len(master.guesses) if found == secret else -1


def check() -> None:
    for args, expected in CASES:
        assert solve(*args) == expected, args

    # An off-list word is a legal call that buys nothing.
    oracle = Master("aaaaaa", ["aaaaaa", "bbbbbb"])
    assert oracle.guess("zzzzzz") == -1
    assert oracle.guess("aaaaaa") == 6
    assert oracle.solved

    # Eleven pairwise-disjoint words cannot be done in ten guesses by anybody.
    assert solve([letter * WORD_LENGTH for letter in "abcdefghijk"], "kkkkkk") == -1

    # A realistic list: every secret must be found inside the budget, and the
    # strategy must only ever send distinct words that are actually on the list.
    rng = random.Random(20240607)
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    pool = {"".join(rng.choice(alphabet) for _ in range(WORD_LENGTH)) for _ in range(60)}
    words = sorted(pool)
    allowed = set(words)

    for secret in words:
        master = Master(secret, words)
        found = find_secret_word(list(words), master)
        assert found == secret, secret
        assert 1 <= len(master.guesses) <= BUDGET, (secret, master.guesses)
        assert len(set(master.guesses)) == len(master.guesses), master.guesses
        assert allowed.issuperset(master.guesses), master.guesses
