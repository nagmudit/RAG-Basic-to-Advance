"""Construct before reference inspection: bounded page coalescing and LRU.

Inputs: valid node/page map, nonduplicate oldest-first cache <= capacity, positive
capacity, ordered beam of node IDs. Classify using residency at beam entry; unique
missed pages requested in encounter order. Touch hits, then complete missed reads
in request order; evict oldest when capacity is exceeded. Do not time an SSD.
"""


def read_beam(node_ids, node_to_page, cache, capacity):
    """Return decisions[{node_id,page_id,cache_hit_at_beam_entry}],
    requested_pages, evicted_pages, cache_after (oldest-first).
    """
    raise NotImplementedError("Construct page coalescing and cache updates")
