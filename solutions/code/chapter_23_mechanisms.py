"""Separate bounded answer. Imports neither learner nor running project."""


def route(kind, available, ambiguous=False, language='en'):
    mapping = {'identifier': 'lexical', 'paraphrase': 'dense', 'date': 'dense',
               'relationship': 'graph', 'count': 'sql'}
    if kind not in mapping or not isinstance(available, frozenset) or available-{'lexical','dense','graph','sql','web'} or type(ambiguous) is not bool:
        raise ValueError('Invalid policy input')
    primary = mapping[kind]
    if ambiguous:
        selected, outcome, fallback, reason = None, 'clarify', False, 'ambiguous_intent'
    elif language != 'en':
        selected, outcome, fallback, reason = None, 'unsupported', False, 'unsupported_language'
    elif primary in available:
        selected, outcome, fallback, reason = primary, 'ready', False, None
    else:
        alternate = 'lexical' if primary in ('dense','graph') else 'dense' if primary=='lexical' else None
        selected = alternate if alternate in available else None
        outcome = ('partial' if primary=='graph' else 'ready') if selected else 'unsupported'
        fallback = selected is not None
        reason = ('evidence_only' if primary=='graph' else 'capability_fallback') if selected else 'route_unavailable'
    return dict(primary=primary, selected=selected, outcome=outcome, fallback=fallback, reason=reason)
