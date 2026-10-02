"""HNSW behavioral, telemetry and evidence continuity tests."""
import importlib.util
import json
import math
import random
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent/"common"))
from experiment_trace import TraceCollector, versions, validate
from hnsw_ch17 import HNSW, search_layer, select_neighbors, squared_l2


def rows(points):
    return [{"item_id": i, "vector": v, "allowed_scopes": ["public"]} for i, v in points.items()]


def replay(detail, ef):
    """Reconstruct actual queues from initial state plus admission/eviction deltas."""
    events = detail["events"]
    first = events[0]
    frontier, retained = dict(first["frontier"]), dict(first["retained"])
    for event in events[1:]:
        current = event["current_id"]
        assert current == min(frontier, key=lambda i: (frontier[i], i))
        value = frontier.pop(current)
        if event["action"] == "stop_bound":
            worst = max(retained, key=lambda i: (retained[i], i))
            assert (value, current) > (retained[worst], worst)
            break
        for decision in event["decisions"]:
            item, distance = decision["item_id"], decision["squared_distance"]
            if decision["admitted"]:
                frontier[item] = distance
                retained[item] = distance
                if decision["evicted_id"] is not None:
                    retained.pop(decision["evicted_id"])
            assert len(retained) <= ef
        if "frontier" in event:
            assert dict(event["frontier"]) == frontier
            assert dict(event["retained"]) == retained
    return sorted(retained.items(), key=lambda p: (p[1], p[0]))


