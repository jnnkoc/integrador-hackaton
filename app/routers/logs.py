from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from services.auth import get_validated_token
import models
import schemas

router = APIRouter(prefix="/api/v1/logs", tags=["logs"])


@router.get("", response_model=list[schemas.ExecutionResponse])
def list_logs(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    token: models.Token = Depends(get_validated_token),
):
    return (
        db.query(models.Execution)
        .filter(models.Execution.token_id == token.id)
        .order_by(models.Execution.executed_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{execution_id}", response_model=schemas.ExecutionResponse)
def get_log(
    execution_id: str,
    db: Session = Depends(get_db),
    token: models.Token = Depends(get_validated_token),
):
    execution = db.query(models.Execution).filter(
        models.Execution.id == execution_id,
        models.Execution.token_id == token.id,
    ).first()
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    return execution
