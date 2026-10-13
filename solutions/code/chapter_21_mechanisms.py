"""Separate bounded answer. Attempt lab A0 first; no engine/learner imports."""
from datetime import datetime, timezone


def utc(value):
    if not isinstance(value, str):
        raise ValueError('Timestamp type')
    try:
        result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        raise ValueError('Timestamp format') from None
    if result.tzinfo is None:
        raise ValueError('Timezone required')
    return result.astimezone(timezone.utc)


def select(rows, tenant, roles, predicate):
    if not isinstance(predicate, dict) or set(predicate)-{'language', 'start', 'end'}:
        raise ValueError('Predicate field')
    if 'language' in predicate and (not isinstance(predicate['language'], str) or not predicate['language']):
        raise ValueError('Requested language')
    start = utc(predicate['start']) if 'start' in predicate else None
    end = utc(predicate['end']) if 'end' in predicate else None
    if start is not None and end is not None and start >= end:
        raise ValueError('Empty/reversed interval')
    selected = []
    for row in rows:
        row_roles = row.get('roles')
        if row.get('tenant') != tenant or not isinstance(row_roles, list) or not row_roles or not set(row_roles).intersection(roles):
            continue
        if 'language' in predicate and row.get('language') != predicate['language']:
            continue
        if start is not None or end is not None:
            try:
                stamp = utc(row.get('published'))
            except ValueError:
                continue
            if (start is not None and stamp < start) or (end is not None and stamp >= end):
                continue
        selected.append(row['id'])
    return sorted(selected)
