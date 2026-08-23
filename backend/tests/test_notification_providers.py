import asyncio
from urllib.parse import parse_qs

import httpx

from app.notifications import send_email, send_sms


def test_twilio_request_contract(monkeypatch):
    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "AC123")
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "secret")
    monkeypatch.setenv("TWILIO_FROM_NUMBER", "+15550001111")
    captured = {}

    def handler(request: httpx.Request):
        captured["url"] = str(request.url)
        captured["form"] = parse_qs(request.content.decode())
        captured["authorization"] = request.headers.get("authorization")
        return httpx.Response(201, json={"sid": "SM123", "status": "queued"})

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await send_sms(client, "+15550002222", "Safety update")

    result = asyncio.run(run())
    assert result == {"channel": "sms", "status": "queued", "provider_id": "SM123", "message": "SMS queued by Twilio."}
    assert captured["url"].endswith("/Accounts/AC123/Messages.json")
    assert captured["form"] == {"To": ["+15550002222"], "Body": ["Safety update"], "From": ["+15550001111"]}
    assert captured["authorization"].startswith("Basic ")


def test_resend_request_contract(monkeypatch):
    monkeypatch.setenv("RESEND_API_KEY", "re_test")
    monkeypatch.setenv("RESEND_FROM_EMAIL", "Guardian <guardian@example.com>")
    captured = {}

    def handler(request: httpx.Request):
        captured["headers"] = request.headers
        captured["body"] = request.content.decode()
        return httpx.Response(200, json={"id": "email-123"})

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await send_email(client, "asha@example.com", "Safety update", "Plain text", "<p>Plain text</p>", "event-123")

    result = asyncio.run(run())
    assert result == {"channel": "email", "status": "queued", "provider_id": "email-123", "message": "Email accepted by Resend."}
    assert captured["headers"]["authorization"] == "Bearer re_test"
    assert captured["headers"]["idempotency-key"] == "event-123"
    assert '"to":["asha@example.com"]' in captured["body"].replace(" ", "")
