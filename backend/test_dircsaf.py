import tempfile
import unittest
from pathlib import Path
from dircsaf import connect, add_object, observe, list_cases, review_case, risk_baseline, audit_events

class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = connect(Path(self.tmp.name)/"test.db")
        add_object(self.db, {"id":"OBJ-1","title":"Fictional ceramic vessel","expected_location":"Shelf A",
                             "source":"synthetic-test","condition":"poor"})
    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()
    def test_matching_observation_is_not_verified_identity(self):
        r=observe(self.db,"OBJ-1","shelf a","tester","photo-1")
        self.assertFalse(r["discrepancy"])
        self.assertEqual(r["verification_status"],"observation_consistent_unverified")
        self.assertEqual(list_cases(self.db),[])
    def test_discrepancy_requires_independent_review(self):
        r=observe(self.db,"OBJ-1","Shelf B","tester","photo-1")
        self.assertTrue(r["discrepancy"])
        self.assertEqual(len(list_cases(self.db)),1)
        with self.assertRaises(ValueError):
            review_case(self.db,r["case_id"],"curator","approved","photo-1")
        c=review_case(self.db,r["case_id"],"curator","approved","signed-inspection-2")
        self.assertEqual(c["status"],"approved")
        with self.assertRaises(ValueError):
            review_case(self.db,r["case_id"],"curator","approved","another")
        self.assertTrue(any(e["event_type"]=="case_reviewed" for e in audit_events(self.db)))
    def test_risk_is_explicit_non_ai_baseline(self):
        self.assertEqual(risk_baseline(self.db,"OBJ-1")["score"],2)
        observe(self.db,"OBJ-1","Shelf B","tester","photo-1")
        r=risk_baseline(self.db,"OBJ-1")
        self.assertEqual(r["score"],3)
        self.assertEqual(r["method"],"transparent_rule_baseline_v1")
    def test_invalid_inputs(self):
        with self.assertRaises(LookupError):
            observe(self.db,"missing","X","tester","evidence")
        with self.assertRaises(ValueError):
            observe(self.db,"OBJ-1","X","","evidence")
        with self.assertRaises(ValueError):
            add_object(self.db,{"id":"","title":"X","expected_location":"Y","source":"Z"})

if __name__ == "__main__":
    unittest.main()
