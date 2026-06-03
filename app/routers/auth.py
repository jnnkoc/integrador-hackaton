from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from database import get_db
from config import settings
import models
import schemas

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/admin/login", response_model=schemas.LoginResponse)
def admin_login(data: schemas.AdminLoginRequest):
    if data.password != settings.admin_password:
        raise HTTPException(status_code=401, detail="Invalid admin password")
    return schemas.LoginResponse(token=settings.admin_token)


@router.post("/login", response_model=schemas.LoginResponse)
def client_login(data: schemas.ClientLoginRequest, db: Session = Depends(get_db)):
    token = db.query(models.Token).filter(
        models.Token.username == data.username,
        models.Token.is_active == True
    ).first()
    if not token or not token.password_hash:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not pwd_context.verify(data.password, token.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return schemas.LoginResponse(token=token.token)
