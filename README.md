# Shakti360 Guardian

> Personal safety without permanent surveillance.

Shakti360 is an installable, privacy-first safety platform that helps a person prepare for a journey, stay connected to people they trust, find nearby support, recognize suspicious messages, and document incidents. It combines an Expo web/PWA experience with a FastAPI safety engine in one Railway deployment.

**Live app:** [shakti360-guardian-production.up.railway.app](https://shakti360-guardian-production.up.railway.app)

## Why it can win

Most safety products ask for continuous access and promise certainty they cannot provide. Shakti360 takes the opposite approach:

- **Purpose-bound protection:** journey and location-sharing sessions end when their purpose ends.
- **Human-controlled escalation:** deterministic rules surface options; the system never claims to contact emergency services automatically.
- **Trusted Guardian Circle:** users choose who receives journey, missed check-in, SOS, and temporary-location updates.
- **Real delivery adapters:** Twilio SMS and Resend email return truthful queued, failed, or unconfigured states.
- **Battery-aware operation:** the Battery Guardian adapts sampling policy instead of assuming unlimited GPS use.
- **Resilient PWA:** installable across desktop, Android, iPhone, and iPad with an offline shell and fresh network-first pages.
- **Explainable assistance:** cyber, context, privacy, readiness, evidence, and pattern tools show their reasoning without pretending to predict crime.

## Judge-ready demo

1. Register or sign in and land on the authenticated dashboard.
2. Add a trusted guardian, then copy or share the 24-hour invitation.
3. Start a timed journey and show the battery policy decision.
4. Trigger a missed check-in or SafeWord and inspect deterministic escalation.
5. End the journey and open its locally stored privacy receipt.
6. Find nearby hospitals, clinics, pharmacies, and police using live OpenStreetMap data with a bounded fallback.
7. Demonstrate the Scam Scanner, Evidence Vault, Safety Readiness, and Impact dashboard.
8. Install the PWA from the browser and reopen it in standalone mode.

## System design

```text
Browser / installed PWA
        │ same-origin HTTPS
        ▼
Railway container :$PORT
        │
        ├── Nginx ─────────────► Expo static web application
        │
        └── /api/* ────────────► FastAPI on 127.0.0.1:8000
                                      │
                                      ├── PostgreSQL or SQLite fallback
                                      ├── Twilio SMS
                                      ├── Resend email
                                      └── OpenStreetMap / Overpass
```

The browser never calls `localhost`, crosses origins, or depends on Railway private DNS. Nginx strips the public `/api` prefix and forwards requests to FastAPI within the same container.

## Working product surface

### Protection

- Timed safety journeys, check-ins, explicit SOS, cancellation, and SafeWord
- Battery policy and deterministic escalation engine
- Guardian permissions and expiring invitation links
- Temporary-session language and privacy receipts

### Assistance

- Live nearby-support lookup with a fast, labeled fallback
- Suspicious-message analysis
- Context fusion, privacy review, and safety-readiness assessment
- Incident documentation, evidence summaries, and pattern insights

### Trust and operations

- Argon2 password hashing
- Short-lived access tokens and revocable server-side refresh sessions
- HttpOnly secure cookies and CSRF protection
- PostgreSQL URL normalization with safe startup fallback
- Request IDs, no-store API responses, bounded upstream timeouts, and explicit provider status
- PWA cache upgrades that do not strand users on old route bundles

## Verified status

The repository includes automated unit, policy, API, authentication, database, and notification-contract tests plus a reusable production smoke test.

```text
66 local backend tests passing
35 application routes registered
36 live Railway operations passing
Frontend TypeScript passing
Production Expo/PWA export passing
```

Run the live smoke test:

```powershell
cd backend
.\.venv\Scripts\python.exe scripts\smoke_api.py https://shakti360-guardian-production.up.railway.app/api
```

The smoke test creates disposable records but deliberately uses no phone number or email address, so it never sends a real notification.

## Local development

Requirements: Python 3.12 and Node.js 22.

### FastAPI

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

API documentation: `http://127.0.0.1:8000/docs`

### Expo app

```powershell
cd app
npm ci
$env:EXPO_PUBLIC_API_URL="http://127.0.0.1:8000"
npx expo start
```

For a physical phone on the same Wi-Fi network, replace `127.0.0.1` with the computer's LAN address.

### Verification

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest -q

cd ..\app
npm run typecheck
npm run build:web
```

## Deploy on Railway

Shakti360 uses one Railway service and one container. No separate frontend service is required.

### 1. Connect the repository

Create a Railway service from this GitHub repository and select the `main` branch.

Configure the service:

```text
Root Directory: /
Config File Path: /railway.json
Build Command: empty
Start Command: empty (repository config supplies it)
```

Railway reads the root [`Dockerfile`](./Dockerfile) and [`railway.json`](./railway.json). The container builds the Expo PWA, installs the Python backend, starts FastAPI privately, and exposes Nginx on Railway's dynamic `$PORT`.

Do not configure `npx`, `expo start`, or `npm start` as the production start command. Node is used only in the build stage.

### 2. Configure required variables

```env
APP_ENV=production
JWT_SECRET=<a-long-cryptographically-random-secret>
GUARDIAN_INVITE_BASE_URL=https://shakti360-guardian-production.up.railway.app/guardian-invite
```

Generate the signing secret locally:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Never expose `JWT_SECRET` through an `EXPO_PUBLIC_` variable or commit it.

### 3. Add persistent PostgreSQL

Add a Railway PostgreSQL service, then use Railway's **Add Reference** control to provide its `DATABASE_URL` to the Shakti360 service. Do not paste an unresolved `${{Postgres.DATABASE_URL}}` expression if the database service has another name.

The API can start with its SQLite fallback for a demo, but SQLite inside an ephemeral container is not restart-proof. PostgreSQL is required for durable production accounts and sessions.

### 4. Enable real notifications

Twilio SMS:

```env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxx
TWILIO_FROM_NUMBER=+15551234567
```

Alternatively, replace `TWILIO_FROM_NUMBER` with:

```env
TWILIO_MESSAGING_SERVICE_SID=MGxxxxxxxxxxxxxxxx
```

Resend email:

```env
RESEND_API_KEY=re_xxxxxxxxxxxxxxxx
RESEND_FROM_EMAIL=Shakti360 Guardian <alerts@your-verified-domain.com>
```

Twilio trial accounts can send only to verified recipients. Resend requires an authorized sender. Shakti360 always retains a copy/share invitation fallback when provider delivery fails.

### 5. Optional signed native releases

The PWA is immediately installable without an app store. Only configure these when signed release artifacts genuinely exist:

```env
EXPO_PUBLIC_ANDROID_DOWNLOAD_URL=https://downloads.example.com/shakti360.apk
EXPO_PUBLIC_IOS_DOWNLOAD_URL=https://apps.apple.com/app/example
```

Android APK and iOS release buttons stay hidden until their corresponding URL is configured.

### 6. Deploy and verify

Deploy the latest commit without a custom start-command override. The build must contain both stages:

```text
FROM node:22-alpine AS web-build
FROM python:3.12-slim
```

Verify:

```text
https://shakti360-guardian-production.up.railway.app/
https://shakti360-guardian-production.up.railway.app/api/health
https://shakti360-guardian-production.up.railway.app/api/ready
https://shakti360-guardian-production.up.railway.app/api/docs
```

Expected health response:

```json
{"status":"ok","service":"shakti360-api"}
```

## API map

| Capability | Endpoints |
|---|---|
| Authentication | `/auth/register`, `/auth/login`, `/auth/me`, `/auth/refresh`, `/auth/logout` |
| Journeys | `/journeys`, `/journeys/{id}`, `/journeys/checkin`, `/journeys/safeword`, `/journeys/{id}/sos` |
| Guardian Circle | `/guardians`, `/guardian-invites/{token}`, `/guardians/{id}/send-invite`, `/guardians/notify` |
| SOS | `/sos`, `/sos/{id}/cancel` |
| Nearby support | `/resources/nearby`, `/resources/nearby-v2` |
| Safety agents | `/agents/cyber`, `/agents/privacy`, `/agents/context`, `/readiness`, `/battery/policy` |
| Evidence and impact | `/incidents`, `/incidents/patterns`, `/feedback`, `/analytics/impact` |
| Operations | `/health`, `/ready`, `/notifications/status`, `/docs` |

In production, prefix every API path with `/api`, for example `/api/auth/login`.

## Safety boundaries

Shakti360 does not guarantee safety, predict crime, replace emergency services, or claim that a queued provider request reached a person. Nearby community data can be incomplete. Users retain control over escalation and should verify critical information through independent channels.

AI assists with interpretation and organization. High-impact escalation remains deterministic and human-controlled.
