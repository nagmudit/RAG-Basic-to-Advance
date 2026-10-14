"""Fresh bounded construction gate; reference implementations are not imported."""
import argparse
import importlib.util


def check(path):
    spec = importlib.util.spec_from_file_location('learner', path)
    learner = importlib.util.module_from_spec(spec); spec.loader.exec_module(learner)
    proposals = [
        {'text': 'A17 trusted certificate', 'atoms': {'A17'}, 'lock': 'bound'},
        {'text': ' A17  trusted certificate ', 'atoms': {'A17'}, 'lock': 'bound'},
        {'text': 'A18 trusted certificate', 'atoms': {'A18'}, 'lock': 'bound'},
        {'text': 'A17 reload store', 'atoms': {'A17'}, 'lock': 'other'},
        {'text': 'A17 renewal recovery', 'atoms': {'A17'}, 'lock': 'bound'},
        {'text': 'A17 extra branch', 'atoms': {'A17'}, 'lock': 'bound'}]
    selected, reasons = learner.admit_toy(' A17  renewal ', {'A17'}, proposals, 'bound')
    assert selected == ['A17 renewal', 'A17 trusted certificate', 'A17 renewal recovery']
    assert reasons == [None, 'duplicate', 'protected_atom_change', 'anchor_mismatch', None, 'branch_budget']
    _, reasons = learner.admit_toy('A17 renewal', {'A17'}, proposals[:1], 'bound', max_words=4)
    assert reasons == ['word_budget']
    for kw in ({'max_branches': True}, {'max_words': 0}, {'max_words': 1}):
        try: learner.admit_toy('A17 renewal', {'A17'}, [], 'bound', **kw)
        except ValueError: pass
        else: raise AssertionError('Invalid budget accepted')
    deps = {'retry': [], 'trust': [], 'combine': ['retry', 'trust'], 'publish': ['combine']}
    assert learner.ready_toy(deps, set()) == ['retry', 'trust']
    assert learner.ready_toy(deps, {'retry'}) == ['trust']
    assert learner.ready_toy(deps, {'retry', 'trust'}) == ['combine']
    assert learner.ready_toy(deps, {'retry', 'trust', 'combine'}) == ['publish']
    for ds, completed in (({'a': ['missing']}, set()), ({'a': ['b'], 'b': ['a'], 'free': []}, set()), (deps, {'missing'})):
        try: learner.ready_toy(ds, completed)
        except ValueError: pass
        else: raise AssertionError('Invalid graph/state accepted')
    print('Construction gate passed; now explain drift, partial failure and stopping without qrels.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('implementation'); args = parser.parse_args()
    check(args.implementation)