class GraphMechanics(unittest.TestCase):
    def test_local_minimum_and_frontier_recovery(self):
        f = json.loads((HERE/"graph_fixture_ch17.json").read_text())
        results = []
        for ef in (1, 2):
            ranking, detail = search_layer(f["query"], f["vectors"], f["adjacency"], ["A"], ef, capture="full")
            self.assertEqual(ranking, replay(detail, ef))
            self.assertEqual(len(detail["scored_ids"]), len(set(detail["scored_ids"])))
            results.append(ranking[0][0])
        self.assertEqual(results, ["B", "D"])

    def test_disconnected_graph_is_not_fixed_by_large_ef(self):
        vs = {"a": (3.,), "b": (2.,), "hidden": (0.,)}
        ranked, detail = search_layer((0.,), vs, {"a": ["b"], "b": ["a"], "hidden": []}, ["a"], 99)
        self.assertEqual([i for i, _ in ranked], ["b", "a"])
        self.assertNotIn("hidden", detail["visited_ids"])

    def test_stable_ties_and_cycles(self):
        vs = {"z": (1.,), "a": (-1.,), "b": (1.,)}
        graph = {i: [j for j in vs if j != i] for i in vs}
        ranked, _ = search_layer((0.,), vs, graph, ["z"], 2)
        self.assertEqual([i for i, _ in ranked], ["a", "b"])

    def test_diversity_selection(self):
        vs = {"P": (1., 0.), "Q": (1.2, .1), "R": (0., 2.)}
        self.assertEqual(select_neighbors((0., 0.), vs, vs, 2), ["P", "R"])
        self.assertEqual(select_neighbors((0., 0.), ["P", "Q"], vs, 2), ["P"])
        self.assertEqual(select_neighbors((0., 0.), ["P", "Q"], vs, 2, keep_pruned=True), ["P", "Q"])

    def test_hierarchy_insertion_and_degree_limits(self):
        rng = random.Random(17)
        data = rows({f"v{i:03d}": [rng.random(), rng.random()] for i in range(70)})
        graph = HNSW(data, scope="public", M=3, ef_construction=20)
        graph.validate_structure()
        self.assertGreater(len(graph.layers), 1)
        self.assertEqual(graph.levels[graph.entry_id], len(graph.layers)-1)
        a = HNSW(scope="public", M=2)
        a.add(rows({"a": [0., 0.]})[0], level=2)
        trace = a.add(rows({"b": [1., 0.]})[0], level=0)
        self.assertEqual(trace["layers"][0]["selected_ids"], ["a"])
        self.assertEqual(a.layers[0]["a"], ["b"])
        self.assertEqual(set(a.layers[2]), {"a"})

    def test_seed_determinism_and_large_ef_exact_on_connected_fixture(self):
        data = rows({f"v{i:02d}": (math.cos(i/7), math.sin(i/7)) for i in range(35)})
        a = HNSW(data, scope="public", M=4, ef_construction=32)
        b = HNSW(data, scope="public", M=4, ef_construction=32)
        self.assertEqual(a.snapshot(), b.snapshot())
        for q in ((1., 0.), (.2, -.3), (-1., 1.)):
            ranked, work = a.search(q, scope="public", k=4, ef_search=100)
            expected = sorted(((r["item_id"], -squared_l2(q, r["vector"])) for r in data), key=lambda p: (-p[1], p[0]))[:4]
            self.assertEqual(ranked, expected)
            for layer in work["graph_trace"]:
                retained = replay(layer, 100 if layer["layer"] == 0 else 1)
                self.assertEqual([i for i, _ in retained], [i for i, _ in work["candidate_stages"][f"layer_{layer['layer']}_retained"]])

    def test_scope_gate_precedes_graph_membership_and_scoring(self):
        data = rows({"a": [1., 0.], "b": [0., 1.]})
        data.append({"item_id": "private", "vector": [0., 0.], "allowed_scopes": ["legal"]})
        graph = HNSW(data, scope="public")
        self.assertNotIn("private", graph.vectors)
        result, work = graph.search((0., 0.), scope="public")
        self.assertNotIn("private", dict(work["candidate_stages"]["scored"]))
        with self.assertRaises(ValueError):
            graph.search((0., 0.), scope="legal")

    def test_delete_blocks_scoring_and_deleted_entry_fallback(self):
        graph = HNSW(rows({"a": [0., 0.], "b": [1., 0.], "c": [2., 0.]}), scope="public")
        graph.delete(graph.entry_id)
        ranked, work = graph.search((0., 0.), scope="public")
        self.assertTrue(set(dict(work["candidate_stages"]["scored"])).isdisjoint(graph.deleted))
        for item in graph.vectors:
            graph.delete(item)
        self.assertEqual(graph.search((0., 0.), scope="public")[0], [])

    def test_empty_and_invalid_inputs(self):
        graph = HNSW(scope="public")
        self.assertEqual(graph.search([1.], scope="public")[0], [])
        self.assertEqual(graph.payload_lower_bounds()["vector_float32_bytes"], 0)
        graph.add(rows({"a": [1., 0.]})[0])
        for q, ef in (([float("nan"), 0.], 2), ([1.], 2), ([1., 0.], 1)):
            with self.assertRaises(ValueError):
                graph.search(q, scope="public", k=2, ef_search=ef)
        with self.assertRaises(ValueError):
            graph.add(rows({"a": [2., 0.]})[0])

    def test_checked_serialization_and_query_only_reload(self):
        graph = HNSW(rows({"a": [1., 0.], "b": [0., 1.]}), scope="public", source_version="fixture-v1")
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)/"graph.json"
            graph.save(path)
            restored = HNSW.load(path, expected_source_version="fixture-v1", expected_digest=graph.snapshot()["sha256"])
            self.assertEqual(graph.search([1., 0.], scope="public"), restored.search([1., 0.], scope="public"))
            with self.assertRaises(ValueError):
                restored.add(rows({"new": [2., 2.]})[0])
            bad = json.loads(path.read_text())
            bad["body"]["vectors"]["a"][0] = .5
            path.write_text(json.dumps(bad))
            with self.assertRaises(ValueError):
                HNSW.load(path, expected_source_version="fixture-v1", expected_digest=graph.snapshot()["sha256"])

    def test_invalid_request_emits_redacted_correlated_error(self):
        graph = HNSW(rows({"a": [0., 1.]}), scope="public")
        collector = TraceCollector("fixture", versions("c", "q", None, "i", None), {"a"})
        with self.assertRaises(ValueError):
            collector.execute("q1", "hnsw", 0, lambda: graph.search([float("nan"), 0.], scope="public"))
        record = collector.records[0]
        validate(record, {"a"})
        self.assertEqual(record["status"], "invalid")
        self.assertEqual(record["reason"], "invalid_input")

    def test_learner_solution_passes_independent_fixtures(self):
        root = HERE.parents[1]
        spec = importlib.util.spec_from_file_location("checker17", root/"labs/chapter-17/check_implementation.py")
        checker = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(checker)
        checker.check(checker.load(root/"solutions/code/chapter_17_mechanisms.py"))


