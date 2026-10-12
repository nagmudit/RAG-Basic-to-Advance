"""Fresh hand-expected fixtures; no native index or storage engine imports."""
import argparse
import importlib.util
from pathlib import Path


def load(path):
    spec = importlib.util.spec_from_file_location("learner18", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check(module):
    pages = {"a": 10, "b": 10, "c": 20, "d": 30}
    first = module.read_beam(["a", "b", "c", "d"], pages, [20], 2)
    assert first["requested_pages"] == [10, 30]
    assert first["cache_after"] == [10, 30]
    assert first["evicted_pages"] == [20]
    assert [d["cache_hit_at_beam_entry"] for d in first["decisions"]] == [False, False, True, False]
    second = module.read_beam(["b", "d", "c"], pages, first["cache_after"], 2)
    assert second["requested_pages"] == [20]
    assert second["cache_after"] == [30, 20]
    assert second["evicted_pages"] == [10]
    empty = module.read_beam([], pages, [10, 30], 2)
    assert empty["requested_pages"] == [] and empty["cache_after"] == [10, 30]
    return {"coalesced_requests": [2, 1], "beam_entry_residency_and_LRU_verified": True}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--implementation", type=Path, default=Path(__file__).with_name("implement.py"))
    args = parser.parse_args()
    print(check(load(args.implementation)))
