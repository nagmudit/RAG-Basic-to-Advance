"""Fresh fixture checker; imports only the supplied learner module."""
import importlib.util
import sys
from pathlib import Path


class MetadataOnly(dict):
    def __getitem__(self, key):
        if key in ('body', 'vector'):
            raise AssertionError('Content access belongs after authorization')
        return super().__getitem__(key)

    def get(self, key, default=None):
        if key in ('body', 'vector'):
            raise AssertionError('Unexpected content access')
        return super().get(key, default)


def check(path):
    spec = importlib.util.spec_from_file_location('learner', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    rows = [MetadataOnly(id='r1', tenant='north', roles=['analyst'], language='en', published='2026-02-03T00:00:00Z'),
            MetadataOnly(id='r2', tenant='north', roles=['analyst'], language='en', published='2026-02-04T00:00:00Z'),
            MetadataOnly(id='r3', tenant='south', roles=['analyst'], language='en', published='2026-02-03T00:00:00Z'),
            MetadataOnly(id='r4', tenant='north', roles=['admin'], language='en', published='2026-02-03T00:00:00Z'),
            MetadataOnly(id='r5', tenant='north', roles=[], language='en', published='2026-02-03T00:00:00Z'),
            MetadataOnly(id='r6', tenant='north', roles=['analyst'], language=None, published='2026-02-03T00:00:00Z')]
    p = {'language': 'en', 'start': '2026-02-03T05:30:00+05:30', 'end': '2026-02-04T00:00:00Z'}
    assert module.select(rows, 'north', {'analyst'}, p) == ['r1']
    assert module.select(rows, 'north', {'analyst'}, {}) == ['r1', 'r2', 'r6']
    assert module.select(rows, 'north', {'admin'}, p) == ['r4']
    assert module.select(rows, 'absent', {'analyst'}, {}) == []
    assert module.select(list(reversed(rows)), 'north', {'analyst'}, p) == ['r1']
    for bad in ({'language': None}, {'start': '2026-02-03'}, {'end': 'bad'},
                {'start': '2026-02-04T00:00:00Z', 'end': '2026-02-03T00:00:00Z'},
                {'tenant': 'south'}, {'language': ['en']}):
        try:
            module.select(rows, 'north', {'analyst'}, bad)
        except ValueError:
            pass
        else:
            raise AssertionError('Malformed/unallowed predicate was accepted')
    print('Fresh metadata-only construction checks pass.')


if __name__ == '__main__':
    check(Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name('implement.py'))
