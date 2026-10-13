"""Independent A0: monotonic upsert/tombstone reducer, no reference imports.

head is None or {revision, digest, tombstone}. event has the same fields.
Validate positive integer revision (bool invalid), explicit bool tombstone and
nonempty string digest. Older event: unchanged/stale. Equal identical event:
unchanged/duplicate. Equal conflicting content: ValueError. Newer: copied head
with accepted status. Never mutate input; never drop a tombstone's revision.
Return (new_head, status). No content, model, index or event broker is needed.
"""


def apply(head, event):
    raise NotImplementedError('Construct revision comparison and tombstone retention')
