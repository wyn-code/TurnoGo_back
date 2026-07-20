from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_negocio
from app.db.session import get_db
from app.models.negocio import Negocio
from app.services.estadistica_service import StatisticsService

router = APIRouter(prefix="/statistics", tags=["Statistics"])


def _parse_date(value: str | None) -> date | None:
    if value is None:
        return None
    return date.fromisoformat(value.split("T")[0])


@router.get("/business/{business_id}")
def get_statistics(
    business_id: int,
    date_start: Optional[str] = Query(None),
    date_end: Optional[str] = Query(None),
    negocio: Negocio = Depends(get_current_negocio),
    db: Session = Depends(get_db),
):
    if negocio.id_negocio != business_id:
        raise HTTPException(
            status_code=403,
            detail="No tenés acceso a las estadísticas de este negocio",
        )

    ds = _parse_date(date_start)
    de = _parse_date(date_end)

    service = StatisticsService(db)
    return service.get_dashboard_statistics(business_id, ds, de)
