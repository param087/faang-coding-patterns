# Constraints First

Every category of coding problem a FAANG SDE-2 interview can ask — the pattern
that solves it, a tested Python template, and which companies actually ask it.

**→ [param087.github.io/faang-coding-patterns](https://param087.github.io/faang-coding-patterns/)**

## Why this exists

The usual failure isn't laziness, it's coverage. You grind a 150-problem list,
then get a monotonic-deque question, or a segment tree, or "design a rate
limiter class" — and none of it was on the list.

So the taxonomy here is **39 patterns**, deliberately wider than the popular
lists. Monotonic stack, union-find, topological sort, prefix sums, sweep line,
string algorithms, ordered-set/TreeMap, randomized sampling, concurrency and
segment trees each get their own page, because in a round you recognise and
reach for them independently. **Design** gets one too, and no popular list has
a bucket for it despite it being one of the highest-frequency SDE-2 categories.

The organising idea is in the name. An SDE-2 is expected to read the constraint
block first and know the shape of the answer before reading the problem:
`n ≤ 20` means find the bitmask, `n ≤ 10⁵` means stop hunting for a clever
quadratic. Colour on this site encodes complexity class and nothing else, so a
grid of patterns reads as a distribution of what things cost.

## What's in it

| | |
| --- | --- |
| Patterns | 39, in 8 groups, each with recognition cues, a tested template, pitfalls and anchor walkthroughs |
| Curated problems | 539 hand-assigned across the patterns (core + stretch) |
| Indexed problems | 3,719 auto-classified, filterable |
| Companies | 659, with per-problem frequency across 5 time windows |
| Solutions | full commented Python, one module per problem, all pytest-verified |

## Data sources

All public, no credentials, no LeetCode Premium. Snapshotted into `data/raw/`
and committed, so the site builds offline and a rebuild never silently changes
what it recommends.

- **[LeetCode GraphQL](https://leetcode.com/graphql)** — 4,033 problems: id,
  slug, difficulty, acceptance rate, premium flag, topic tags.
- **[neetcode-gh/leetcode](https://github.com/neetcode-gh/leetcode)**
  `.problemSiteData.json` — 450 curated problems with NeetCode's pattern,
  Blind 75 / NeetCode 150 membership, and solution-video IDs.
- **[snehasishroy/leetcode-companywise-interview-questions](https://github.com/snehasishroy/leetcode-companywise-interview-questions)**
  — company tags for 659 companies, snapshot dated **12 July 2026**.
- **[Simple Icons](https://simpleicons.org)** (CC0) — brand marks, vendored at
  build time with a version ladder, since recent releases dropped several
  major marks over trademark requests.

**Company frequencies are approximate.** They come from a community scrape of
a paid feature and go stale. Treat them as a signal about where to spend your
next hour, not a prediction of your interview.

**Problem statements are never reproduced here.** Every problem links out to
LeetCode. The logos are trademarks of their owners, used only to identify the
company.

## Layout

```
CATALOGUE.md              hand-curated pattern → problem assignments (the gating artifact)
code/                     pattern templates, Python, pytest-covered
solutions/                one module per catalogued problem
src/data/taxonomy.ts      the 39 patterns + tag-classification rules
src/lib/complexity.ts     the complexity ramp — drives colour and the constraint instrument
src/content/patterns/     one MDX page per pattern
src/content/solutions/    one MDX page per solved problem
scripts/                  fetch → join → classify → verify
```

Nothing on the site is untested code: MDX never contains a code block, it
references a symbol in `code/` or `solutions/` that the test suite runs, and
`<Snippet>` slices it in at build time.

## Working on it

```sh
npm install
uv venv .venv -p 3.12 && uv pip install --python .venv/bin/python pytest ruff

npm run data:all      # refresh the snapshot (optional — data/raw/ is committed)
npm run dev

bash scripts/gate.sh  # ruff, pytest, catalogue, biome, astro check, build, links
```

`scripts/gate.sh --quick` skips the sampled outbound link check, which is the
only step that needs network. CI runs the quick gate, then deploys to Pages on
every push to `main`.

## Licence

MIT for the code and prose. Problem metadata belongs to LeetCode; brand marks
belong to their owners.
