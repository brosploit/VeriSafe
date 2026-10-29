# VeriSafe Frontend

Responsive React + TypeScript + Tailwind CSS frontend for [VeriSafe](https://github.com/brosploit/VeriSafe), developed against `docs/API_SPEC.md`.

## Requirements

- Node.js 20+ and npm
- Backend Python/FastAPI service (optional for viewing the UI; required for actual analyses)

## Local development

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173`. Start the FastAPI backend at `http://localhost:8000` to connect `/api/health`. Vite proxies `/api/*` to port 8000.

## Backend integration

The frontend sends:

- `GET /api/health`
- `POST /api/messages/analyze` with `{message_text, sender?, channel}`
- `POST /api/urls/analyze` with `{url, context?}`

The corresponding analysis responses follow `docs/API_SPEC.md` and include risk classification, score, summary, indicators, and recommendations. The backend provides full implementations for `/api/health`, `/api/messages/analyze`, and `/api/urls/analyze`.

Configure deployed API origin in `.env` (do **not** commit secrets):

```bash
VITE_API_BASE_URL=https://your-fastapi-host.example
```

The backend must enable CORS for the deployed frontend origin. Avoid wildcard CORS + credentials in production. HTTPS should be used in deployment. Vercel: project root `frontend`, build command `npm run build`, output directory `dist`.

## Build / checks

```bash
npm run typecheck
npm run build
```

## Security considerations

- Submitted messages and URLs are sent to the configured backend, so users should remove sensitive content first.
- No demo verdicts or client-side fake detection are presented.
- URLs submitted for analysis are never auto-opened in a browser.
- Inputs are validated client-side, but the backend must independently validate and sanitize all inputs.
- No secrets should be stored in `VITE_*` variables; they are visible in the browser.
- This frontend does not persist submitted content in browser storage.

## Features

Responsive landing/dashboard; message/URL analysis forms; sample input; backend health check; loading and error handling; severity-level indicators; confidence and assessment summary; recommendations; report clipboard export; accessibility and responsive layouts.
