# DIR-CSAF Vercel console

Responsive stewardship frontend, hosted as a static Vercel site with an optional server-side API proxy. The default view is **demo mode** with fictional records. Demo mode is read-only.

## Deploy on Vercel

1. Import the existing GitHub repository `falolatit-prog/dir-csaf` into Vercel.
2. Set **Root Directory** to `frontend`.
3. Framework preset: **Other**. Build command: `npm run build`. Output directory: `dist`.
4. Deploy. The demo dashboard requires no environment variables and contains no real collection records.

### Connected mode

To connect to a separately hosted Python backend, configure these **server-side** Vercel environment variables:

- `DIRCSAF_DASHBOARD_TOKEN`: long random secret (at least 16 characters) used to authorize the browser dashboard's API requests.
- `DIRCSAF_BACKEND_URL`: externally reachable **HTTPS** origin for the Python API, e.g. `https://api.example.org`. Never use a local address.
- `DIRCSAF_BACKEND_TOKEN`: the backend's `DIRCSAF_DEV_TOKEN` value, used only inside the Vercel function.

The browser prompts for `DIRCSAF_DASHBOARD_TOKEN` and retains it in page memory only. The backend token is never returned to the browser. The dashboard token is a shared development secret, **not institutional user authentication**.

**Important:** A Python backend bound to `127.0.0.1` cannot be accessed from Vercel. A separately hosted HTTPS backend, appropriate authentication, access policies, durable storage, backups, and security review are required for connected mode. Do not expose the current development API to the public internet with real records.

## Local frontend

```bash
cd frontend
npm test
npm run build
```

Serve the `dist/` folder using any local static server to preview demo mode. To test serverless proxy routes, use Vercel's local development tooling with environment variables configured. Do not place secrets in `frontend/public` or any `VITE_*` browser variable.

## Capabilities and limits

- Overview, inventory, discrepancy cases, preservation actions, evidence/audit.
- Read-only fictional demo records, clearly labeled.
- Connected inventory creation, case review, and preservation-action creation.
- Server-side route allowlist, token authorization, request-size and timeout limits.
- No secure institutional identity, role-based permissions, image upload, object-level access controls, or independently validated AI.
- Vercel deployment and live connected mode have not been verified in this repository.
