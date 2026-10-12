"""Native adapter, logical I/O and preserved benchmark evidence tests."""
import importlib.util
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import faiss
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"common"))
from experiment_trace import TraceCollector, versions, validate
from native_ch18 import NativeIndex, single_thread, oracle
from storage_ch18 import read_beam


def rows(points):
    return [{"item_id":i,"vector":v,"allowed_scopes":["public"]} for i,v in points.items()]


class Mechanisms(unittest.TestCase):
    def setUp(self):
        self.thread_context=single_thread()
        self.thread_context.__enter__()
        self.data=rows({"a":(1.,0.),"b":(0.,1.),"c":(-1.,0.),"d":(0.,-1.)})

    def tearDown(self):
        self.thread_context.__exit__(None,None,None)

    def build(self,data=None,kind="flat"):
        return NativeIndex(self.data if data is None else data,dimension=2,scope="public",kind=kind,
                           source_version="geometry-v1",model_version="none")

    def test_hand_exact_order_and_within_pool_ties(self):
        index=self.build()
        result,work=index.search((1.,0.),scope="public",k=3,depth=4)
        self.assertEqual(result,[("a",0.),("b",-2.),("d",-2.)])
        self.assertEqual(result,oracle(self.data,(1.,0.),k=3))
        self.assertEqual(len(work["candidate_stages"]["exact_refinement_pool"]),4)

    def test_scope_exclusion_precedes_conversion_and_index(self):
        data=self.data+[{"item_id":"private","vector":[float("nan"),float("nan")],"allowed_scopes":["legal"]}]
        index=self.build(data,"hnsw")
        self.assertEqual(index.index.ntotal,4)
        _,work=index.search((1.,0.),scope="public",depth=4,ef_search=16)
        self.assertNotIn("private",dict(work["candidate_stages"]["scored"]))
        with self.assertRaises(ValueError): index.search((1.,0.),scope="legal")

    def test_invalid_input_redacted_request(self):
        index=self.build()
        trace=TraceCollector("fixture",versions("c","q",None,"i","m"),index.ids)
        for query in ((float("nan"),0.),(1.,), (1e100,0.)):
            with self.assertRaises(ValueError):
                trace.execute("q0","native",0,lambda: index.search(query,scope="public"))
        self.assertEqual(len(trace.records),3)
        for record in trace.records:
            self.assertEqual(record["status"],"invalid")
            self.assertEqual(record["reason"],"invalid_input")
            validate(record,index.ids)

    def test_metadata_shortlist_loss_and_empty_reason(self):
        index=NativeIndex(rows({f"v{i}":(float(i),0.) for i in range(8)}),dimension=2,scope="public",source_version="tag-v1")
        predicate=lambda i:i=="v7"
        result,work=index.search((0.,0.),scope="public",k=1,depth=2,public_predicate=predicate)
        self.assertEqual(result,[])
        self.assertEqual(work["candidate_stages"]["native_returned"],[("v0",0.),("v1",-1.)])
        self.assertEqual(work["candidate_stages"]["metadata_survivors"],[])
        self.assertEqual(work["reason"],"no_metadata_survivor_in_shortlist")
        pre=NativeIndex(rows({"v7":(7.,0.)}),dimension=2,scope="public",source_version="tag-v1")
        self.assertEqual(pre.search((0.,0.),scope="public",k=1)[0],[("v7",-49.)])

    def test_full_shortlist_native_graph_parity_on_fixture(self):
        data=rows({f"p{i:02d}":(math.cos(i/5),math.sin(i/5)) for i in range(25)})
        graph=self.build(data,"hnsw")
        result,work=graph.search((.2,.8),scope="public",depth=25,ef_search=64)
        self.assertEqual(result,oracle(data,(.2,.8)))
        self.assertIsNone(work["native_frontier"])
        self.assertGreater(work["native_work"]["distance_evaluations"],0)

    def test_graph_seed_one_thread_repeatability(self):
        a,b=self.build(kind="hnsw"),self.build(kind="hnsw")
        self.assertEqual(a.index_digest,b.index_digest)

    def test_snapshot_reload_parity_and_checked_bytes(self):
        for kind in ("flat","hnsw"):
            index=self.build(kind=kind)
            with tempfile.TemporaryDirectory() as temporary:
                metadata=index.save(temporary)
                self.assertEqual(Path(temporary,"index.faiss").stat().st_size,len(index.payload))
                reloaded=NativeIndex.load(temporary,self.data,expected_manifest_digest=metadata["manifest_sha256"],
                    scope="public",expected_source_version="geometry-v1",expected_model_version="none")
                self.assertEqual(index.search((1.,0.),scope="public")[0],reloaded.search((1.,0.),scope="public")[0])

    def test_changed_vector_same_id_fails_before_native_deserialize(self):
        index=self.build()
        changed=[{**r,"vector":(5.,5.)} if r["item_id"]=="a" else r for r in self.data]
        with tempfile.TemporaryDirectory() as temporary:
            metadata=index.save(temporary)
            with patch("native_ch18.faiss.deserialize_index") as reader:
                with self.assertRaises(ValueError): NativeIndex.load(temporary,changed,
                    expected_manifest_digest=metadata["manifest_sha256"],scope="public",
                    expected_source_version="geometry-v1",expected_model_version="none")
                reader.assert_not_called()

    def test_payload_and_source_version_mismatch_rejected(self):
        index=self.build()
        with tempfile.TemporaryDirectory() as temporary:
            metadata=index.save(temporary)
            kwargs=dict(expected_manifest_digest=metadata["manifest_sha256"],scope="public",expected_model_version="none")
            with self.assertRaises(ValueError): NativeIndex.load(temporary,self.data,expected_source_version="wrong",**kwargs)
            Path(temporary,"index.faiss").write_bytes(b"corrupt")
            with self.assertRaises(ValueError): NativeIndex.load(temporary,self.data,expected_source_version="geometry-v1",**kwargs)

    def test_empty_roster_and_parameter_validation(self):
        index=self.build([])
        self.assertEqual(index.search((1.,0.),scope="public")[1]["reason"],"no_eligible_vectors")
        with self.assertRaises(ValueError): self.build().search((1.,0.),scope="public",depth=1,k=2)
        with self.assertRaises(ValueError): self.build(kind="hnsw").search((1.,0.),scope="public",depth=8,ef_search=4)

    def test_batch_is_matrix_kernel_not_individual_latency(self):
        index=self.build()
        result=index.batch_kernel([(1.,0.),(0.,1.)],depth=4)
        self.assertEqual(len(result["candidate_ids_by_query"]),2)
        self.assertGreater(result["queries_per_second"],0)
        self.assertNotIn("per_query_latency",result)

    def test_native_hnsw_does_not_promise_delete(self):
        import numpy as np
        with self.assertRaises(RuntimeError): self.build(kind="hnsw").index.remove_ids(np.asarray([0],dtype="int64"))

    def test_page_coalescing_eviction_and_independent_answer(self):
        pages={"a":10,"b":10,"c":20,"d":30}
        actual=read_beam(["a","b","c","d"],pages,[20],2)
        self.assertEqual(actual["requested_pages"],[10,30])
        self.assertEqual(actual["cache_after"],[10,30])
        self.assertEqual(actual["evicted_pages"],[20])
        spec=importlib.util.spec_from_file_location("check18",HERE.parents[1]/"labs/chapter-18/check_implementation.py")
        module=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.check(module.load(HERE.parents[1]/"solutions/code/chapter_18_mechanisms.py"))
        module.check(type("Reference",(),{"read_beam":staticmethod(read_beam)}))


class RecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((HERE/"chapter-18-experiment.json").read_text(encoding="utf-8"))

    def test_code_hashes_and_historical_oracles(self):
        from experiment_ch15 import source_hash
        for name,sha in self.data["code_sha256"].items(): self.assertEqual(source_hash(HERE/name),sha)
        old=json.loads((HERE/"chapter-17-experiment.json").read_text())
        self.assertEqual([c["oracle_ids"] for c in self.data["synthetic"]["cases"]], [c["oracle_ids"] for c in old["synthetic"][1]["cases"]])
        self.assertEqual([c["oracle_ids"] for c in self.data["v0_diagnostic"]["cases"]], [c["oracle_ids"] for c in old["v0_diagnostic"]["cases"]])

    def test_registry_identities_and_content_bound_evidence(self):
        registry=json.loads((HERE.parents[1]/"evaluation/WORKLOAD_REGISTRY.json").read_text())
        entries={r["workload_id"]:r for r in registry["workloads"]}
        for w in [self.data["synthetic"],self.data["v0_diagnostic"],*self.data["public_tag_filters"]]:
            entry=entries[w["workload_id"]]
            self.assertIn(18,entry["chapters_using_it"])
            self.assertEqual(entry["number_of_queries"],w["query_count"])
            for field in ("corpus_version","query_set_version","qrels_version"):
                self.assertEqual(entry[field],w["versions"][field])
        self.assertEqual(self.data["v0_diagnostic"]["evidence_manifest_sha256"], entries["ch13-stress-probes-v1"]["evidence_manifest_sha256"])

    def test_correlated_actual_shortlists_and_reference_frontiers(self):
        request_ids=[]
        for w in [self.data["synthetic"],self.data["v0_diagnostic"],*self.data["public_tag_filters"]]:
            allowed=set(w.get("insertion_order",[])) if "insertion_order" in w else {f"s{i:05d}" for i in range(1024)}
            for r in w["request_samples"]:
                validate(r,allowed)
                request_ids.append(r["request_id"])
                if r["mode"]=="inspectable_reference_e24":
                    self.assertTrue(r["graph_trace"])
                    self.assertIn("not the native",r["reference_warning"])
                elif "batch" not in r["mode"] and r["mode"]!="query_encode":
                    self.assertEqual(r["raw_pool_semantics"],"native_returned_shortlist_only")
                    self.assertEqual(r["raw_candidate_ids"],r["intermediate_candidate_ids"]["native_returned"])
                    self.assertIsNone(r["native_frontier"])
                    self.assertTrue(set(r["final_candidate_ids"]) <= set(r["intermediate_candidate_ids"]["exact_refinement_pool"]))
                if "batch_query_ids" in r:
                    self.assertEqual(len(r["batch_query_ids"]),len(r["candidate_ids_by_query"]))
                    for ids in r["candidate_ids_by_query"]: self.assertTrue(set(ids)<=allowed)
                self.assertFalse(any(i.startswith("D10:") for i in r["raw_candidate_ids"]))
        self.assertEqual(len(request_ids),len(set(request_ids)))

    def test_predicate_oracle_parity_and_real_postfilter_underfill(self):
        for w in self.data["public_tag_filters"]:
            self.assertEqual(w["summaries"]["prefilter_flat"]["mean_filtered_exact_neighbor_recall_at_2"],1.)
            self.assertGreater(w["summaries"]["post_flat_r8"]["underfill_rate"],0.)
            for c in w["cases"]:
                for mode in c["modes"].values(): self.assertTrue(set(mode["candidate_ids"]) <= set(w["eligible_ids"]))

    def test_native_file_size_and_payload_digest(self):
        import hashlib
        for workload in ("synthetic","support"):
            record=self.data["synthetic"] if workload=="synthetic" else self.data["v0_diagnostic"]
            for kind in ("flat","hnsw"):
                payload=(HERE/"index_ch18"/workload/kind/"index.faiss").read_bytes()
                build=record["builds"][kind]
                self.assertEqual(len(payload),build["serialized_native_bytes"])
                self.assertEqual(hashlib.sha256(payload).hexdigest(),build["native_index_sha256"])

    def test_logical_io_counts_are_not_a_disk_benchmark(self):
        w=self.data["logical_storage"]
        self.assertEqual([len(c["requested_pages"]) for c in w["cases"]],[2,1])
        self.assertIn("no SSD",w["measurement_kind"])
        for r in w["request_samples"]:
            validate(r,{"A","B","C","D"})
            self.assertEqual(r["reason"],"no_vector_search_or_storage_io_run")


if __name__=="__main__": unittest.main()
