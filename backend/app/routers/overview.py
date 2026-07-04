from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db
from app.services.overview_service import get_overview

router = APIRouter(prefix="/api/v1", tags=["overview"])


@router.get("/overview")
async def get_tournament_overview(db: AsyncSession = Depends(get_db)):
    return await get_overview(db)
