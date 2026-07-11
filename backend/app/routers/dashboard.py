from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db
from app.schemas.dashboard import DashboardResponse
from app.services.match_service import get_latest_match_id, get_match_dashboard

router = APIRouter(prefix="/api/v1", tags=["dashboard"])


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(db: AsyncSession = Depends(get_db)):
    try:
        match_id = await get_latest_match_id(db)
        return await get_match_dashboard(db, match_id)
    except ValueError as e:
        # empty DB / unknown match — a clean 404 instead of an unhandled 500
        raise HTTPException(status_code=404, detail=str(e))
    except NoResultFound:
        raise HTTPException(
            status_code=404,
            detail="Featured match is missing stats rows — re-run ingestion.",
        )
