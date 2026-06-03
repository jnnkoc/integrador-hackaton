import secrets
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from database import get_db
from services.auth import verify_admin
import models
import schemas

router = APIRouter(prefix="/api/v1/admin/tokens", tags=["admin-tokens"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.get("", response_model=list[schemas.TokenResponse])
def list_tokens(db: Session = Depends(get_db), _=Depends(verify_admin)):
    return db.query(models.Token).all()


@router.post("", response_model=schemas.TokenResponse, status_code=201)
def create_token(data: schemas.TokenCreate, db: Session = Depends(get_db), _=Depends(verify_admin)):
    if db.query(models.Token).filter(models.Token.username == data.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    token = models.Token(
        name=data.name,
        username=data.username,
        password_hash=pwd_context.hash(data.password),
        token=secrets.token_hex(32)
    )
    db.add(token)
    db.commit()
    db.refresh(token)
    return token


@router.patch("/{token_id}", response_model=schemas.TokenResponse)
def patch_token(token_id: str, data: schemas.TokenPatch, db: Session = Depends(get_db), _=Depends(verify_admin)):
    token = db.query(models.Token).filter(models.Token.id == token_id).first()
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")
    token.is_active = data.is_active
    db.commit()
    db.refresh(token)
    return token


@router.delete("/{token_id}", status_code=204)
def delete_token(token_id: str, db: Session = Depends(get_db), _=Depends(verify_admin)):
    token = db.query(models.Token).filter(models.Token.id == token_id).first()
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")
    db.delete(token)
    db.commit()
