import importlib.util
import sys
from pathlib import Path


def check(path):
    spec = importlib.util.spec_from_file_location('learner22', path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    state = None
    first = {'revision': 2, 'digest': 'text-two', 'tombstone': False}
    state, status = module.apply(state, first)
    assert state == first and status == 'accepted'
    assert module.apply(state, dict(first)) == (state, 'duplicate')
    old = {'revision': 1, 'digest': 'text-one', 'tombstone': False}
    assert module.apply(state, old) == (state, 'stale')
    delete = {'revision': 3, 'digest': 'deletion-three', 'tombstone': True}
    deleted, status = module.apply(state, delete)
    assert deleted == delete and status == 'accepted' and state == first
    assert module.apply(deleted, first) == (deleted, 'stale')
    assert module.apply(deleted, delete) == (deleted, 'duplicate')
    recreate = {'revision': 4, 'digest': 'explicit-recreate-four', 'tombstone': False}
    assert module.apply(deleted, recreate) == (recreate, 'accepted')
    for bad in ({'revision': True, 'digest': 'x', 'tombstone': False},
                {'revision': 0, 'digest': 'x', 'tombstone': False},
                {'revision': 2, 'digest': '', 'tombstone': False},
                {'revision': 2, 'digest': 'x', 'tombstone': 'false'},
                {'revision': 3, 'digest': 'conflict-three', 'tombstone': True}):
        try: module.apply(deleted, bad)
        except ValueError: pass
        else: raise AssertionError('Invalid/conflicting event accepted')
    assert state == first and deleted == delete
    print('Fresh revision/tombstone construction checks pass.')


if __name__ == '__main__':
    check(Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).with_name('implement.py'))
