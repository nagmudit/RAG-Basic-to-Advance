"""Write your bounded policy before viewing the separate answer/reference.

route(kind, available, ambiguous=False, language='en') -> dictionary with
primary, selected, outcome, fallback, reason. Follow LAB.md's exact contract.
Kinds: identifier, paraphrase, date, relationship, count. available is frozenset.
Return no input mutations. Invalid kind/capabilities/non-bool ambiguity -> ValueError.
"""


def route(kind, available, ambiguous=False, language='en'):
    raise NotImplementedError('Construct the query routing policy yourself')
