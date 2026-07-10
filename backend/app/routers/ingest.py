"""
PDF Ingest Upload Endpoint
==========================
Protected by Bearer token (INGEST_SECRET_KEY in .env).

POST /api/v1/ingest/upload
  Authorization: Bearer <INGEST_SECRET_KEY>
  Content-Type: multipart/form-data
  Body: file=<pdf>

Saves the PDF to PDF_WATCH_DIR, then triggers watch_pdfs.py immediately as a
subprocess. Returns the log output and success/error status.

On Phusion Passenger: set INGESTION_MODULE_DIR to the absolute path of the
ingestion package root (the directory containing the 'ingestion/' sub-package).
Set INGESTION_PYTHON to the Python interpreter that has the ingestion deps
installed (pymupdf, sqlalchemy, etc.).
"""

from __future__ import annotations

import asyncio
import secrets
import subprocess
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings

router = APIRouter(prefix="/api/v1/ingest", tags=["ingest"])

_bearer = HTTPBearer(auto_error=False)

MAX_PDF_BYTES = 50 * 1024 * 1024  # 50 MB


def _require_key(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> None:
    if not settings.ingest_secret_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Ingest endpoint is not configured on this server.",
        )
    if credentials is None or not secrets.compare_digest(
        credentials.credentials, settings.ingest_secret_key
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key.",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post(
    "/upload",
    summary="Upload a PDF match report and ingest it immediately",
    status_code=status.HTTP_200_OK,
)
async def upload_pdf(
    file: UploadFile = File(..., description="EFI Post Match Summary Report (PDF)"),
    _: None = Depends(_require_key),
) -> dict:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .pdf files are accepted.",
        )

    content = await file.read()
    if len(content) > MAX_PDF_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File exceeds the 50 MB limit.",
        )
    if not content.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is not a valid PDF.",
        )

    watch_dir = Path(settings.pdf_watch_dir).expanduser().resolve()
    watch_dir.mkdir(parents=True, exist_ok=True)

    # basename only — a client-supplied "../x.pdf" or absolute path must never
    # escape the watch dir
    safe_name = Path(file.filename).name
    if not safe_name or safe_name.startswith("."):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file name.",
        )
    dest = (watch_dir / safe_name).resolve()
    if dest.parent != watch_dir:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file name.",
        )
    await asyncio.to_thread(dest.write_bytes, content)

    # Re-process only the uploaded file (not the whole drop dir)
    python = settings.ingestion_python or "python3"
    cmd = [
        python, "-m", "ingestion.watch_pdfs",
        "--dir", str(watch_dir), "--force", "--file", str(dest),
    ]

    cwd = settings.ingestion_module_dir or None

    try:
        # subprocess.run blocks — run it in a worker thread so the event loop
        # (and every other endpoint) stays responsive during ingestion
        proc = await asyncio.to_thread(
            subprocess.run,
            cmd,
            capture_output=True,
            text=True,
            timeout=180,
            cwd=cwd,
        )
        ok = proc.returncode == 0
        log = (proc.stdout + proc.stderr).strip()
    except FileNotFoundError:
        dest.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                f"Python interpreter not found: {python!r}. "
                "Set INGESTION_PYTHON and INGESTION_MODULE_DIR in .env."
            ),
        )
    except subprocess.TimeoutExpired:
        dest.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Ingestion timed out after 180 s.",
        )

    if not ok:
        # remove the bad PDF so the cron fallback does not retry it forever
        dest.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"message": "Ingestion failed.", "log": log},
        )

    return {
        "status": "ok",
        "file": safe_name,
        "saved_to": str(dest),
        "log": log,
    }
