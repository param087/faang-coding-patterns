"""Find All Possible Recipes from Given Supplies — LeetCode 2115."""

from __future__ import annotations

from collections import defaultdict, deque

META = {
    "pattern": "topological-sort",
    "insight": "Count only the ingredients you do not already have; a recipe becomes makeable the moment that counter hits zero.",
    "time": "O(total ingredient mentions)",
    "space": "O(total ingredient mentions)",
    "sections": [
        (
            "What it asks",
            """
`recipes[i]` is made from `ingredients[i]`, an ingredient may itself be another
recipe, and `supplies` is what you start with in unlimited quantity. Return
every recipe you can eventually create, in any order.

Ask whether recipes can depend on each other cyclically. They can — and the
"unlimited quantity" phrasing is what tells you this is pure reachability, not a
resource-allocation problem. If quantities were finite the whole approach
changes.

Also confirm names are unique across `recipes` and `supplies` (they are), which
is why a single string keyspace works with no disambiguation.
""",
        ),
        (
            "The insight",
            """
This is Kahn's algorithm where the indegree is *"how many ingredients I still
do not have"*, not *"how many edges point at me"*.

That distinction is the whole trick. Building a literal graph over every
ingredient and topologically sorting it forces you to invent nodes for base
supplies and then remember they start satisfied. Instead:

- for each recipe, count only the ingredients **not in `supplies`** — call it
  `missing[recipe]`;
- register the recipe as a dependent of each such ingredient;
- seed the queue with recipes whose `missing` is already 0;
- popping a recipe means it is now available, so decrement `missing` for
  everything waiting on it.

An ingredient that is neither a supply nor a producible recipe simply never gets
popped, so its dependents' counters never reach 0 — a missing base ingredient
and a cyclic dependency fail through the *same* mechanism, with no cycle check
written anywhere. That is the elegant part, and it is worth pointing out.

O(sum of ingredient list lengths). At the limits (100 recipes × 100 ingredients)
that is 10⁴ operations; the naive "loop over all recipes repeatedly until no
progress" is O(n²·m) = 10⁶ and also passes, but volunteering the linear version
is the difference between a hire and a lean-hire.
""",
        ),
        (
            "Edge cases",
            """
- **Cycle**: `recipes = ["a","b"]`, `ingredients = [["b"],["a"]]`, no supplies →
  `[]`. Neither counter ever reaches 0.
- **Self-reference**: `["a"]` needing `["a"]` → `[]`, same mechanism, no special
  case.
- **A chain**: `bread → sandwich → burger`. The output order is the order
  discovered, which is a valid topological order — the problem accepts any
  order, so `solve` sorts here purely to make the tests deterministic. Say this
  out loud rather than sorting silently, since sorting is O(n log n) you did not
  need.
- **Repeated ingredient inside one recipe.** It increments `missing` twice and is
  registered twice in `dependents`, so both decrements fire. Correct without a
  `set`, but if you *do* dedupe the ingredient list you must dedupe before
  counting, not after.
- **An ingredient that is also a supply** never enters `dependents` at all —
  that is exactly what "already have it" means.
- **Empty recipe list** → `[]`, and the seeding generator handles it without a
  guard.
""",
        ),
    ],
}


def find_all_recipes(
    recipes: list[str],
    ingredients: list[list[str]],
    supplies: list[str],
) -> list[str]:
    available = set(supplies)
    dependents: dict[str, list[str]] = defaultdict(list)
    missing: dict[str, int] = {}

    for recipe, needed in zip(recipes, ingredients, strict=True):
        outstanding = 0
        for item in needed:
            if item not in available:  # base supplies are satisfied from the start
                dependents[item].append(recipe)
                outstanding += 1
        missing[recipe] = outstanding

    queue = deque(recipe for recipe in recipes if missing[recipe] == 0)
    made: list[str] = []

    while queue:
        recipe = queue.popleft()
        made.append(recipe)
        for dependent in dependents[recipe]:
            missing[dependent] -= 1
            if missing[dependent] == 0:
                queue.append(dependent)

    return made  # cycles and absent ingredients both simply never get popped


CASES = [
    ((["bread"], [["yeast", "flour"]], ["yeast", "flour", "corn"]), ["bread"]),
    (
        (
            ["bread", "sandwich"],
            [["yeast", "flour"], ["bread", "meat"]],
            ["yeast", "flour", "meat"],
        ),
        ["bread", "sandwich"],
    ),
    (
        (
            ["bread", "sandwich", "burger"],
            [["yeast", "flour"], ["bread", "meat"], ["sandwich", "meat", "bread"]],
            ["yeast", "flour", "meat"],
        ),
        ["bread", "burger", "sandwich"],
    ),
    ((["bread"], [["yeast", "flour"]], ["yeast"]), []),
    ((["a", "b"], [["b"], ["a"]], ["x"]), []),
    ((["a"], [["a"]], ["x"]), []),
    ((["a", "b"], [["b"], ["x"]], ["x"]), ["a", "b"]),
    (([], [], ["x"]), []),
]


def solve(
    recipes: list[str],
    ingredients: list[list[str]],
    supplies: list[str],
) -> list[str]:
    # Any order is accepted; sorted for a deterministic comparison.
    return sorted(find_all_recipes(recipes, ingredients, supplies))
