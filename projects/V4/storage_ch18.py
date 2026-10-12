"""Logical page/cache mechanism. Counts are not measured SSD latency or DiskANN."""
from collections import OrderedDict


def read_beam(node_ids, node_to_page, cache, capacity):
    """Return per-node hit/miss decisions and coalesced missed pages.

    Snapshot residency at beam entry; collect unique misses in encounter order,
    then complete reads in that order and update LRU. Cache lists are oldest-first.
    Two misses to the same page in a beam create ONE page request, not two.
    """
    if capacity < 1 or len(cache) > capacity or len(cache) != len(set(cache)):
        raise ValueError("Invalid LRU state")
    state = OrderedDict((page, None) for page in cache)
    decisions, requests, evictions = [], [], []
    resident = set(state)
    for node in node_ids:
        page = node_to_page[node]
        hit = page in resident
        decisions.append({"node_id": node, "page_id": page, "cache_hit_at_beam_entry": hit})
        if hit:
            state.move_to_end(page)
        elif page not in requests:
            requests.append(page)
    for page in requests:
        state[page] = None
        state.move_to_end(page)
        if len(state) > capacity:
            evictions.append(state.popitem(last=False)[0])
    return {"decisions": decisions, "requested_pages": requests,
            "evicted_pages": evictions, "cache_after": list(state)}
