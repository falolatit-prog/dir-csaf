"""Idempotent field-observation ingestion.

Each client-generated key is bound to the canonical request payload. A retry with
the same key returns the same response; reuse with different content is rejected.
"""
import hashlib
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from dircsaf import get_object, audit

def initialize(db):
    db.execute("""CREATE TABLE IF NOT EXISTS sync_receipts (
      client_id TEXT NOT NULL, request_id TEXT NOT NULL,
      payload_hash TEXT NOT NULL, response_json TEXT NOT NULL,
      PRIMARY KEY(client_id,request_id))""")

def submit_observation(db, payload):
    initialize(db)
    client_id=payload.get("client_id")
    request_id=payload.get("request_id")
    if not all(isinstance(x,str) and 1<=len(x)<=128 and x.strip() for x in (client_id,request_id)):
        raise ValueError("client_id and request_id are required")
    fields=("object_id","observed_location","observer","evidence_ref")
    data={k:payload[k] for k in fields}
    digest=hashlib.sha256(json.dumps(data,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    row=db.execute("SELECT payload_hash,response_json FROM sync_receipts WHERE client_id=? AND request_id=?",
                   (client_id,request_id)).fetchone()
    if row:
        if row["payload_hash"]!=digest:
            raise ValueError("idempotency key reused with different observation")
        return json.loads(row["response_json"])
    # BEGIN IMMEDIATE ensures a competing writer cannot insert the same key between
    # the lookup and observation insert. Roll back the observation if receipt fails.
    db.execute("BEGIN IMMEDIATE")
    try:
        row=db.execute("SELECT payload_hash,response_json FROM sync_receipts WHERE client_id=? AND request_id=?",
                       (client_id,request_id)).fetchone()
        if row:
            if row["payload_hash"]!=digest: raise ValueError("idempotency key reused with different observation")
            db.commit()
            return json.loads(row["response_json"])
        obj=get_object(db,data["object_id"])
        if obj is None: raise LookupError("object not found")
        if any(not isinstance(v,str) or not v.strip() for v in data.values()):
            raise ValueError("observation fields must be nonempty strings")
        oid=str(uuid.uuid4())
        mismatch=data["observed_location"].strip().casefold()!=obj["expected_location"].strip().casefold()
        case_id=str(uuid.uuid4()) if mismatch else None
        timestamp=datetime.now(timezone.utc).isoformat()
        db.execute("INSERT INTO observations VALUES(?,?,?,?,?,?)",
                   (oid,data["object_id"],data["observed_location"],data["observer"],data["evidence_ref"],timestamp))
        audit(db,"physical_observation",oid,data["observer"],
              {"object_id":data["object_id"],"evidence_ref":data["evidence_ref"]})
        if mismatch:
            db.execute("INSERT INTO cases(id,object_id,observation_id,status,reason,created_at) VALUES(?,?,?,?,?,?)",
                       (case_id,data["object_id"],oid,"needs_evidence","location_discrepancy",timestamp))
            audit(db,"case_opened",case_id,data["observer"],
                  {"observation_id":oid,"expected":obj["expected_location"],"observed":data["observed_location"]})
        response={"observation_id":oid,"discrepancy":mismatch,"case_id":case_id,
                  "verification_status":"discrepant" if mismatch else "observation_consistent_unverified"}
        db.execute("INSERT INTO sync_receipts VALUES(?,?,?,?)",
                   (client_id,request_id,digest,json.dumps(response,sort_keys=True)))
        db.commit()
        return response
    except Exception:
        db.rollback()
        raise
