"""Your construction starts here. Do not import the supplied reference."""


def admit_toy(original, protected, proposals, lock, max_branches=3, max_words=24):
    """Return (selected_texts, decision_reasons), reserving the original first.

    protected is a set of exact whitespace-delimited protected atoms. Each proposal
    has text, lock and atoms (its independently extracted protected-atom set).
    Reasons, in precedence order: anchor_mismatch, protected_atom_change,
    duplicate, branch_budget, word_budget; None means accepted.
    Normalize whitespace and casefold only the duplicate key. Count words across
    accepted inputs. Invalid positive-integer budgets or an oversized original
    must raise ValueError. Preserve proposal order. Inputs are otherwise valid.
    """
    raise NotImplementedError('Construct before opening the reference')


def ready_toy(dependencies, completed):
    """Return sorted pending tasks whose named dependencies all completed.

    Reject unknown completed IDs, missing dependencies and cycles, including
    cycles in disconnected components. Validate before returning ready tasks.
    You may assume each dependency list contains distinct task IDs.
    """
    raise NotImplementedError('Construct before opening the reference')
