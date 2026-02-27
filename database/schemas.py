from pydantic import BaseModel
from datetime import datetime

class TelemetryCreate(BaseModel):
    user_id: int
    stage_id: int
    telemetry_type: str
    dateTime: datetime
    data: dict

class TelemetryResponse(BaseModel):
    id: int
    user_id: int
    stage_id: int
    telemetry_type: str
    dateTime: datetime
    data: dict
    model_config = {"from_attributes": True}

class ParameterCreate(BaseModel):
    name: str
    value: float

class ParameterResponse(BaseModel):
    name: str
    value: float
    model_config = {"from_attributes": True}

class BalancingRuleCreate(BaseModel):
    trigger_condition: str
    suggested_change: str
    explanation: str | None = None

class BalancingRuleResponse(BaseModel):
    id: int
    trigger_condition: str
    suggested_change: str
    explanation: str | None = None
    model_config = {"from_attributes": True}

class DecisionLogCreate(BaseModel):
    parameter_name: str
    stage_id: int | None = None
    change: str
    rationale: str
    evidence: str | None = None
    dateTime: datetime

class DecisionLogResponse(BaseModel):
    id: int
    parameter_name: str
    stage_id: int | None = None
    change: str
    rationale: str
    evidence: str | None = None
    dateTime: datetime
    model_config = {"from_attributes": True}

class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    is_admin: int
    created_at: datetime
    model_config = {"from_attributes": True}

class TokenResponse(BaseModel):
    user_id: int
    access_token: str
    token_type: str
    is_admin: int

class AnomalyCreate(BaseModel):
    telemetry_ids: list[int]
    anomaly_type: str
    resolution: str | None = None

class AnomalyResponse(BaseModel):
    id: int
    telemetry_ids: list[int]
    anomaly_type: str
    resolution: str | None = None
    model_config = {"from_attributes": True}