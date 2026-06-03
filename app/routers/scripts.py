from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from services.auth import get_validated_token
from services.executor import execute_script
import models
import schemas

router = APIRouter(prefix="/api/v1/scripts", tags=["scripts"])


@router.get("", response_model=list[schemas.ScriptPublic])
def list_scripts(db: Session = Depends(get_db), token: models.Token = Depends(get_validated_token)):
    return db.query(models.Script).filter(models.Script.is_active == True).all()


@router.post("/{name}/execute", response_model=schemas.ExecutionResponse)
def execute(
    name: str,
    body: schemas.ExecuteRequest,
    db: Session = Depends(get_db),
    token: models.Token = Depends(get_validated_token),
):
    script = db.query(models.Script).filter(models.Script.name == name).first()
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    if not script.is_active:
        raise HTTPException(status_code=403, detail="Script is inactive")

    result = execute_script(script, body.parameters)

    execution = models.Execution(
        script_id=script.id,
        token_id=token.id,
        parameters=body.parameters,
        stdout=result["stdout"],
        stderr=result["stderr"],
        exit_code=result["exit_code"],
        status=result["status"],
    )
    db.add(execution)
    db.commit()
    db.refresh(execution)
    return execution
