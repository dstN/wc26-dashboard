from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import (
    contact,
    dashboard,
    health,
    ingest,
    matches,
    overview,
    players,
    stats,
    teams,
)

app = FastAPI(
    title="EFI WC26 Data Engine",
    version="1.0.0",
    description="Enhanced Football Intelligence — World Cup 2026 Data API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.allowed_origin],
    allow_origin_regex=r"http://localhost(:\d+)?",
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(dashboard.router)
app.include_router(matches.router)
app.include_router(teams.router)
app.include_router(players.router)
app.include_router(overview.router)
app.include_router(stats.router)
app.include_router(contact.router)
app.include_router(ingest.router)
