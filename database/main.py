from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, JSON, DateTime, Float, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, Session, relationship
from datetime import datetime
import os

# Import allowed telemetry types from constants module
# This try-except block allows for flexible importing depending on whether you are running the script or running pytests
try:
    from database.constants import ALLOWED_TELEMETRY_TYPES
except ModuleNotFoundError:
    try:
        from constants import ALLOWED_TELEMETRY_TYPES
    except ModuleNotFoundError:
        raise ModuleNotFoundError("Could not import ALLOWED_TELEMETRY_TYPES from database.constants or constants. Please ensure the file exists.")

# Database setup (get url from environment variable or use default)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./td.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()



# Database model
# These define the structure of the database tables
class Telemetry(Base):
    __tablename__ = "Telemetry"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    stage_id = Column(Integer, nullable=False)
    telemetry_type = Column(String(30), nullable=False)
    dateTime = Column(DateTime, default=datetime.now(), nullable=False)
    data = Column(JSON)

class Parameters(Base):
    __tablename__ = "Parameter"

    name = Column(String(50), primary_key=True, index=True)
    value = Column(Float, nullable=False)

    decisions = relationship("DecisionLog", back_populates="parameter")

class BalancingRule(Base):
    __tablename__ = "BalancingRule"

    id = Column(Integer, primary_key=True, index=True)
    trigger_condition = Column(String, nullable=False)
    suggested_change = Column(String, nullable=False)
    explanation = Column(String, nullable=True)

class DecisionLog(Base):
    __tablename__ = "DecisionLog"

    id = Column(Integer, primary_key=True, index=True)
    parameter_name = Column(String(50), ForeignKey("Parameter.name"), nullable=False) # Foreign key which references Parameters.name
    stage_id = Column(Integer, nullable=True)
    change = Column(String, nullable=False)
    rationale = Column(String, nullable=True)
    evidence = Column(String, nullable=True)
    dateTime = Column(DateTime, default=datetime.now(), nullable=False)

    parameter = relationship("Parameters", back_populates="decisions")


# Create tables if they don't exist
Base.metadata.create_all(bind=engine)



# Pydantic models
# These define the structure of the data we send and receive via the API
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

    # Needed to convert from SQLAlchemy model objects to Pydantic model
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

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



# FastAPI app
app = FastAPI()

# Telemetry endpoints

# Create telemetry record
@app.post("/telemetry/", response_model=TelemetryResponse)
def create_telemetry(telemetry: TelemetryCreate, db: Session = Depends(get_db)):
    if telemetry.telemetry_type not in ALLOWED_TELEMETRY_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid telemetry_type. Allowed types: {ALLOWED_TELEMETRY_TYPES}")
    db_telemetry = Telemetry(**telemetry.model_dump())
    db.add(db_telemetry)
    db.commit()
    db.refresh(db_telemetry)
    return db_telemetry

# Get all telemetry that satisfy the given conditions
@app.get("/telemetry/", response_model=list[TelemetryResponse])
def read_telemetry(telemetry_id: int | None = None, user_id: int | None = None, stage_id: int | None = None,
                   start_time: datetime | None = None, end_time: datetime | None = None, db: Session = Depends(get_db)):
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

# Parameters endpoints

# Create or update parameter
@app.post("/parameters/", response_model=ParameterResponse)
def create_parameter(parameter: ParameterCreate, db: Session = Depends(get_db)):
    # Check if parameter already exists
    existing = db.query(Parameters).filter(Parameters.name == parameter.name).first()
    if existing:
        # Update existing parameter
        existing.value = parameter.value # type: ignore (safe to ignore as we checked for existence)
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing

    # Create new parameter if not found
    db_parameter = Parameters(name=parameter.name, value=parameter.value)
    db.add(db_parameter)
    db.commit()
    db.refresh(db_parameter)
    return db_parameter

# Read all parameters
@app.get("/parameters/", response_model=list[ParameterResponse])
def read_parameters(parameter_name: str | None = None, db: Session = Depends(get_db)):
    query = db.query(Parameters)
    if parameter_name is not None:
        query = query.filter(Parameters.name == parameter_name)
    return query.all()



# BalancingRule endpoints

# Create balancing rule
@app.post("/balancing_rules/", response_model=BalancingRuleResponse)
def create_balancing_rule(rule: BalancingRuleCreate, db: Session = Depends(get_db)):
    db_rule = BalancingRule(**rule.model_dump())
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule

# Read all balancing rules
@app.get("/balancing_rules/", response_model=list[BalancingRuleResponse])
def read_balancing_rules(rule_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(BalancingRule)
    if rule_id is not None:
        query = query.filter(BalancingRule.id == rule_id)
    return query.all()



# DecisionLog endpoints

# Create decision log entry
@app.post("/decision_logs/", response_model=DecisionLogResponse)
def create_decision_log(entry: DecisionLogCreate, db: Session = Depends(get_db)):
    db_entry = DecisionLog(**entry.model_dump())
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry

# Read all decision log entries
@app.get("/decision_logs/", response_model=list[DecisionLogResponse])
def read_decision_logs(decision_id: int | None = None, parameter_name: str | None = None, stage_id: int | None = None,
                           start_time: datetime | None = None, end_time: datetime | None = None, db: Session = Depends(get_db)):
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