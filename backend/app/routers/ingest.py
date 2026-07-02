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
    if credentials is None or credentials.credentials != settings.ingest_secret_key:
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
            detail=f"File exceeds the 50 MB limit.",
        )

    watch_dir = Path(settings.pdf_watch_dir).expanduser().resolve()
    watch_dir.mkdir(parents=True, exist_ok=True)

    dest = watch_dir / file.filename
    dest.write_bytes(content)

    # Build subprocess command — force re-process this specific file
    python = settings.ingestion_python or "python3"
    cmd = [python, "-m", "ingestion.watch_pdfs", "--dir", str(watch_dir), "--force"]

    cwd = settings.ingestion_module_dir or None

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=180,
            cwd=cwd,
        )
        ok = proc.returncode == 0
        log = (proc.stdout + proc.stderr).strip()
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                f"Python interpreter not found: {python!r}. "
                "Set INGESTION_PYTHON and INGESTION_MODULE_DIR in .env."
            ),
        )
    except subprocess.TimeoutExpired:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Ingestion timed out after 180 s.",
        )

    if not ok:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"message": "Ingestion failed.", "log": log},
        )

    return {
        "status": "ok",
        "file": file.filename,
        "saved_to": str(dest),
        "log": log,
    }
