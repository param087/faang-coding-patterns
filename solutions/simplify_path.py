"""Simplify Path — LeetCode 71."""

from __future__ import annotations

META = {
    "pattern": "string-manipulation",
    "insight": "Split on '/' and let a stack do the work: '..' pops, '.' and empty are noise, everything else is a directory name.",
    "time": "O(n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Turn an absolute Unix-style path into its canonical form: exactly one `/`
between components, no trailing `/` (except for the root itself), no `.`, and
every `..` resolved against its parent.

Ask two things. **Is the path always absolute?** On LeetCode yes, which is why
the answer can unconditionally start with `/`. **Are symlinks in play?** No —
this is pure lexical normalisation, which is precisely why `..` may be resolved
by popping. Real `realpath(3)` cannot do that, because `a/b/..` is not `a` when
`b` is a symlink. Saying this is a cheap signal that you have shipped
filesystem code.
""",
        ),
        (
            "The insight",
            """
Do not walk the string character by character tracking slash runs. `split("/")`
already does the tokenising, and it hands you empty strings exactly where the
duplicate and trailing slashes were — so `"//"` and `"/"` collapse for free.

After that there are only four token kinds, and the classification *is* the
algorithm:

| token | action |
| --- | --- |
| `""` | skip (duplicate or trailing slash) |
| `"."` | skip (current directory) |
| `".."` | pop, if there is anything to pop |
| anything else | push |

Join with `/` and prefix a `/`. The stack never holds a `.` or a `..`, so the
output is canonical by construction — no post-processing pass.
""",
        ),
        (
            "The tokens that catch people",
            """
- **`"..."` is a legal directory name**, and so is `"...."`. Only the exact
  two-character `".."` is special. Anyone matching with `startswith("..")` gets
  this wrong.
- **`..` at the root is a no-op, not an error.** `"/../"` is `"/"`. The `if
  stack` guard is the entire handling; there is no parent of `/` to complain
  about.
- **The root is the one path that keeps its slash.** With an empty stack,
  `"/" + "/".join([])` is `"/"` — the formulation gives you that free, which is
  why it is worth writing it exactly that way rather than joining and then
  patching the ends.
- **Nothing is trimmed.** `"/a /b"` has a directory literally named `"a "`.
  Do not call `.strip()` on the tokens.
""",
        ),
    ],
}


def simplify_path(path: str) -> str:
    stack: list[str] = []

    for part in path.split("/"):
        if part in {"", "."}:
            continue  # duplicate/trailing slash, or the current directory
        if part == "..":
            if stack:  # at the root, ".." is simply a no-op
                stack.pop()
        else:
            stack.append(part)  # note: "..." lands here, and should

    return "/" + "/".join(stack)


CASES = [
    (("/home/",), "/home"),
    (("/",), "/"),
    (("/../",), "/"),
    (("/home//foo/",), "/home/foo"),
    (("/a/./b/../../c/",), "/c"),
    (("/...",), "/..."),
    (("/a//b////c/d//././/..",), "/a/b/c"),
    (("/a/../../b/../c//.//",), "/c"),
]


def solve(path: str) -> str:
    return simplify_path(path)
