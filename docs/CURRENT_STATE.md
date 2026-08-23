# Shakti360 current-state audit

Updated: 2026-08-21

## Stack and versions

- Frontend: Expo 57, Expo Router 57, React 19.2, React Native 0.86, TypeScript 6
- Web: statically rendered Expo Router PWA, Workbox service worker, Nginx container
- Backend: FastAPI 0.116, Pydantic 2.11, Python 3.12
- Data: in-memory dictionaries/lists; local device state in AsyncStorage
- Maps/resources: browser/device geolocation plus OpenStreetMap Overpass provider with labeled fallback
- CI: Python 3.12 on Windows/Linux; TypeScript, Expo Doctor, PWA export and artifact checks

## What works

- Five-tab responsive application shell and installable PWA
- Timed safety journeys, check-ins, deterministic escalation and SafeWord demo
- Adaptive Battery Policy Engine with explicit inputs, outputs, reason and policy version
- Guardian creation with scoped 24-hour invitation tokens
- User-controlled SOS sessions and cancellation
- Live nearby-resource lookup with real GPS and transparent provenance
- Explainable rule-first scam analysis
- Incident recording, descriptive pattern analysis, readiness and privacy checks
- Locally persisted active journey, Daily Notes and truthful Privacy Receipts
- Offline shell, network indicator, crash boundary and non-sensitive event queue
- Live session impact counters; demo data is labeled
- 25 passing backend tests before the authentication phase

## Mocked or development-only

- Guardians, journeys, incidents, SOS sessions, feedback and analytics are held in backend memory
- Guardian “delivery” is a labeled demo log; no email/SMS provider is connected
- Guardian invitation URL exposes permission metadata but not a full live journey page
- Journey screens do not yet collect or persist browser location points
- Evidence records are structured text only; attachments, encryption, SHA-256 audit trails and PDF export are absent
- Privacy Receipts truthfully state that no location points/token revocation occurred in the demo
- Nearby fallback records are explicitly labeled demo data
- Judge timeline is explicitly labeled simulation and excluded from impact analytics

## Incomplete

- Authentication, authorization, database migrations and durable user ownership
- PostgreSQL production configuration and retention cleanup jobs
- Onboarding, authenticated profile, settings and role-protected admin routes
- MapLibre interactive map and zero-install guardian journey experience
- Authenticated location sessions with revocation
- Encrypted evidence storage and emergency card
- Consent-aware feedback/testimonial flow
- Full analytics funnel and activated-user calculation
- Complete internationalization and automated frontend/accessibility/E2E tests
- Production email/SMS/push delivery, rate limiting across distributed instances and observability metrics

## Reusable foundations to preserve

- `app/lib/ui.tsx` design tokens and calm green visual language
- Expo Router cross-platform routes and static PWA export
- `app/lib/api.ts` timeout/error boundary behavior
- `app/lib/storage.ts` minimal local recovery patterns
- `backend/app/policy.py` deterministic escalation boundary
- `backend/app/safety_engine.py` adaptive battery policy
- `backend/app/resource_provider.py` provider-shaped resource normalization
- Existing safety disclaimers, real/demo labeling and no-autonomous-dispatch boundary

## Technical debt to address incrementally

- Split the large backend `main.py` into routers/services after persistence and auth stabilize
- Replace `any` frontend response types with shared schemas
- Externalize all UI strings
- Add database ownership to existing journey/guardian/evidence records
- Replace process-local rate limiting and event metrics with durable/distributed implementations
- Add frontend unit tests and Playwright smoke tests
- Optimize the 1.5 MB PWA icon and 1.7 MB initial JavaScript bundle

## Do not rewrite unnecessarily

Do not introduce a parallel Next.js application while the Expo Router app already provides responsive static web, PWA installation, and native reuse. Do not replace deterministic safety policies with autonomous agents. Do not fabricate production delivery, persistent analytics, location tracking, encryption, or user validation.
