"""Reproduce changed source bytes/descriptors, never refresh judgments."""
import copy
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def make():
    base = {s['source_id']: s for s in json.loads((HERE/'sources_ch21.json').read_text('utf-8'))}
    directory = HERE/'fixtures_ch22'
    directory.mkdir(exist_ok=True)
    descriptors = []
    for source, revision, minutes, role in (('A06', 2, 9, 'reader'), ('A06', 3, 12, 'reader'), ('A08', 2, 120, 'admin')):
        desc = copy.deepcopy(base[source])
        desc['source_version'] = str(revision)
        desc['path'] = source+'-v'+str(revision)+'.md'
        desc['metadata']['version'] = revision
        desc['metadata']['acl_roles'] = [role]
        desc['metadata']['updated_at'] = '2026-10-13T12:00:00Z'
        desc['allowed_scopes'] = ['A-'+role]
        text = (f'Orion rollback procedure: The coordinator waits {minutes} minutes after approval before rollback. '
                'The signed approval record must be attached to the incident. Stop if the health check fails.')
        (directory/desc['path']).write_bytes((text+'\n').encode('utf-8'))
        descriptors.append(desc)
    (directory/'updates.json').write_bytes((json.dumps(descriptors, ensure_ascii=False, indent=2)+'\n').encode('utf-8'))


if __name__ == '__main__':
    make()
