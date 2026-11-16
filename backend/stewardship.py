"""Persistent stewardship records and evidence tracking."""
import hashlib
import json
import uuid
from datetime import datetime, timezone

def _now():
    return datetime.now(timezone.utc).isoformat()

def initialize(db):
    db.executescript("""
    CREATE TABLE IF NOT EXISTS evidence (
      id TEXT PRIMARY KEY, object_id TEXT NOT NULL REFERENCES objects(id),
      kind TEXT NOT NULL, reference TEXT NOT NULL, sha256 TEXT,
      recorded_by TEXT NOT NULL, created_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS assessments (
      id TEXT PRIMARY KEY, object_id TEXT NOT NULL REFERENCES objects(id),
      method TEXT NOT NULL, model_version TEXT NOT NULL,
      inputs_json TEXT NOT NULL, result_json TEXT NOT NULL,
      validation_status TEXT NOT NULL, created_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS actions (
      id TEXT PRIMARY KEY, object_id TEXT NOT NULL REFERENCES objects(id),
      title TEXT NOT NULL, rationale TEXT NOT NULL, priority TEXT NOT NULL,
      status TEXT NOT NULL, approved_by TEXT, verification_ref TEXT,
      created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
    """)

def add_evidence(db, object_id, kind, reference, actor, sha256=None):
    if kind not in ("photo","document","physical_inspection","environmental_record"):
        raise ValueError("invalid evidence kind")
    if not all(isinstance(v,str) and v.strip() for v in (object_id,reference,actor)):
        raise ValueError("object, reference and actor required")
    if sha256 is not None and (len(sha256)!=64 or any(c not in "0123456789abcdef" for c in sha256)):
        raise ValueError("sha256 must be lowercase hexadecimal")
    eid=str(uuid.uuid4())
    with db:
        db.execute("INSERT INTO evidence VALUES(?,?,?,?,?,?,?)",
                   (eid,object_id,kind,reference,sha256,actor,_now()))
        db.execute("INSERT INTO audit(event_type,entity_id,actor,details,created_at) VALUES(?,?,?,?,?)",
                   ("evidence_recorded",eid,actor,json.dumps({"object_id":object_id,"kind":kind}),_now()))
    return {"id":eid,"object_id":object_id,"kind":kind,"reference":reference,"sha256":sha256,
            "verification_status":"reference_recorded_not_authenticated"}

def save_assessment(db, object_id, method, version, inputs, result):
    if not all(isinstance(v,str) and v.strip() for v in (object_id,method,version)):
        raise ValueError("object, method, and version required")
    if not isinstance(inputs,dict) or not isinstance(result,dict):
        raise ValueError("inputs and result must be objects")
    aid=str(uuid.uuid4())
    with db:
        db.execute("INSERT INTO assessments VALUES(?,?,?,?,?,?,?,?)",
                   (aid,object_id,method,version,json.dumps(inputs,sort_keys=True),
                    json.dumps(result,sort_keys=True),result.get("validation_status","unvalidated"),_now()))
    return {"id":aid,"object_id":object_id,"method":method,"validation_status":result.get("validation_status","unvalidated")}

def create_action(db, object_id, title, rationale, priority):
    if priority not in ("low","medium","high","critical"):
        raise ValueError("invalid priority")
    if not all(isinstance(v,str) and v.strip() for v in (object_id,title,rationale)):
        raise ValueError("object, title and rationale required")
    aid=str(uuid.uuid4()); stamp=_now()
    with db:
        db.execute("INSERT INTO actions VALUES(?,?,?,?,?,?,?,?,?,?)",
                   (aid,object_id,title,rationale,priority,"proposed",None,None,stamp,stamp))
    return {"id":aid,"status":"proposed"}

def transition_action(db, action_id, actor, status, evidence_ref=None):
    if not isinstance(actor,str) or not actor.strip():
        raise ValueError("actor required")
    row=db.execute("SELECT * FROM actions WHERE id=?",(action_id,)).fetchone()
    if row is None: raise LookupError("action not found")
    transitions={"proposed":{"approved","rejected"},"approved":{"in_progress"},
                 "in_progress":{"implemented"},"implemented":{"verified"}}
    if status not in transitions.get(row["status"],set()):
        raise ValueError("invalid action transition")
    if status=="verified" and (not isinstance(evidence_ref,str) or not evidence_ref.strip()):
        raise ValueError("independent verification reference required")
    with db:
        db.execute("UPDATE actions SET status=?, approved_by=CASE WHEN ?='approved' THEN ? ELSE approved_by END, verification_ref=COALESCE(?,verification_ref),updated_at=? WHERE id=?",
                   (status,status,actor,evidence_ref,_now(),action_id))
        db.execute("INSERT INTO audit(event_type,entity_id,actor,details,created_at) VALUES(?,?,?,?,?)",
                   ("action_transition",action_id,actor,json.dumps({"status":status,"evidence_ref":evidence_ref}),_now()))
    return {"id":action_id,"status":status}

def dashboard(db):
    initialize(db)
    counts={}
    for table in ("objects","observations","cases","evidence","assessments","actions"):
        counts[table]=db.execute("SELECT COUNT(*) FROM "+table).fetchone()[0]
    counts["unresolved_cases"]=db.execute("SELECT COUNT(*) FROM cases WHERE status='needs_evidence'").fetchone()[0]
    counts["pending_actions"]=db.execute("SELECT COUNT(*) FROM actions WHERE status NOT IN ('verified','rejected')").fetchone()[0]
    counts["verified_actions"]=db.execute("SELECT COUNT(*) FROM actions WHERE status='verified'").fetchone()[0]
    return {"counts":counts,"warning":"Recorded evidence references and review actions are not independently authenticated"}

def list_objects(db):
    return [dict(row) for row in db.execute("SELECT * FROM objects ORDER BY id")]

def list_actions(db):
    initialize(db)
    return [dict(row) for row in db.execute("SELECT * FROM actions ORDER BY created_at,id")]
