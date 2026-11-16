"""Idempotent field-observation ingestion.

Each client-generated key is bound to the canonical request payload. A retry with
the same key returns the same response; reuse with different content is rejected.
"""
import hashlib
import json
import sqlite3
from dircsaf import observe

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
        response=observe(db,**data)
        db.execute("INSERT INTO sync_receipts VALUES(?,?,?,?)",
                   (client_id,request_id,digest,json.dumps(response,sort_keys=True)))
        db.commit()
        return response
    except Exception:
        db.rollback()
        raise
