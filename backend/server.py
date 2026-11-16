"""Small local JSON API; use a reverse proxy and authentication before any deployment."""
import json
import os
import hmac
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
from dircsaf import connect, add_object, observe, list_cases, review_case, risk_baseline, audit_events
from intelligence import image_signature, match_images, train_risk_model, predict_risk, rank_preservation_actions
from stewardship import initialize, add_evidence, save_assessment, create_action, transition_action, dashboard, list_objects, list_actions

DB_PATH = os.environ.get("DIRCSAF_DB", "dircsaf.db")

class Handler(BaseHTTPRequestHandler):
    def respond(self, code, data):
        # JSON responses are never cached by shared proxies.
        body = json.dumps(data).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def dispatch(self, method):
        path = urlparse(self.path).path
        token = os.environ.get("DIRCSAF_DEV_TOKEN")
        if not token or len(token)<24:
            return self.respond(503, {"error":"DIRCSAF_DEV_TOKEN must be configured with at least 24 characters"})
        if not hmac.compare_digest(self.headers.get("Authorization",""),"Bearer "+token):
            return self.respond(401, {"error":"authentication required"})
        payload = {}
        if method == "POST":
            length = int(self.headers.get("Content-Length", "0"))
            if length > 1000000:
                return self.respond(413, {"error":"payload too large"})
            payload = json.loads(self.rfile.read(length) or b"{}")
            if not isinstance(payload, dict):
                return self.respond(400, {"error":"JSON object required"})
        if method == "POST" and path == "/vision/signature":
            return self.respond(200, {"signature":image_signature(payload["pixels"],payload["width"],payload["height"])})
        if method == "POST" and path == "/vision/match":
            return self.respond(200, match_images(payload["query_signature"],payload["references"],payload.get("limit",5)))
        if method == "POST" and path == "/models/risk/train":
            return self.respond(200, train_risk_model(payload["examples"]))
        if method == "POST" and path == "/models/risk/predict":
            return self.respond(200, predict_risk(payload["model"],payload["features"]))
        if method == "POST" and path == "/preservation/plan":
            return self.respond(200, rank_preservation_actions(payload["items"],payload["capacity"]))
        with connect(DB_PATH) as db:
            initialize(db)
            if method == "GET" and path == "/dashboard":
                return self.respond(200, dashboard(db))
            if method == "GET" and path == "/objects":
                return self.respond(200, list_objects(db))
            if method == "GET" and path == "/actions":
                return self.respond(200, list_actions(db))
            if method == "POST" and path == "/evidence":
                return self.respond(201, add_evidence(db,payload["object_id"],payload["kind"],payload["reference"],payload["actor"],payload.get("sha256")))
            if method == "POST" and path == "/assessments":
                return self.respond(201, save_assessment(db,payload["object_id"],payload["method"],payload["model_version"],payload["inputs"],payload["result"]))
            if method == "POST" and path == "/actions":
                return self.respond(201, create_action(db,payload["object_id"],payload["title"],payload["rationale"],payload["priority"]))
            if method == "POST" and path.startswith("/actions/") and path.endswith("/transition"):
                return self.respond(200, transition_action(db,path.split("/")[2],payload["actor"],payload["status"],payload.get("evidence_ref")))
            if method == "GET" and path == "/health":
                return self.respond(200, {"status":"ok","service":"dir-csaf"})
            if method == "POST" and path == "/objects":
                return self.respond(201, add_object(db, payload))
            if method == "POST" and path == "/observations":
                return self.respond(201, observe(db, payload["object_id"], payload["observed_location"], payload["observer"], payload["evidence_ref"]))
            if method == "GET" and path == "/cases":
                return self.respond(200, list_cases(db))
            if method == "POST" and path.startswith("/cases/") and path.endswith("/review"):
                case_id = path.split("/")[2]
                return self.respond(200, review_case(db, case_id, payload["reviewer"], payload["decision"], payload["evidence_ref"]))
            if method == "GET" and path.startswith("/risk/"):
                return self.respond(200, risk_baseline(db, path.split("/")[2]))
            if method == "GET" and path == "/audit":
                return self.respond(200, audit_events(db))
        return self.respond(404, {"error":"route not found"})

    def do_GET(self):
        if urlparse(self.path).path == "/":
            file = Path(__file__).resolve().parent.parent / "web" / "index.html"
            if file.exists():
                body=file.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type","text/html; charset=utf-8")
                self.send_header("Content-Security-Policy","default-src 'self'; script-src 'unsafe-inline' 'self'; style-src 'unsafe-inline' 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'")
                self.send_header("Content-Length",str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
        self.safe_dispatch("GET")

    def do_GET_old(self):
        self.safe_dispatch("GET")

    def do_POST(self):
        self.safe_dispatch("POST")

    def safe_dispatch(self, method):
        try:
            self.dispatch(method)
        except (KeyError, ValueError, json.JSONDecodeError) as e:
            self.respond(400, {"error":str(e)})
        except LookupError as e:
            self.respond(404, {"error":str(e)})
        except Exception as e:
            if isinstance(e, __import__("sqlite3").IntegrityError):
                self.respond(409, {"error":"record already exists or violates data integrity"})
            else:
                self.respond(500, {"error":"internal error"})

if __name__ == "__main__":
    if len(os.environ.get("DIRCSAF_DEV_TOKEN","")) < 24:
        raise SystemExit("Set DIRCSAF_DEV_TOKEN to a random string of at least 24 characters")
    print("DIR-CSAF local development API: http://127.0.0.1:8765")
    ThreadingHTTPServer(("127.0.0.1", 8765), Handler).serve_forever()
