import unittest
from intelligence import image_signature, match_images, train_risk_model, predict_risk, rank_preservation_actions, FEATURES

class IntelligenceTests(unittest.TestCase):
    def test_image_matching_ranks_exact_signature_first(self):
        image=[0 if x<4 else 255 for y in range(8) for x in range(8)]
        sig=image_signature(image,8,8)
        self.assertEqual(len(sig),64)
        found=match_images(sig,{"different":"1"*64,"same":sig})
        self.assertEqual(found[0]["object_id"],"same")
        self.assertEqual(found[0]["status"],"candidate_only_unverified")
    def test_invalid_image_rejected(self):
        with self.assertRaises(ValueError):
            image_signature([0]*63,8,8)
    def test_fitted_model_and_explanations(self):
        rows=[]
        for n in range(20):
            x=n/19
            rows.append({"features":dict(zip(FEATURES,[x,x,x,x])),
                         "label":int(n>=10)})
        model=train_risk_model(rows)
        low=predict_risk(model,dict.fromkeys(FEATURES,0.0))
        high=predict_risk(model,dict.fromkeys(FEATURES,1.0))
        self.assertGreater(high["score"],low["score"])
        self.assertEqual(high["decision"],"human_review_required")
        self.assertEqual(model["validation_status"],"not_validated")
        self.assertEqual(model,train_risk_model(rows))
    def test_training_requires_two_classes(self):
        rows=[{"features":dict.fromkeys(FEATURES,0.0),"label":0} for _ in range(4)]
        with self.assertRaises(ValueError):
            train_risk_model(rows)
    def test_planning_respects_capacity(self):
        plan=rank_preservation_actions([{"object_id":"A","score":0.2},{"object_id":"B","score":0.9}],1)
        self.assertEqual(plan["recommended"][0]["object_id"],"B")
        self.assertEqual(len(plan["deferred"]),1)
        self.assertEqual(plan["status"],"advisory_only")
if __name__=="__main__":
    unittest.main()
