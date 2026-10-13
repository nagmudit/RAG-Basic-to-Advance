"""Write before reading the project or separate answer."""


def word_windows(text,size,overlap=0):
    r"""Return half-open code-point intervals for whitespace-word windows.

    Use consecutive \S+ matches in original text. Validate positive integer size
    and integer 0<=overlap<size; booleans are invalid. Advance size-overlap words,
    emit a final shortened window once, then stop. Empty/whitespace-only -> [].
    Do not split/rejoin text to invent source offsets.
    """
    raise NotImplementedError('Construct the source-preserving chunker')
