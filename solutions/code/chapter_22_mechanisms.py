"""Separate metadata-only reducer answer; attempt lab A0 first."""


def apply(head, event):
    for item in (event, head) if head is not None else (event,):
        if not isinstance(item, dict) or type(item.get('revision')) is not int or item['revision']<1 or type(item.get('tombstone')) is not bool or not isinstance(item.get('digest'),str) or not item['digest']:
            raise ValueError('Invalid revision state')
    if head is not None:
        if event['revision'] < head['revision']:
            return dict(head), 'stale'
        if event['revision'] == head['revision']:
            if event != head:
                raise ValueError('Conflicting same revision')
            return dict(head), 'duplicate'
    return dict(event), 'accepted'
