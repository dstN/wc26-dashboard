from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db
from app.schemas.dashboard import DashboardResponse
from app.services.match_service import get_match_dashboard, get_featured_match_id

router = APIRouter(prefix="/api/v1", tags=["dashboard"])


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    is_featured: int = Query(default=1),
    db: AsyncSession = Depends(get_db),
):
    match_id = await get_featured_match_id(db)
    return await get_match_dashboard(db, match_id)
