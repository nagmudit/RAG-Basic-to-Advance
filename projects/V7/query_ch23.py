"""Bounded interpretation and routing, not generated rewriting or fusion."""
import copy
import re
import unicodedata
from datetime import date, timedelta

ROUTER_VERSION = 'ch23-closed-grammar-1'
ROUTES = frozenset({'lexical', 'dense', 'sql', 'graph', 'web'})
ID = re.compile(r'(?<![\w-])[AB][0-9]{2}(?![\w-])')
DATE = r'[0-9]{4}-[0-9]{2}-[0-9]{2}'


def normalize(text):
    if not isinstance(text, str) or not text or len(text) > 2048:
        raise ValueError('Invalid query length/type')
    if any(unicodedata.category(c) in ('Cc', 'Cf') and c not in '\t\n\r' for c in text):
        raise ValueError('Unsupported control character')
    value = ' '.join(unicodedata.normalize('NFC', text).split())
    if not value:
        raise ValueError('Empty query')
    return value


def route_features(kind, available, ambiguous=False, language='en'):
    """Small policy: fallback preserves operation semantics, not just vocabulary."""
    if kind not in ('identifier', 'paraphrase', 'date', 'relationship', 'count', 'fresh'):
        raise ValueError('Unknown query kind')
    if not isinstance(available, frozenset) or available - ROUTES or type(ambiguous) is not bool:
        raise ValueError('Invalid capability/policy input')
    primary = {'identifier': 'lexical', 'paraphrase': 'dense', 'date': 'dense',
               'relationship': 'graph', 'count': 'sql', 'fresh': 'web'}[kind]
    if ambiguous:
        return dict(primary=primary, selected=None, outcome='clarify', fallback=False, reason='ambiguous_intent')
    if language != 'en':
        return dict(primary=primary, selected=None, outcome='unsupported', fallback=False, reason='unsupported_language')
    if primary in available:
        return dict(primary=primary, selected=primary, outcome='ready', fallback=False, reason=None)
    alternate = 'lexical' if primary in ('dense', 'graph') else 'dense' if primary == 'lexical' else None
    if alternate in available:
        return dict(primary=primary, selected=alternate,
                    outcome='partial' if primary == 'graph' else 'ready', fallback=True,
                    reason='evidence_only' if primary == 'graph' else 'capability_fallback')
    return dict(primary=primary, selected=None, outcome='unsupported', fallback=False, reason='route_unavailable')


def interpret(text, *, available=frozenset({'lexical', 'dense'}), language='en',
              context=None, principal_key=None, session_id=None, clock_ms=5300):
    if type(clock_ms) is not int or clock_ms<0:raise ValueError('Invalid source reference clock')
    surface = normalize(text)
    folded = surface.casefold()  # Cue matching only; IDs use the preserved surface.
    predicate, provenance = {}, {}
    as_of, error = None, None
    ids = list(dict.fromkeys(ID.findall(surface)))
    if len(ids) > 1:
        error = 'multiple_identifiers'
    elif ids:
        predicate['record_id'] = ids[0]; provenance['record_id'] = 'current_query'
    # A visually similar/full-width or lowercase ID is NOT silently repaired.
    loose_ids = re.findall(r'(?<![\w-])[ab][0-9]{2}(?![\w-])', surface)
    if loose_ids or any(unicodedata.east_asian_width(c) == 'F' for c in surface):
        error = 'identifier_confirmation_required'
    entities = [name for name in ('Orion', 'Green') if re.search(r'\b'+name.casefold()+r'\b', folded)]
    if len(entities) > 1:
        error = 'multiple_entities'
    elif entities:
        predicate['entity'] = entities[0]; provenance['entity'] = 'current_query'
    if re.search(r'\b(it|its|that record)\b', folded) and not ids:
        ctx = copy.deepcopy(context or {})
        if ctx.get('principal_key') != principal_key or ctx.get('session_id') != session_id:
            error = 'context_scope_mismatch'
        elif type(ctx.get('expires_at_ms')) is not int or ctx['expires_at_ms'] <= clock_ms:
            error = 'context_expired'
        elif not isinstance(ctx.get('record_ids'), list) or len(ctx['record_ids']) != 1 or not ID.fullmatch(ctx['record_ids'][0]):
            error = 'ambiguous_reference'
        elif entities and ctx.get('entity') != entities[0]:
            error = 'context_entity_conflict'
        else:
            predicate['record_id'] = ctx['record_ids'][0]
            provenance['record_id'] = 'prior_turn:'+str(ctx.get('origin_query_id'))
    on = re.search(r'\bpublished on ('+DATE+r')\b', folded)
    span = re.search(r'\bpublished from ('+DATE+r') to ('+DATE+r')\b', folded)
    temporal = re.search(r'\bas of source ([0-9]+)\b', folded)
    try:
        if on and span or temporal and (on or span):
            error = 'multiple_time_axes'
        elif on:
            day = date.fromisoformat(on[1]); end = day+timedelta(days=1)
            predicate.update(published_gte=day.isoformat()+'T00:00:00Z', published_lt=end.isoformat()+'T00:00:00Z')
            provenance['publication_interval'] = 'current_query:UTC_day'
        elif span:
            start, end = date.fromisoformat(span[1]), date.fromisoformat(span[2])
            if start >= end:
                raise ValueError('Invalid interval')
            predicate.update(published_gte=start.isoformat()+'T00:00:00Z', published_lt=end.isoformat()+'T00:00:00Z')
            provenance['publication_interval'] = 'current_query:half_open_UTC'
        elif temporal:
            as_of = int(temporal[1]); provenance['as_of'] = 'current_query:fixture_source_clock'
            if as_of>clock_ms:error='future_source_time'
        elif re.search(r'\b(published|as of|yesterday|last week)\b', folded):
            error = 'unresolved_time'
    except (ValueError, OverflowError):
        error = 'invalid_date'
    # Intentionally coarse count rule: "How many minutes ...?" is a measured
    # false positive retained in the frozen workload, not patched to fit it.
    if re.search(r'\b(how many|count of|total number|sum of|average)\b', folded):
        kind = 'count'
    elif re.search(r'\b(depends on|connected to|relationship|reports to)\b', folded):
        kind = 'relationship'
    elif re.search(r'\b(latest public|announcement today|live web)\b', folded):
        kind = 'fresh'
    elif 'record_id' in predicate:
        kind = 'identifier'
    elif on or span or temporal:
        kind = 'date'
    else:
        kind = 'paraphrase'
    decision = route_features(kind, available, bool(error), language)
    if error:
        decision['reason'] = error
    return {'original': text, 'surface': surface, 'kind': kind, 'predicate': predicate,
            'as_of_ms': as_of, 'slot_provenance': provenance, 'router_version': ROUTER_VERSION,
            'route_confidence': None, **decision}
