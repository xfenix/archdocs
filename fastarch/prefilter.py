"""Cheap rejection of sources before any regex runs.

`str.__contains__` scans with memchr while `re` walks its own bytecode on a virtual
machine, so on a miss a substring costs tens of times less than a pattern. Every parser
misses on the overwhelming majority of a project's files — celery is mentioned in a module
or two and nowhere else — so the miss is what to optimise: first the cheap "is the word in
this file at all", and only then the expensive "is it in the right context".

Literals have to be a necessary condition for the pattern to match, covering every one of
its alternatives: a superfluous literal costs one wasted regex run, a missing one silently
costs a feature on the diagram. The source arrives already lowercased because the patterns
are compiled with `IGNORECASE`, and one `lower()` per file is enough for all of them.
"""


def contains_any_literal(lowered_source: str, every_literal: tuple[str, ...], /) -> bool:
    return any(one_literal in lowered_source for one_literal in every_literal)
