"""Correctness checks for the Chapter 3 diagnostic, without timing assertions."""

import unittest

from measurements import linear_find, make_queries, make_records, measure_size


class MeasurementTests(unittest.TestCase):
    def test_scan_and_dictionary_have_the_same_exact_id_behavior(self):
        records = make_records(12)
        by_id = {record["id"]: record for record in records}
        for key in ("S00000", "S00006", "S00011", "M00000"):
            self.assertEqual(linear_find(records, key), by_id.get(key))

    def test_query_workload_is_seeded_and_balanced(self):
        first = make_queries(12, query_count=20, seed=7)
        self.assertEqual(first, make_queries(12, query_count=20, seed=7))
        self.assertEqual(sum(key.startswith("S") for key in first), 10)
        self.assertEqual(sum(key.startswith("M") for key in first), 10)
        self.assertTrue(all(key.startswith("M") for key in make_queries(12, 20, 7, 0.0)))
        self.assertTrue(all(key.startswith("S") for key in make_queries(12, 20, 7, 1.0)))

    def test_report_keeps_raw_samples_and_units(self):
        row = measure_size(12, query_count=20, trials=2, seed=7)
        self.assertEqual(len(row["scan_us_per_lookup_samples"]), 2)
        self.assertEqual(len(row["dict_us_per_lookup_samples"]), 2)
        self.assertEqual(row["hits_per_trial"], 10)
        self.assertGreater(row["json_utf8_bytes"], 0)


if __name__ == "__main__":
    unittest.main()
