"""Implement A0 before opening the reference or separate solution.

Rows are metadata-only dictionaries with id, tenant, roles, language, published.
Return sorted IDs. Authorization is tenant equality AND nonempty role overlap.
Missing tenant/roles deny. Optional language None never matches a requested
language. Dates must be timezone-aware ISO strings, with [start,end) bounds.
The only predicate keys are language, start, end. Unknown/malformed predicates
raise ValueError before selecting anything; unsupported naive dates also raise.
An invalid row timestamp excludes that row when a date constraint is present.
Do not access a body/vector, evaluate query text, or import the reference.
"""


def select(rows, tenant, roles, predicate):
    raise NotImplementedError('Construct the authorization and predicate intersection')
