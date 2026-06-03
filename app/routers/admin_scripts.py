from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from services.auth import verify_admin
import models
import schemas

router = APIRouter(prefix="/api/v1/admin/scripts", tags=["admin-scripts"])


@router.get("", response_model=list[schemas.ScriptResponse])
def list_scripts(db: Session = Depends(get_db), _=Depends(verify_admin)):
    return db.query(models.Script).all()


@router.post("", response_model=schemas.ScriptResponse, status_code=201)
def create_script(data: schemas.ScriptCreate, db: Session = Depends(get_db), _=Depends(verify_admin)):
    if db.query(models.Script).filter(models.Script.name == data.name).first():
        raise HTTPException(status_code=400, detail="Script name already exists")
    script = models.Script(**data.model_dump())
    db.add(script)
    db.commit()
    db.refresh(script)
    return script


@router.put("/{script_id}", response_model=schemas.ScriptResponse)
def update_script(script_id: str, data: schemas.ScriptUpdate, db: Session = Depends(get_db), _=Depends(verify_admin)):
    script = db.query(models.Script).filter(models.Script.id == script_id).first()
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(script, field, value)
    db.commit()
    db.refresh(script)
    return script


@router.delete("/{script_id}", status_code=204)
def delete_script(script_id: str, db: Session = Depends(get_db), _=Depends(verify_admin)):
    script = db.query(models.Script).filter(models.Script.id == script_id).first()
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    db.delete(script)
    db.commit()
