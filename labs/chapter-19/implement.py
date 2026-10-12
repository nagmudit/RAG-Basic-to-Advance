"""Implement before opening the reference or separate solution."""


def locate_span(blocks, start, end):
    """Ordered nonoverlapping positive-width blocks; half-open code-point spans.

    Validate all blocks and 0 <= start < end <= last block end. Return only
    positive intersections in order as block_id/canonical_overlap/locator.
    Separator-only spans return []. Empty maps cannot contain a valid span.
    Preserve whole source locators: do not fabricate inverse raw offsets.
    """
    raise NotImplementedError('Write the source-span mapper independently')
