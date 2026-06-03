from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from config import settings
import models


def get_validated_token(
    x_isy_token: str = Header(...),
    db: Session = Depends(get_db)
) -> models.Token:
    token = db.query(models.Token).filter(
        models.Token.token == x_isy_token,
        models.Token.is_active == True
    ).first()
    if not token:
        raise HTTPException(status_code=401, detail="Invalid or inactive token")
    return token


def verify_admin(x_isy_admin_token: str = Header(...)):
    if x_isy_admin_token != settings.admin_token:
        raise HTTPException(status_code=401, detail="Invalid admin token")
    return x_isy_admin_token
