"""Independent answer to the bounded lab; inspect only after construction.

Sorted retained list makes invariants visible (O(ef) updates). The full teaching
engine uses a worst-first heap instead. No import of that engine is used here.
"""
import heapq


def d2(a, b):
    return sum((x-y)**2 for x, y in zip(a, b))


def search_layer(query, vectors, adjacency, entry_ids, ef):
    visited, scored, frontier, retained, events = set(), [], [], [], []
    for item in sorted(set(entry_ids)):
        pair = (d2(query, vectors[item]), item)
        visited.add(item)
        scored.append(item)
        heapq.heappush(frontier, pair)
        retained.append(pair)
    retained = sorted(retained)[:ef]
    while frontier:
        value, current = heapq.heappop(frontier)
        if len(retained) == ef and (value, current) > retained[-1]:
            break
        for item in sorted(adjacency[current]):
            if item in visited:
                continue
            visited.add(item)
            scored.append(item)
            pair = (d2(query, vectors[item]), item)
            if len(retained) < ef or pair < retained[-1]:
                heapq.heappush(frontier, pair)
                retained = sorted(retained+[pair])[:ef]
        events.append({"current_id": current,
                       "retained_ids": [i for _, i in retained],
                       "frontier_ids": [i for _, i in sorted(frontier)]})
    return {"ranking": [(i, d) for d, i in retained], "scored_ids": scored, "events": events}


def select_neighbors(center, candidates, vectors, limit):
    selected = []
    for item in sorted(set(candidates), key=lambda i: (d2(center, vectors[i]), i)):
        if len(selected) == limit:
            break
        if all(d2(vectors[item], vectors[s]) >= d2(center, vectors[item]) for s in selected):
            selected.append(item)
    return selected