class CheckedRecord(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((HERE/"chapter-17-experiment.json").read_text(encoding="utf-8"))

    def test_source_hash_and_evidence_identity(self):
        from experiment_ch15 import source_hash
        for name, digest in self.data["code_sha256"].items():
            self.assertEqual(source_hash(HERE/name), digest)
        self.assertEqual(self.data["v0_diagnostic"]["evidence_manifest_sha256"],
                         "6d78c210769d0992dd530ab66349792077f1b89564c368f63797301ebc66523c")

    def test_all_samples_and_actual_frontier_replay(self):
        for workload in [*self.data["synthetic"], self.data["v0_diagnostic"]]:
            eligible_ids = set(workload["request_samples"][0]["raw_candidate_ids"])
            if workload["scope"] == "support-team":
                eligible_ids = set(workload["cases"][0]["modes"]["exact"]["candidate_ids"])
                eligible_ids = set(next(r for r in workload["request_samples"] if r["mode"] == "exact")["raw_candidate_ids"])
            for record in workload["request_samples"]:
                validate(record, eligible_ids)
                self.assertEqual(record["workload_id"], workload["workload_id"])
                self.assertFalse(any(i.startswith("D10:") for i in record["raw_candidate_ids"]))
                if record.get("graph_trace"):
                    cfg = workload["configuration"][record["mode"]]
                    for layer in record["graph_trace"]:
                        result = replay(layer, cfg["efSearch"] if layer["layer"] == 0 else 1)
                        self.assertEqual([i for i, _ in result], record["intermediate_candidate_ids"][f"layer_{layer['layer']}_retained"])

    def test_same_workload_preserves_historical_oracles(self):
        old = json.loads((HERE/"chapter-16-experiment.json").read_text(encoding="utf-8"))
        for current, historical in zip(self.data["synthetic"], old["synthetic"]):
            self.assertEqual(current["workload_id"], f"ch16-synthetic-n{historical['n']}-d{historical['dimension']}-v1")
            self.assertEqual([c["oracle_ids"] for c in current["cases"]], [c["exact_ids"] for c in historical["cases"]])
        for case in self.data["v0_diagnostic"]["cases"]:
            self.assertEqual(case["modes"]["ivf_flat_p3"]["candidate_ids"], case["oracle_ids"])
            self.assertIsNone(case["modes"]["exact"]["answer_correctness"])

    def test_workload_bindings_counts_and_hand_cutoff(self):
        registry = json.loads((HERE.parents[1]/"evaluation/WORKLOAD_REGISTRY.json").read_text(encoding="utf-8"))
        entries = {r["workload_id"]: r for r in registry["workloads"]}
        for w in [*self.data["synthetic"], self.data["v0_diagnostic"]]:
            entry = entries[w["workload_id"]]
            self.assertIn(17, entry["chapters_using_it"])
            self.assertEqual(entry["number_of_queries"], w["query_count"])
            for field in ("corpus_version", "query_set_version", "qrels_version"):
                self.assertEqual(w["versions"][field], entry[field])
        hand = self.data["hand"]
        self.assertEqual(hand["fixture"]["qrels_version"], "geometric-exact-top1")
        self.assertEqual(entries[hand["workload_id"]]["number_of_queries"], 1)


if __name__ == "__main__":
    unittest.main()
