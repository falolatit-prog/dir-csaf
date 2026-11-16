"""Small local JSON API; use a reverse proxy and authentication before any deployment."""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
from dircsaf import connect, add_object, observe, list_cases, review_case, risk_baseline, audit_events

DB_PATH = os.environ.get("DIRCSAF_DB", "dircsaf.db")

class Handler(BaseHTTPRequestHandler):
    def respond(self, code, data):
        body = json.dumps(data).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def dispatch(self, method):
        path = urlparse(self.path).path
        payload = {}
        if method == "POST":
            length = int(self.headers.get("Content-Length", "0"))
            if length > 1000000:
                return self.respond(413, {"error":"payload too large"})
            payload = json.loads(self.rfile.read(length) or b"{}")
            if not isinstance(payload, dict):
                return self.respond(400, {"error":"JSON object required"})
        with connect(DB_PATH) as db:
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
    print("DIR-CSAF local development API: http://127.0.0.1:8765")
    ThreadingHTTPServer(("127.0.0.1", 8765), Handler).serve_forever()
