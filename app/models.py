import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Text, Integer, DateTime, ForeignKey
from sqlalchemy.types import JSON
from database import Base

def _uuid():
    return str(uuid.uuid4())

class Script(Base):
    __tablename__ = "scripts"

    id = Column(String(36), primary_key=True, default=_uuid)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, default="")
    content = Column(Text, nullable=False)
    parameters = Column(JSON, default=list)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Token(Base):
    __tablename__ = "tokens"

    id = Column(String(36), primary_key=True, default=_uuid)
    name = Column(String(100), nullable=False)
    username = Column(String(100), unique=True, nullable=True, index=True)
    password_hash = Column(String(128), nullable=True)
    token = Column(String(64), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Execution(Base):
    __tablename__ = "executions"

    id = Column(String(36), primary_key=True, default=_uuid)
    script_id = Column(String(36), ForeignKey("scripts.id"), nullable=False)
    token_id = Column(String(36), ForeignKey("tokens.id"), nullable=False)
    parameters = Column(JSON, default=dict)
    stdout = Column(Text, default="")
    stderr = Column(Text, default="")
    exit_code = Column(Integer, default=0)
    status = Column(String(20), default="success")
    executed_at = Column(DateTime, default=datetime.utcnow)
