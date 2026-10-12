"""Independent bounded answer. Inspect after your first attempt; no engine import."""


def read_beam(node_ids, node_to_page, cache, capacity):
    initial = set(cache)
    state, requested, decisions, evicted = list(cache), [], [], []
    for node in node_ids:
        page = node_to_page[node]
        hit = page in initial
        decisions.append({"node_id": node, "page_id": page, "cache_hit_at_beam_entry": hit})
        if hit:
            state.remove(page)
            state.append(page)
        elif page not in requested:
            requested.append(page)
    for page in requested:
        state.append(page)
        if len(state) > capacity:
            evicted.append(state.pop(0))
    return {"decisions": decisions, "requested_pages": requested,
            "evicted_pages": evicted, "cache_after": state}
