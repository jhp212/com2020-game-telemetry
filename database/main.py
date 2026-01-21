from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, JSON, DateTime, Float
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from datetime import datetime

# Database setup
DATABASE_URL = "sqlite:///./td.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()



# Database model
class Telemetry(Base):
    __tablename__ = "telemetry"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    stage_id = Column(Integer, nullable=False)
    telemetry_type = Column(String, nullable=False)
    dateTime = Column(DateTime, default=datetime.now(), nullable=False)
    data = Column(JSON)

class Parameters(Base):
    __tablename__ = "parameters"

    name = Column(String, primary_key=True, index=True)
    value = Column(Float, nullable=False)

Base.metadata.create_all(bind=engine)



# Pydantic models
# Models for request and response bodies, used for data validation
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

    class Config:
        from_attributes = True

class ParameterCreate(BaseModel):
    name: str
    value: float

class ParameterResponse(BaseModel):
    name: str
    value: float

    class Config:
        from_attributes = True



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
    db_telemetry = Telemetry(**telemetry.model_dump())
    db.add(db_telemetry)
    db.commit()
    db.refresh(db_telemetry)
    return db_telemetry

# Read all telemetry records
@app.get("/telemetry/", response_model=list[TelemetryResponse])
def read_all_telemetry(db: Session = Depends(get_db)):
    telemetry_records = db.query(Telemetry).all()
    return telemetry_records

# Read telemetry records for a specific user
@app.get("/telemetry/user/{user_id}", response_model=list[TelemetryResponse])
def read_telemetry(user_id: int, db: Session = Depends(get_db)):
    telemetry_records = db.query(Telemetry).filter(Telemetry.user_id == user_id).all()
    return telemetry_records

# Read telemetry records for a specific stage
@app.get("/telemetry/stage/{stage_id}", response_model=list[TelemetryResponse])
def read_telemetry_by_stage(stage_id: int, db: Session = Depends(get_db)):
    telemetry_records = db.query(Telemetry).filter(Telemetry.stage_id == stage_id).all()
    return telemetry_records


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
def read_all_parameters(db: Session = Depends(get_db)):
    parameters = db.query(Parameters).all()
    return parameters

# Read parameter by name
@app.get("/parameters/{name}", response_model=ParameterResponse)
def read_parameter(name: str, db: Session = Depends(get_db)):
    parameter = db.query(Parameters).filter(Parameters.name == name).first()
    if parameter is None:
        raise HTTPException(status_code=404, detail="Parameter not found")
    return parameter