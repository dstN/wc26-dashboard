import asyncio
import smtplib
import time
from email.message import EmailMessage

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, EmailStr

from app.config import settings

router = APIRouter(prefix="/api/v1", tags=["contact"])

# Simple in-memory rate limiter: max 3 requests per IP per hour
_rate: dict[str, list[float]] = {}
_RATE_LIMIT = 3
_RATE_WINDOW = 3600


def _check_rate(ip: str) -> None:
    now = time.time()
    # Sweep expired timestamps for ALL known IPs — otherwise the dict grows
    # unboundedly with every distinct client IP that ever hits the endpoint.
    for known_ip in list(_rate):
        fresh = [t for t in _rate[known_ip] if now - t < _RATE_WINDOW]
        if fresh:
            _rate[known_ip] = fresh
        else:
            del _rate[known_ip]
    timestamps = _rate.get(ip, [])
    if len(timestamps) >= _RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")
    timestamps.append(now)
    _rate[ip] = timestamps


class ContactPayload(BaseModel):
    name: str
    email: EmailStr
    message: str


def _send_email(payload: ContactPayload) -> None:
    if not settings.smtp_user or not settings.smtp_pass:
        raise RuntimeError("SMTP credentials not configured")

    msg = EmailMessage()
    msg["Subject"] = f"EFI Dashboard — Contact from {payload.name}"
    msg["From"] = settings.smtp_user
    msg["To"] = settings.contact_to_email
    msg["Reply-To"] = payload.email
    msg.set_content(
        f"Name: {payload.name}\n"
        f"Email: {payload.email}\n"
        f"\n{payload.message}"
    )

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as s:
        s.ehlo()
        s.starttls()
        s.login(settings.smtp_user, settings.smtp_pass)
        s.send_message(msg)


@router.post("/contact")
async def contact(payload: ContactPayload, request: Request) -> dict:
    ip = request.client.host if request.client else "unknown"
    _check_rate(ip)

    if not payload.name.strip() or not payload.message.strip():
        raise HTTPException(status_code=422, detail="Name and message are required.")

    try:
        await asyncio.to_thread(_send_email, payload)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except smtplib.SMTPException as e:
        raise HTTPException(status_code=502, detail=f"Mail delivery failed: {e}")

    return {"ok": True}
