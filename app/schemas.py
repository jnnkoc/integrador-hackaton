from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class ScriptCreate(BaseModel):
    name: str
    description: str = ""
    content: str
    parameters: List[str] = []
    is_active: bool = True


class ScriptUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    parameters: Optional[List[str]] = None
    is_active: Optional[bool] = None


class ScriptResponse(BaseModel):
    id: str
    name: str
    description: str
    content: str
    parameters: List[str]
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ScriptPublic(BaseModel):
    id: str
    name: str
    description: str
    parameters: List[str]

    model_config = {"from_attributes": True}


class TokenCreate(BaseModel):
    name: str
    username: str
    password: str


class TokenPatch(BaseModel):
    is_active: bool


class TokenResponse(BaseModel):
    id: str
    name: str
    token: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminLoginRequest(BaseModel):
    password: str


class ClientLoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    token_type: str = "bearer"


class ExecuteRequest(BaseModel):
    parameters: Dict[str, Any] = {}


class ExecutionResponse(BaseModel):
    id: str
    script_id: str
    token_id: str
    parameters: Dict[str, Any]
    stdout: str
    stderr: str
    exit_code: int
    status: str
    executed_at: datetime

    model_config = {"from_attributes": True}
