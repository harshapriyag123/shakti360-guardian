import html
import os
from typing import Any

import httpx


def invite_url(token: str) -> str:
    base = os.getenv("GUARDIAN_INVITE_BASE_URL", "http://localhost:8080/guardian-invite").rstrip("/")
    return f"{base}?token={token}"


def invite_copy(guardian: dict[str, Any]) -> tuple[str, str, str]:
    url = invite_url(guardian["invite_token"])
    expires = guardian["invite_expires_at"].strftime("%b %d, %Y at %H:%M UTC")
    text = (
        f"{guardian['name']}, you have been invited to join a Shakti360 Guardian Circle. "
        f"Review the temporary permissions here: {url} This invitation expires {expires}. "
        "If you did not expect this, ignore it."
    )
    safe_name, safe_url, safe_expires = html.escape(guardian["name"]), html.escape(url), html.escape(expires)
    email_html = (
        f"<h2>You're invited to a Guardian Circle</h2><p>Hello {safe_name},</p>"
        "<p>Someone you trust invited you to receive selected Shakti360 safety updates.</p>"
        f'<p><a href="{safe_url}">Review invitation</a></p><p>This link expires {safe_expires}.</p>'
        "<p>If you did not expect this invitation, you can safely ignore it.</p>"
    )
    return url, text, email_html


async def send_guardian_invite(guardian: dict[str, Any], channels: list[str]) -> list[dict[str, Any]]:
    _, text, email_html = invite_copy(guardian)
    results: list[dict[str, Any]] = []
    async with httpx.AsyncClient(timeout=12) as client:
        if "sms" in channels:
            results.append(await send_sms(client, guardian.get("phone"), text))
        if "email" in channels:
            results.append(await send_email(client, guardian.get("email"), "You're invited to a Shakti360 Guardian Circle", text, email_html, f"invite-{guardian['id']}"))
    return results


async def send_sms(client: httpx.AsyncClient, recipient: str | None, body: str) -> dict[str, Any]:
    if not recipient:
        return {"channel": "sms", "status": "failed", "message": "Add a mobile number first."}
    sid, token = os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN")
    sender, service = os.getenv("TWILIO_FROM_NUMBER"), os.getenv("TWILIO_MESSAGING_SERVICE_SID")
    if not sid or not token or not (sender or service):
        return {"channel": "sms", "status": "not_configured", "message": "SMS provider is not configured."}
    payload = {"To": recipient, "Body": body, **({"MessagingServiceSid": service} if service else {"From": sender})}
    try:
        response = await client.post(
            f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json",
            data=payload,
            auth=httpx.BasicAuth(sid, token),
        )
        response.raise_for_status()
        data = response.json()
        return {"channel": "sms", "status": "queued", "provider_id": data.get("sid"), "message": "SMS queued by Twilio."}
    except httpx.HTTPError:
        return {"channel": "sms", "status": "failed", "message": "Twilio rejected the SMS. Check the number and provider logs."}


async def send_email(client: httpx.AsyncClient, recipient: str | None, subject: str, text: str, email_html: str, idempotency_key: str) -> dict[str, Any]:
    if not recipient:
        return {"channel": "email", "status": "failed", "message": "Add an email address first."}
    api_key, sender = os.getenv("RESEND_API_KEY"), os.getenv("RESEND_FROM_EMAIL")
    if not api_key or not sender:
        return {"channel": "email", "status": "not_configured", "message": "Email provider is not configured."}
    try:
        response = await client.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {api_key}", "User-Agent": "Shakti360-Guardian/1.0", "Idempotency-Key": idempotency_key[:256]},
            json={"from": sender, "to": [recipient], "subject": subject, "text": text, "html": email_html},
        )
        response.raise_for_status()
        data = response.json()
        return {"channel": "email", "status": "queued", "provider_id": data.get("id"), "message": "Email accepted by Resend."}
    except httpx.HTTPError:
        return {"channel": "email", "status": "failed", "message": "Resend rejected the email. Check the address and provider logs."}


def provider_status() -> dict[str, Any]:
    sms_ready = bool(os.getenv("TWILIO_ACCOUNT_SID") and os.getenv("TWILIO_AUTH_TOKEN") and (os.getenv("TWILIO_FROM_NUMBER") or os.getenv("TWILIO_MESSAGING_SERVICE_SID")))
    email_ready = bool(os.getenv("RESEND_API_KEY") and os.getenv("RESEND_FROM_EMAIL"))
    return {"sms": {"provider": "twilio", "configured": sms_ready}, "email": {"provider": "resend", "configured": email_ready}}


async def send_guardian_alert(guardian: dict[str, Any], event: str, message: str | None, location_url: str | None, event_id: str) -> list[dict[str, Any]]:
    titles = {"journey_started": "Safety journey started", "missed_checkin": "Missed safety check-in", "sos": "SOS alert", "journey_completed": "Safety journey completed", "sos_cancelled": "SOS alert cancelled"}
    subject = f"Shakti360: {titles[event]}"
    detail = message or {"journey_started": "A safety journey has started.", "missed_checkin": "A scheduled safety check-in was missed.", "sos": "An SOS was activated. Contact the person and follow their agreed safety plan.", "journey_completed": "The safety journey was marked complete.", "sos_cancelled": "The SOS was cancelled by the user."}[event]
    location = f" Temporary session location: {location_url}" if location_url else ""
    text = f"Shakti360 Guardian update for {guardian['name']}: {detail}{location} Do not rely on this message as a replacement for emergency services."
    email_html = f"<h2>{html.escape(subject)}</h2><p>{html.escape(detail)}</p>" + (f'<p><a href="{html.escape(location_url)}">Open temporary session location</a></p>' if location_url else "") + "<p>This safety update does not replace emergency services.</p>"
    results: list[dict[str, Any]] = []
    async with httpx.AsyncClient(timeout=12) as client:
        if guardian.get("phone"):
            results.append(await send_sms(client, guardian["phone"], text))
        if guardian.get("email"):
            results.append(await send_email(client, guardian["email"], subject, text, email_html, f"alert-{event_id}-{guardian['id']}-{event}"))
    if not results:
        results.append({"channel": "none", "status": "failed", "message": "Guardian has no delivery address."})
    return results
