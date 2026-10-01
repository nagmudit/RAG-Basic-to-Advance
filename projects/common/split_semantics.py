"""Declare the held-out unit rather than inferring it from document IDs."""


def validate_generalization(data):
    policy = data["generalization_unit"]
    split = data["document_split"]
    families = data["source_family"]
    documents = {d for group in split.values() for d in group}
    if set(families) != documents or any(not isinstance(f, str) or not f.strip() for f in families.values()):
        raise ValueError("Every split document needs exactly one explicit source family")
    groups = {name: set(families[d] for d in split[name]) for name in ("train", "validation", "test")}
    overlaps = {f"{a}/{b}": sorted(groups[a] & groups[b])
                for a, b in (("train", "validation"), ("train", "test"), ("validation", "test"))}
    if policy not in ("new-query-document-holdout-with-family-overlap", "source-family-holdout"):
        raise ValueError("Unknown generalization unit")
    if policy == "source-family-holdout" and any(overlaps.values()):
        raise ValueError("Source-family holdout requires disjoint train/dev/test families")
    return {"unit": policy, "families_by_split": {n: sorted(v) for n, v in groups.items()},
            "family_overlap": overlaps,
            "unseen_family_transfer_established": False}
