import tempfile
import unittest
from pathlib import Path
from dircsaf import connect, add_object
from stewardship import initialize, add_evidence, save_assessment, create_action, transition_action, dashboard

class StewardshipTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.db=connect(Path(self.tmp.name)/"test.db")
        initialize(self.db)
        add_object(self.db,{"id":"S-1","title":"Fictional textile","expected_location":"Store 1","source":"synthetic"})
    def tearDown(self):
        self.db.close();self.tmp.cleanup()
    def test_evidence_recorded_not_verified(self):
        e=add_evidence(self.db,"S-1","photo","synthetic-photo-1","registrar")
        self.assertEqual(e["verification_status"],"reference_recorded_not_authenticated")
        self.assertEqual(dashboard(self.db)["counts"]["evidence"],1)
    def test_action_approval_and_verification(self):
        a=create_action(self.db,"S-1","Inspect textile","Visible discoloration","high")
        with self.assertRaises(ValueError):
            transition_action(self.db,a["id"],"registrar","verified","proof")
        transition_action(self.db,a["id"],"conservator","approved")
        transition_action(self.db,a["id"],"conservator","in_progress")
        transition_action(self.db,a["id"],"conservator","implemented")
        with self.assertRaises(ValueError):
            transition_action(self.db,a["id"],"conservator","verified")
        transition_action(self.db,a["id"],"reviewer","verified","signed-check-2")
        self.assertEqual(dashboard(self.db)["counts"]["verified_actions"],1)
    def test_persist_assessment(self):
        a=save_assessment(self.db,"S-1","logistic","v1",{"x":0.1},{"score":0.6,"validation_status":"unvalidated"})
        self.assertEqual(a["validation_status"],"unvalidated")
        self.assertEqual(dashboard(self.db)["counts"]["assessments"],1)
if __name__=="__main__":
    unittest.main()
