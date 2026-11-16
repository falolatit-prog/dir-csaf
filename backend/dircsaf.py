"""DIR-CSAF inventory, risk and accountable review core. Python standard library only."""
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

def now():
    return datetime.now(timezone.utc).isoformat()

def connect(path="dircsaf.db"):
    db = sqlite3.connect(str(path))
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    db.executescript("""
    CREATE TABLE IF NOT EXISTS objects (
      id TEXT PRIMARY KEY, title TEXT NOT NULL, expected_location TEXT NOT NULL,
      material TEXT, condition TEXT NOT NULL DEFAULT 'unknown',
      source TEXT NOT NULL, created_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS observations (
      id TEXT PRIMARY KEY, object_id TEXT NOT NULL REFERENCES objects(id),
      observed_location TEXT NOT NULL, observer TEXT NOT NULL,
      evidence_ref TEXT NOT NULL, observed_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS cases (
      id TEXT PRIMARY KEY, object_id TEXT NOT NULL REFERENCES objects(id),
      observation_id TEXT NOT NULL UNIQUE REFERENCES observations(id),
      status TEXT NOT NULL, reason TEXT NOT NULL, reviewer TEXT,
      resolution_evidence TEXT, created_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS audit (
      id INTEGER PRIMARY KEY AUTOINCREMENT, event_type TEXT NOT NULL,
      entity_id TEXT NOT NULL, actor TEXT NOT NULL, details TEXT NOT NULL,
      created_at TEXT NOT NULL);
    """)
    return db

def audit(db, event, entity, actor, details):
    db.execute("INSERT INTO audit(event_type,entity_id,actor,details,created_at) VALUES(?,?,?,?,?)",
               (event, entity, actor, json.dumps(details, sort_keys=True), now()))

def add_object(db, item):
    required = ("id", "title", "expected_location", "source")
    if any(not isinstance(item.get(k), str) or not item[k].strip() for k in required):
        raise ValueError("id, title, expected_location and source are required strings")
    with db:
        db.execute("INSERT INTO objects VALUES(?,?,?,?,?,?,?)",
                   (item["id"], item["title"], item["expected_location"],
                    item.get("material"), item.get("condition", "unknown"), item["source"], now()))
        audit(db, "object_created", item["id"], "import", {"source":item["source"]})
    return get_object(db, item["id"])

def get_object(db, oid):
    row = db.execute("SELECT * FROM objects WHERE id=?", (oid,)).fetchone()
    return dict(row) if row else None

def observe(db, object_id, location, observer, evidence_ref):
    if not all(isinstance(x, str) and x.strip() for x in (location, observer, evidence_ref)):
        raise ValueError("location, observer and evidence_ref required")
    obj = get_object(db, object_id)
    if obj is None:
        raise LookupError("object not found")
    oid = str(uuid.uuid4())
    mismatch = location.strip().casefold() != obj["expected_location"].strip().casefold()
    case_id = str(uuid.uuid4()) if mismatch else None
    with db:
        db.execute("INSERT INTO observations VALUES(?,?,?,?,?,?)",
                   (oid, object_id, location, observer, evidence_ref, now()))
        audit(db, "physical_observation", oid, observer, {"object_id":object_id,"evidence_ref":evidence_ref})
        if mismatch:
            db.execute("INSERT INTO cases(id,object_id,observation_id,status,reason,created_at) VALUES(?,?,?,?,?,?)",
                       (case_id, object_id, oid, "needs_evidence", "location_discrepancy", now()))
            audit(db, "case_opened", case_id, observer, {"observation_id":oid,"expected":obj["expected_location"],"observed":location})
    return {"observation_id":oid,"discrepancy":mismatch,"case_id":case_id,
            "verification_status":"discrepant" if mismatch else "observation_consistent_unverified"}

def list_cases(db):
    return [dict(r) for r in db.execute("SELECT * FROM cases ORDER BY created_at,id")]

def review_case(db, case_id, reviewer, decision, evidence_ref):
    if decision not in ("approved", "rejected"):
        raise ValueError("decision must be approved or rejected")
    if not reviewer or not str(reviewer).strip() or not evidence_ref or not str(evidence_ref).strip():
        raise ValueError("reviewer and independent evidence reference required")
    row = db.execute("SELECT * FROM cases WHERE id=?", (case_id,)).fetchone()
    if not row:
        raise LookupError("case not found")
    if row["status"] != "needs_evidence":
        raise ValueError("case has already been reviewed")
    if decision == "approved" and evidence_ref == db.execute("SELECT evidence_ref FROM observations WHERE id=?", (row["observation_id"],)).fetchone()[0]:
        raise ValueError("approval requires evidence independent of the original observation")
    with db:
        db.execute("UPDATE cases SET status=?,reviewer=?,resolution_evidence=? WHERE id=?",
                   (decision, reviewer, evidence_ref, case_id))
        audit(db, "case_reviewed", case_id, reviewer, {"decision":decision,"evidence_ref":evidence_ref})
    return dict(db.execute("SELECT * FROM cases WHERE id=?", (case_id,)).fetchone())

def risk_baseline(db, object_id):
    """Transparent NON-AI triage baseline; not a deterioration forecast."""
    obj = get_object(db, object_id)
    if obj is None:
        raise LookupError("object not found")
    factors = []
    score = 0
    if obj["condition"].strip().casefold() in ("poor", "critical"):
        score += 2
        factors.append("recorded_condition_poor_or_critical")
    if db.execute("SELECT 1 FROM cases WHERE object_id=? AND status='needs_evidence' LIMIT 1", (object_id,)).fetchone():
        score += 1
        factors.append("unresolved_inventory_discrepancy")
    return {"object_id":object_id,"method":"transparent_rule_baseline_v1",
            "score":score,"category":"high" if score>=2 else "review" if score else "low",
            "factors":factors,"limitations":"Not AI, not a probability, not a deterioration forecast"}

def audit_events(db):
    return [dict(r) for r in db.execute("SELECT * FROM audit ORDER BY id")]
