import tempfile
import unittest
from pathlib import Path
from dircsaf import connect,add_object
from sync import submit_observation
class SyncTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.db=connect(Path(self.tmp.name)/"sync.db")
        add_object(self.db,{"id":"A","title":"Fictional item","expected_location":"Shelf A","source":"synthetic"})
        self.payload={"client_id":"field-device-1","request_id":"obs-1","object_id":"A",
                      "observed_location":"Shelf B","observer":"tester","evidence_ref":"note-1"}
    def tearDown(self):
        self.db.close();self.tmp.cleanup()
    def test_retry_returns_same_observation(self):
        a=submit_observation(self.db,self.payload)
        b=submit_observation(self.db,self.payload)
        self.assertEqual(a,b)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM observations").fetchone()[0],1)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM cases").fetchone()[0],1)
    def test_key_reuse_with_different_data_rejected(self):
        submit_observation(self.db,self.payload)
        with self.assertRaises(ValueError):
            submit_observation(self.db,{**self.payload,"observed_location":"Shelf C"})
    def test_missing_key_rejected(self):
        with self.assertRaises(ValueError):
            submit_observation(self.db,{k:v for k,v in self.payload.items() if k!="request_id"})
if __name__=="__main__":
    unittest.main()
