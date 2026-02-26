from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from database import get_db # type: ignore
from models import *
import schemas
from security import get_current_user, get_current_admin_user

# This try-except is needed to allow importing from the correct location whether running from main.py or directly from this file for testing
try:
    from database.constants import ALLOWED_TELEMETRY_TYPES # type: ignore
except (ModuleNotFoundError, ImportError):
    from constants import ALLOWED_TELEMETRY_TYPES

router = APIRouter(tags=["Game Data"])

# Create a new telemetry entry (Access: Everyone)
@router.post("/telemetry/", response_model=schemas.TelemetryResponse)
def create_telemetry(telemetry: schemas.TelemetryCreate, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    if telemetry.telemetry_type not in ALLOWED_TELEMETRY_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid telemetry_type. Allowed types: {ALLOWED_TELEMETRY_TYPES}")
    db_telemetry = Telemetry(**telemetry.model_dump())
    db.add(db_telemetry)
    db.commit()
    db.refresh(db_telemetry)
    return db_telemetry

# Read telemetry entries with optional filters (Access: Admin)
@router.get("/telemetry/", response_model=list[schemas.TelemetryResponse])
def read_telemetry(telemetry_id: int | None = None, user_id: int | None = None, stage_id: int | None = None,
                   start_time: datetime | None = None, end_time: datetime | None = None, 
                   db: Session = Depends(get_db), current_user: Users = Depends(get_current_admin_user)):
    query = db.query(Telemetry)
    if telemetry_id is not None:
        query = query.filter(Telemetry.id == telemetry_id)
    if user_id is not None:
        query = query.filter(Telemetry.user_id == user_id)
    if stage_id is not None:
        query = query.filter(Telemetry.stage_id == stage_id)
    if start_time is not None and end_time is not None:
        query = query.filter(Telemetry.dateTime >= start_time, Telemetry.dateTime <= end_time)
    elif start_time is not None:
        query = query.filter(Telemetry.dateTime >= start_time)
    elif end_time is not None:
        query = query.filter(Telemetry.dateTime <= end_time)
    return query.all()

# Create or update a parameter (Access: Admin)
@router.post("/parameters/", response_model=schemas.ParameterResponse)
def create_parameter(parameter: schemas.ParameterCreate, db: Session = Depends(get_db), current_user: Users = Depends(get_current_admin_user)):
    existing = db.query(Parameters).filter(Parameters.name == parameter.name).first()
    if existing:
        existing.value = parameter.value # type: ignore
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing

    db_parameter = Parameters(name=parameter.name, value=parameter.value)
    db.add(db_parameter)
    db.commit()
    db.refresh(db_parameter)
    return db_parameter

# Read parameters with optional name filter (Access: Everyone)
@router.get("/parameters/", response_model=list[schemas.ParameterResponse])
def read_parameters(parameter_name: str | None = None, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    query = db.query(Parameters)
    if parameter_name is not None:
        query = query.filter(Parameters.name == parameter_name)
    return query.all()

# Create a new balancing rule (Access: Admin)
@router.post("/balancing_rules/", response_model=schemas.BalancingRuleResponse)
def create_balancing_rule(rule: schemas.BalancingRuleCreate, db: Session = Depends(get_db), current_user: Users = Depends(get_current_admin_user)):
    db_rule = BalancingRule(**rule.model_dump())
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule

# Read balancing rules with optional id filter (Access: Admin)
@router.get("/balancing_rules/", response_model=list[schemas.BalancingRuleResponse])
def read_balancing_rules(rule_id: int | None = None, db: Session = Depends(get_db), current_user: Users = Depends(get_current_admin_user)):
    query = db.query(BalancingRule)
    if rule_id is not None:
        query = query.filter(BalancingRule.id == rule_id)
    return query.all()

# Create a new decision log entry (Access: Admin)
@router.post("/decision_logs/", response_model=schemas.DecisionLogResponse)
def create_decision_log(entry: schemas.DecisionLogCreate, db: Session = Depends(get_db), current_user: Users = Depends(get_current_admin_user)):
    db_entry = DecisionLog(**entry.model_dump())
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry

# Read decision logs with optional filters (Access: Admin)
@router.get("/decision_logs/", response_model=list[schemas.DecisionLogResponse])
def read_decision_logs(decision_id: int | None = None, parameter_name: str | None = None, stage_id: int | None = None,
                           start_time: datetime | None = None, end_time: datetime | None = None, 
                           db: Session = Depends(get_db), current_user: Users = Depends(get_current_admin_user)):
    query = db.query(DecisionLog)
    if decision_id is not None:
        query = query.filter(DecisionLog.decision_id == decision_id)
    if parameter_name is not None:
        query = query.filter(DecisionLog.parameter_name == parameter_name)
    if stage_id is not None:
        query = query.filter(DecisionLog.stage_id == stage_id)
    if start_time is not None and end_time is not None:
        query = query.filter(DecisionLog.dateTime >= start_time, DecisionLog.dateTime <= end_time)
    elif start_time is not None:
        query = query.filter(DecisionLog.dateTime >= start_time)
    elif end_time is not None:
        query = query.filter(DecisionLog.dateTime <= end_time)
    return query.all()