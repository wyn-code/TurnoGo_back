from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_negocio
from app.db.session import get_db
from app.models.negocio import Negocio
from app.services.estadistica_service import StatisticsService

router = APIRouter(prefix="/statistics", tags=["Statistics"])


@router.get("/business/{business_id}")
def get_statistics(
    business_id: int,
    negocio: Negocio = Depends(get_current_negocio),
    db: Session = Depends(get_db),
):
    if negocio.id_negocio != business_id:
        raise HTTPException(
            status_code=403,
            detail="No tenés acceso a las estadísticas de este negocio",
        )

    service = StatisticsService(db)
    return service.get_dashboard_statistics(business_id)
