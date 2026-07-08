from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.estadistica_service import StatisticsService

router = APIRouter(prefix="/statistics", tags=["Statistics"])


@router.get("/business/{business_id}")
def get_statistics(
    business_id: int,
    db: Session = Depends(get_db),
):
    service = StatisticsService(db)
    return service.get_dashboard_statistics(business_id)