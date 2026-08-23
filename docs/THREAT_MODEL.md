# Shakti360 threat model

## Safety boundary

Shakti360 provides decision support. It does not detect attackers, guarantee safety, or autonomously contact emergency services. Safety-critical transitions are deterministic and versioned.

## Protected assets

- Temporary journey locations and sharing tokens
- Guardian identity and permissions
- Evidence content and hashes
- Emergency profile data
- Authentication and refresh tokens (production roadmap)

## Primary threats and mitigations

| Threat | Current mitigation | Production requirement |
|---|---|---|
| Stalker gains account access | Minimal session data; Quick Exit | Passkeys/MFA, device-bound sessions, login alerts |
| Guardian link leaks | Random token, 24-hour invitation expiry, two-hour SOS session | Hashed tokens, one-time acceptance, revocation UI |
| Phone is lost | No automatic evidence upload | Device secure storage, biometric app lock, remote revocation |
| Backend is compromised | No coordinate/evidence logging in app code | Database encryption, key separation, audit monitoring |
| Malicious upload | Evidence upload not implemented | MIME validation, size limits, malware scanning, isolated storage |
| API abuse | Pydantic input constraints | Per-user/IP rate limits, auth scopes, WAF controls |

## Logging rules

Never log coordinates, evidence contents, health information, access/refresh tokens, SafeWords, or guardian phone numbers. Analytics events use opaque IDs and event names.

## Known hackathon limitations

The API uses in-memory session storage and permissive development CORS. Authentication, encrypted persistent storage, rate limiting, and deletion workflows must ship before a real pilot.
