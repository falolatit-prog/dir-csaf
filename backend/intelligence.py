"""Reproducible image matching and learned risk ranking experiments.

This module contains actual fitted-model logic, but no claims of real-world accuracy.
Only synthetic examples are included in the repository.
"""
import math
import hashlib
import json

def image_signature(pixels, width, height):
    """8x8 average-hash from grayscale pixel values; input is row-major, 0..255.
    This is an image-feature baseline, not a trained vision model.
    """
    if not isinstance(width, int) or not isinstance(height, int) or width < 8 or height < 8:
        raise ValueError("image dimensions must be at least 8x8")
    if len(pixels) != width * height or any(not isinstance(v, (int,float)) or not 0 <= v <= 255 for v in pixels):
        raise ValueError("pixels must be width*height grayscale values between 0 and 255")
    cells = []
    for row in range(8):
        for col in range(8):
            x0, x1 = col*width//8, (col+1)*width//8
            y0, y1 = row*height//8, (row+1)*height//8
            vals = [pixels[y*width+x] for y in range(y0,y1) for x in range(x0,x1)]
            cells.append(sum(vals)/len(vals))
    avg = sum(cells)/64
    return "".join("1" if v > avg else "0" for v in cells)

def match_images(query_signature, references, limit=5):
    if len(query_signature) != 64 or set(query_signature) - {"0","1"}:
        raise ValueError("invalid query signature")
    if not isinstance(limit,int) or limit < 1:
        raise ValueError("limit must be positive")
    results = []
    for object_id, signature in references.items():
        if len(signature) != 64 or set(signature) - {"0","1"}:
            raise ValueError("invalid reference signature")
        distance = sum(a!=b for a,b in zip(query_signature,signature))
        results.append({"object_id":object_id,"hamming_distance":distance,
                        "similarity":round(1-distance/64,4),
                        "status":"candidate_only_unverified"})
    return sorted(results,key=lambda x:(x["hamming_distance"],x["object_id"]))[:limit]

FEATURES = ("condition_severity", "environment_exposure", "documentation_gap", "unresolved_discrepancy")

def validate_features(row):
    if set(row) != set(FEATURES):
        raise ValueError("feature names must match the documented schema")
    values = [row[k] for k in FEATURES]
    if any(not isinstance(x,(int,float)) or isinstance(x,bool) or not math.isfinite(x) or x<0 or x>1 for x in values):
        raise ValueError("features must be finite numbers in [0,1]")
    return values

def sigmoid(z):
    if z >= 0:
        return 1/(1+math.exp(-z))
    e=math.exp(z)
    return e/(1+e)

def train_risk_model(examples, epochs=400, rate=0.2):
    """Fit regularized logistic regression to labeled binary risk outcomes.
    For development tests only; requires independently sourced labels for real use.
    """
    if not isinstance(examples,list) or len(examples)<4:
        raise ValueError("at least four labeled examples required")
    if not isinstance(epochs,int) or epochs<1 or epochs>10000 or not 0<rate<=1:
        raise ValueError("invalid training hyperparameters")
    xs=[]; ys=[]
    for row in examples:
        x=validate_features(row["features"])
        y=row["label"]
        if type(y) is not int or y not in (0,1):
            raise ValueError("labels must be binary 0/1")
        xs.append(x);ys.append(y)
    if len(set(ys))!=2:
        raise ValueError("training data must contain both classes")
    weights=[0.0]*4; bias=0.0
    for _ in range(epochs):
        dw=[0.0]*4; db=0.0
        for x,y in zip(xs,ys):
            err=sigmoid(sum(w*v for w,v in zip(weights,x))+bias)-y
            for j in range(4):dw[j]+=err*x[j]
            db+=err
        n=len(xs)
        weights=[w-rate*(dw[j]/n+0.001*w) for j,w in enumerate(weights)]
        bias-=rate*db/n
    return {"model_type":"trained_logistic_risk_v1","feature_order":list(FEATURES),
            "weights":weights,"bias":bias,"training_count":len(xs),
            "training_fingerprint":hashlib.sha256(json.dumps(examples,sort_keys=True).encode()).hexdigest(),
            "validation_status":"not_validated"}

def predict_risk(model, features):
    x=validate_features(features)
    if model.get("model_type")!="trained_logistic_risk_v1" or model.get("feature_order")!=list(FEATURES):
        raise ValueError("unsupported model")
    weights=model["weights"]
    if len(weights)!=4 or any(not isinstance(w,(int,float)) or not math.isfinite(w) for w in weights):
        raise ValueError("invalid weights")
    p=sigmoid(sum(w*v for w,v in zip(weights,x))+model["bias"])
    return {"score":round(p,6),"model_type":model["model_type"],
            "validation_status":model["validation_status"],
            "feature_contributions":dict(zip(FEATURES,[round(w*v,6) for w,v in zip(weights,x)])),
            "decision":"human_review_required","limitations":"Model score is not a validated probability of deterioration"}

def rank_preservation_actions(items, capacity):
    """Deterministic constrained planning baseline: order by score, never auto-execute."""
    if not isinstance(capacity,int) or capacity<0:
        raise ValueError("capacity must be nonnegative")
    if any(not isinstance(i.get("score"),(int,float)) or not math.isfinite(i["score"]) or
           not isinstance(i.get("object_id"),str) for i in items):
        raise ValueError("invalid action candidates")
    ranked=sorted(items,key=lambda i:(-i["score"],i["object_id"]))
    return {"recommended":ranked[:capacity],"deferred":ranked[capacity:],
            "status":"advisory_only","method":"score_sorted_capacity_baseline"}
