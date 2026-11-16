# DIR-CSAF Field Verification (Expo)

Mobile field-capture application in the same repository as the backend and web console.

## Implemented

- Enter collection object identifier, observed location, observer, and evidence reference.
- Capture a photograph with the device camera.
- Save observations to a local AsyncStorage queue while offline.
- Synchronize observation **metadata** to the backend `POST /observations` route.
- Preserve unsent records on synchronization failure and show discrepancy status in server responses.

## Important limitations

- Photos are **not uploaded**. Their local URIs may become inaccessible if the OS cleans temporary camera files; production media capture must copy images into app-owned persistent storage.
- Synchronization is **not idempotent** on the server. If a request succeeds but its response is lost, retrying can create a duplicate observation. Do not rely on this workflow for authoritative collection records until the backend supports idempotency keys.
- The current backend uses one shared development bearer token, not user authentication or role-based authorization.
- No barcode/QR scanning, automated image matching on-device, production encryption, or institution-specific authorization is implemented.
- This is development software for fictional records, not a production collections system.

## Local setup

Requires a supported Node.js version and Expo development tooling.

```bash
cd mobile
npm install
npm test
npx expo start
```

Start the backend separately with `DIRCSAF_DEV_TOKEN` configured as documented in the repository root README. In the app, enter an API URL reachable **from the phone**. `127.0.0.1` on a physical phone refers to the phone, not your development computer. A local HTTP server and development token are only suitable for an isolated trusted development environment. Use HTTPS and proper authentication before deployment.

## Test status

`npm test` executes the pure offline queue unit tests. UI, camera, device storage, and end-to-end sync must be verified on supported iOS and Android devices.
