"""Reproduce fictional source bytes/metadata; never regenerate judgments."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def make():
    sources = []
    specs = [('A'+str(day).zfill(2), 'A', day, 'Orion', 'en', 'reader', minutes)
             for day, minutes in zip(range(1, 9), (30, 30, 45, 60, 75, 90, 105, 120))]
    specs += [('A09', 'A', 6, 'Green', 'en', 'reader', 15),
              ('A10', 'A', 8, 'Orion', 'es', 'reader', 150)]
    specs += [('B'+str(n).zfill(2), 'B', day, 'Orion', 'en', 'reader', minutes)
              for n, day, minutes in ((1, 4, 20), (2, 6, 40), (3, 8, 80), (4, 9, 160))]
    specs += [('A-admin', 'A', 6, 'Orion', 'en', 'admin', 1),
              ('A-unknown', 'A', 6, 'Orion', None, None, 5),
              ('A-unlicensed', 'A', 6, 'Orion', 'en', 'reader', 10)]
    fixture = HERE/'fixtures_ch21'
    fixture.mkdir(parents=True, exist_ok=True)
    for source_id, tenant, day, entity, language, role, minutes in specs:
        text = (f'{entity} rollback procedure: The coordinator waits {minutes} minutes after approval before rollback. '
                'The signed approval record must be attached to the incident. Stop if the health check fails.')
        if language == 'es':
            text = ('Procedimiento Orion: El coordinador espera 150 minutos despu\u00e9s de la aprobaci\u00f3n antes de revertir. '
                    'Adjunte el registro firmado al incidente. Detenga el proceso si falla la comprobaci\u00f3n.')
        (fixture/(source_id+'.md')).write_bytes((text+'\n').encode('utf-8'))
        stamp = f'2026-10-{day:02d}T00:00:00Z'
        meta = {'schema_version': 'ch21-metadata-1', 'policy_version': 'ch21-role-intersection-1',
                'record_id': source_id, 'tenant': tenant, 'acl_roles': [role] if role else [],
                'owner': 'ops-'+tenant, 'published_at': stamp, 'updated_at': stamp, 'version': 1,
                'entity': entity, 'language': language, 'parent_id': tenant+'/manual',
                'extraction_confidence': .99}
        sources.append({'source_id': source_id, 'source_version': '1', 'path': source_id+'.md',
                        'allowed_scopes': [tenant+'-'+role] if role else [],
                        'license': 'book-authored-fixture' if source_id != 'A-unlicensed' else None,
                        'indexing_allowed': source_id != 'A-unlicensed',
                        'retention_policy': 'book-fixture-snapshot', 'metadata': meta})
    (HERE/'sources_ch21.json').write_bytes((json.dumps(sources, ensure_ascii=False, indent=2)+'\n').encode('utf-8'))


if __name__ == '__main__':
    make()
