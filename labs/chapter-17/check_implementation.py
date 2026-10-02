"""Fresh, visible feedback fixtures; no reference ANN engine imports."""
import argparse
import importlib.util
from pathlib import Path


def load(path):
    spec = importlib.util.spec_from_file_location("learner_ch17", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check(m):
    points = {"start": (3., 0.), "near": (1., 0.), "bridge": (1.2, 0.), "goal": (.2, 0.)}
    edges = {"start": ["near"], "near": ["start", "bridge"],
             "bridge": ["near", "goal"], "goal": ["bridge"]}
    narrow = m.search_layer((0., 0.), points, edges, ["start"], 1)
    wide = m.search_layer((0., 0.), points, edges, ["start"], 2)
    assert narrow["ranking"][0][0] == "near", "Expected measured local-minimum failure"
    assert wide["ranking"][0][0] == "goal", "Bridge must remain expandable"
    assert len(wide["scored_ids"]) == 4 > 2, "ef is not a visit budget"
    assert len(wide["scored_ids"]) == len(set(wide["scored_ids"]))
    assert all(len(e["retained_ids"]) <= 2 for e in wide["events"])
    assert any("bridge" in e["frontier_ids"] for e in wide["events"])
    tied = {"a": (1., 0.), "z": (-1., 0.)}
    assert m.search_layer((0., 0.), tied, {"a": ["z"], "z": ["a"]}, ["z"], 1)["ranking"] == [("a", 1.)]
    disconnected = {**edges, "goal": []}
    disconnected["bridge"] = ["near"]
    assert m.search_layer((0., 0.), points, disconnected, ["start"], 10)["ranking"][0][0] == "near"
    candidates = {"p": (1., 0.), "redundant": (1.2, .1), "other": (0., 2.)}
    assert m.select_neighbors((0., 0.), list(candidates), candidates, 2) == ["p", "other"]
    return {"local_minimum_preserved": True, "frontier_recovery": True,
            "cycle_tie_disconnection_diversity_checked": True}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--implementation", type=Path, default=Path(__file__).with_name("implement.py"))
    args = parser.parse_args()
    print(check(load(args.implementation)))
