# Shakti360 Guardian

Privacy-first, battery-aware, installable personal-safety PWA for DoraHacks 2.0.

## Core winning features
- Installable responsive PWA plus iOS and Android from one Expo codebase
- Journey Guardian with event-driven safety sessions
- Trusted Circle + escalation policy
- Nearby hospitals / police / pharmacies on map
- Battery Guardian with low-power modes
- Cyber Guardian for suspicious message analysis
- Evidence Vault + incident timeline
- Privacy Guardian
- Offline/degraded-mode friendly architecture
- Multilingual-ready UI
- FastAPI backend with deterministic safety engine

> Important: Shakti360 does not claim to predict crime or guarantee safety.
> AI assists with interpretation and organization; critical escalation logic stays deterministic.

## Quick start

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

To enable real Guardian Circle delivery locally, copy `backend/.env.example` to `backend/.env`, add your Twilio and Resend secrets, then load it when starting the API:

```powershell
cd backend
Copy-Item .env.example .env
# Edit .env without committing it
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000 --env-file .env
```

Use Python 3.12. The repository `.python-version`, backend container, and CI all target 3.12 so `pydantic-core` installs from a Windows wheel rather than compiling locally.

### App
```bash
cd app
npm install
npx expo start
```

Set:
```bash
EXPO_PUBLIC_API_URL=http://localhost:8000
```

For a real phone on the same Wi‑Fi, replace localhost with your laptop LAN IP.

### Production web/PWA

Requires Node 22. The export creates statically rendered HTML routes, the web manifest, offline fallback, and a Workbox-generated service worker:

```bash
cd app
npm ci
EXPO_PUBLIC_API_URL=https://api.example.com npm run build:web
```

Deploy the `app/dist/` directory to any static HTTPS host. HTTPS is required for service workers and browser geolocation outside localhost. Do not cache API responses at the CDN.

The service worker caches versioned application-shell assets only. It does not cache private API responses or Overpass requests. Offline mode cannot confirm guardian delivery, live resources, or server synchronization.

### Docker

```bash
docker compose up --build
```

- PWA: `http://localhost:8080`
- API: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`

Production environment variables:

- `EXPO_PUBLIC_API_URL`: public HTTPS API origin embedded during the web build
- `CORS_ORIGINS`: comma-separated allowed web origins
- `DATABASE_URL`: SQLAlchemy URL; SQLite is the local fallback and Compose uses PostgreSQL
- `JWT_SECRET`: strong random signing secret; required before public deployment
- `OVERPASS_ENDPOINT`: planned configurable nearby-resource endpoint; current provider uses the documented public endpoint
- `GUARDIAN_INVITE_BASE_URL`: public PWA invitation URL, for example `https://app.example.com/guardian-invite`
- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, and either `TWILIO_FROM_NUMBER` or `TWILIO_MESSAGING_SERVICE_SID`: real Guardian Circle SMS delivery
- `RESEND_API_KEY` and `RESEND_FROM_EMAIL`: real Guardian Circle email delivery; the sender domain must be verified

Guardian delivery credentials belong only in `backend/.env` or the deployment secret store. Never prefix them with `EXPO_PUBLIC_` or commit them. Twilio trial accounts can text only verified recipients. The UI reports `queued` only after the provider accepts a request; it never claims recipient delivery or opening.

Notification API endpoints:

- `GET /notifications/status` — authenticated, secret-safe provider readiness
- `POST /guardians/{guardian_id}/send-invite` — deliver the expiring invite by selected channels
- `POST /guardians/notify` — permission-aware `journey_started`, `missed_checkin`, `journey_completed`, `sos`, or `sos_cancelled` fan-out
- `POST /sos` — starts the SOS session and sends real alerts to the signed-in user's opted-in guardians

All notification mutation endpoints require the authenticated cookie session and `X-CSRF-Token`. Provider IDs and accepted/failed statuses are returned per channel for operational diagnosis.

### Verification

```bash
cd app
npm run typecheck
npx expo-doctor
npm run build:web

cd ../backend
python -m pytest -q
```

CI runs Python 3.12 backend tests on Windows/Linux and performs the frontend typecheck, Expo Doctor, static export, and PWA artifact checks.

## Demo flow
1. Install Shakti360 from the browser or open the responsive PWA.
2. Add a Guardian and share the expiring invitation.
3. Start a safety journey and show adaptive Battery Guardian output.
4. Trigger a demo missed check-in and show the deterministic policy result.
5. End the journey and open its truthful Privacy Receipt.
6. Open nearby live OpenStreetMap resources.
7. Demonstrate Scam Shield, Evidence Vault, and Judge Mode.

## Pro additions
This upgraded package adds SafeWord, Context Fusion, Safety Readiness, Pattern Intelligence, Impact Analytics, deterministic policy tests, trusted-circle demo delivery, multilingual string scaffolding, Docker files, and expanded judge/pitch documentation.

### New API endpoints
- `GET /agents`
- `POST /agents/context`
- `POST /readiness`
- `POST /journeys/safeword`
- `GET /incidents/patterns`
- `POST /feedback`
- `GET /analytics/impact`
- `POST /resources/nearby-v2`
