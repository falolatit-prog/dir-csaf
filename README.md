# DIR-CSAF

**Evidence | Accountability | Human Review**

DIR-CSAF is an AI-powered collections stewardship and accountability system under active development for museums and archives.

## Implemented first vertical slice

The Python standard-library backend includes:
- SQLite collection object records with source provenance.
- Physical location observations and discrepancy case creation.
- Human review with an independent evidence-reference requirement.
- Append-only application audit events.
- A transparent, **non-AI** preservation triage baseline for later comparison.
- A local JSON HTTP API and unit tests.

**Not implemented yet:** computer vision, predictive AI, image storage, authentication, production authorization, web dashboard, mobile application, and real institutional integration. A reference string is not independently validated evidence; the current human-review gate is a workflow control, not proof that evidence is genuine. Do not deploy this development server to public networks.

## Run tests

```bash
cd backend
python -m unittest -v
```

## Run the local API

```bash
cd backend
python server.py
```

Available routes: `GET /health`, `POST /objects`, `POST /observations`, `GET /cases`, `POST /cases/{id}/review`, `GET /risk/{object_id}`, `GET /audit`.

Example fictional record:

```bash
curl -X POST http://127.0.0.1:8765/objects -H 'Content-Type: application/json' -d '{"id":"OBJ-1","title":"Fictional ceramic vessel","expected_location":"Shelf A","source":"synthetic-demo","condition":"poor"}'
```

See [framework specification](docs/FRAMEWORK_SPECIFICATION_v0.1.md) for the architecture and planned evaluation.

## Browser console and persistent stewardship workflow

The development server serves the stewardship console at `http://127.0.0.1:8765/`.
Set a **locally generated**, random development token before starting the server:

```bash
cd backend
export DIRCSAF_DEV_TOKEN="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
python server.py
```

On Windows PowerShell, set `$env:DIRCSAF_DEV_TOKEN` to a locally generated random token before starting the server. The console prompts for that token and holds it in page memory only. Do not publish or commit tokens.

Additional routes:
- `GET /dashboard`, `GET /objects`, `GET /actions`
- `POST /evidence`, `POST /assessments`, `POST /actions`
- `POST /actions/{id}/transition`

All JSON API routes require `Authorization: Bearer <token>`. This is **single-token development authentication**, not production identity management or role-based authorization. The browser console is not suitable for public hosting. Evidence references are not authenticated; image content storage and mobile capture are not implemented. AI assessments can be stored, but model outputs are not yet connected automatically to object workflows.

Run all unit tests with `cd backend && python -m unittest discover -v`. Tests must pass in CI before a release is considered verified.
