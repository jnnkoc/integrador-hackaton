from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from services.auth import verify_admin
import models
import schemas

router = APIRouter(prefix="/api/v1/admin/logs", tags=["admin-logs"])


@router.get("", response_model=list[schemas.ExecutionResponse])
def list_all_logs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _=Depends(verify_admin),
):
    return (
        db.query(models.Execution)
        .order_by(models.Execution.executed_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
