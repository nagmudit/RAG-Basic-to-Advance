"""Separate worked answer. Read only after completing the chapter's A0 gate."""


def admit_toy(original, protected, proposals, lock, max_branches=3, max_words=24):
    if type(max_branches) is not int or max_branches < 1 or type(max_words) is not int or max_words < 1:
        raise ValueError('Invalid budget')
    original = ' '.join(original.split()); used = len(original.split())
    if used > max_words: raise ValueError('Original over budget')
    selected = [original]; seen = {original.casefold()}; reasons = []
    for p in proposals:
        text = ' '.join(p['text'].split()); key = text.casefold()
        reason = ('anchor_mismatch' if p['lock'] != lock else
                  'protected_atom_change' if p['atoms'] - protected else
                  'duplicate' if key in seen else
                  'branch_budget' if len(selected) >= max_branches else
                  'word_budget' if used + len(text.split()) > max_words else None)
        reasons.append(reason)
        if reason is None:
            selected.append(text); seen.add(key); used += len(text.split())
    return selected, reasons


def ready_toy(dependencies, completed):
    if not set(completed) <= set(dependencies): raise ValueError('Unknown completion')
    if any(not set(ds) <= set(dependencies) for ds in dependencies.values()):
        raise ValueError('Missing dependency')
    seen = set()
    while len(seen) < len(dependencies):
        layer = {n for n, ds in dependencies.items() if n not in seen and set(ds) <= seen}
        if not layer: raise ValueError('Cycle')
        seen |= layer
    return sorted(n for n, ds in dependencies.items() if n not in completed and set(ds) <= set(completed))
