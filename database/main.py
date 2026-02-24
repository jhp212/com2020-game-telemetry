from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, JSON, DateTime, Float, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, Session, relationship
from datetime import datetime, timedelta
from passlib.context import CryptContext
from contextlib import asynccontextmanager
import jwt
import os

# Import allowed telemetry types from constants module
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

# --- SECURITY CONFIGURATION ---
SECRET_KEY = os.getenv("SECRET_KEY", "SUPER_SECRET_DEV_KEY_CHANGE_IN_PRODUCTION")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Using the argon2 hashing algorithm for password hashing
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency to verify token and get current user (For everyone)
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
        
    user = db.query(Users).filter(Users.username == username).first()
    if user is None:
        raise credentials_exception
    return user

# Dependency to verify token AND check admin status (For dashboard access)
def get_current_admin_user(current_user = Depends(get_current_user)):
    if current_user.is_admin != 1:
        raise HTTPException(
            status_code=403, 
            detail="Not enough privileges. Admin access required."
        )
    return current_user


# --- DATABASE MODELS ---
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
    parameter_name = Column(String(50), ForeignKey("Parameter.name"), nullable=False)
    stage_id = Column(Integer, nullable=True)
    change = Column(String, nullable=False)
    rationale = Column(String, nullable=True)
    evidence = Column(String, nullable=True)
    dateTime = Column(DateTime, default=datetime.now(), nullable=False)
    parameter = relationship("Parameters", back_populates="decisions")

class Users(Base):
    __tablename__ = "Users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False)
    password_hash = Column(String(128), nullable=False)
    is_admin = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now(), nullable=False)

Base.metadata.create_all(bind=engine)

# --- PYDANTIC MODELS ---
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

    # Enable from_attributes to allow automatic conversion from SQLAlchemy models
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
    is_admin: int # Added so the dashboard immediately knows the user's role

# Default parameter values
DEFAULT_PARAMETERS = [
    {"name": "enemy_damage_multiplier", "value": 1.0}
]

def initialize_default_parameters():
    db = SessionLocal()
    try:
        for param in DEFAULT_PARAMETERS:
            existing = db.query(Parameters).filter(Parameters.name == param["name"]).first()
            
            if not existing:
                new_param = Parameters(name=param["name"], value=param["value"])
                db.add(new_param)
        
        db.commit()
    finally:
        db.close()

# Default users
DEFAULT_USERS = [
    {"username": "testadmin", "password": "adminpass", "is_admin": 1},
    {"username": "testplayer", "password": "playerpass", "is_admin": 0}
]

def initialize_default_users():
    db = SessionLocal()
    try:
        for user in DEFAULT_USERS:
            existing = db.query(Users).filter(Users.username == user["username"]).first()
            
            if not existing:
                password_hash = get_password_hash(user["password"])
                new_user = Users(username=user["username"], password_hash=password_hash, is_admin=user["is_admin"])
                db.add(new_user)
        
        db.commit()
    finally:
        db.close()

# The lifespan context manager runs code before the server fully starts
@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_default_parameters()
    initialize_default_users()
    yield # This tells FastAPI to hand control back to the server

# --- FASTAPI APP ---

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- AUTHENTICATION ENDPOINTS ---

# Registration endpoint - creates a new user with hashed password
@app.post("/auth/register/", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(Users).filter(Users.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    password_hash = get_password_hash(user.password)
    db_user = Users(username=user.username, password_hash=password_hash)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Login endpoint - verifies credentials and returns User ID and JWT token
@app.post("/auth/token", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = db.query(Users).filter(Users.username == form_data.username).first()
    
    if not db_user or not verify_password(form_data.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": db_user.username})
    return {"user_id": db_user.id, "access_token": access_token, "token_type": "bearer", "is_admin": db_user.is_admin}


# --- API ENDPOINTS ---
# All endpoints that modify or access data require authentication and will use the current_user dependency to ensure the user is authenticated.

# Create a new telemetry entry (Access: Everyone)
@app.post("/telemetry/", response_model=TelemetryResponse)
def create_telemetry(telemetry: TelemetryCreate, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    if telemetry.telemetry_type not in ALLOWED_TELEMETRY_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid telemetry_type. Allowed types: {ALLOWED_TELEMETRY_TYPES}")
    db_telemetry = Telemetry(**telemetry.model_dump())
    db.add(db_telemetry)
    db.commit()
    db.refresh(db_telemetry)
    return db_telemetry

# Read telemetry entries with optional filters (Access: Admin)
@app.get("/telemetry/", response_model=list[TelemetryResponse])
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
@app.post("/parameters/", response_model=ParameterResponse)
def create_parameter(parameter: ParameterCreate, db: Session = Depends(get_db), current_user: Users = Depends(get_current_admin_user)):
    existing = db.query(Parameters).filter(Parameters.name == parameter.name).first()
    if existing:
        existing.value = parameter.value # type: ignore (safe to ignore as we checked for existence)
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
@app.get("/parameters/", response_model=list[ParameterResponse])
def read_parameters(parameter_name: str | None = None, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    query = db.query(Parameters)
    if parameter_name is not None:
        query = query.filter(Parameters.name == parameter_name)
    return query.all()

# Create a new balancing rule (Access: Admin)
@app.post("/balancing_rules/", response_model=BalancingRuleResponse)
def create_balancing_rule(rule: BalancingRuleCreate, db: Session = Depends(get_db), current_user: Users = Depends(get_current_admin_user)):
    db_rule = BalancingRule(**rule.model_dump())
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule

# Read balancing rules with optional id filter (Access: Admin)
@app.get("/balancing_rules/", response_model=list[BalancingRuleResponse])
def read_balancing_rules(rule_id: int | None = None, db: Session = Depends(get_db), current_user: Users = Depends(get_current_admin_user)):
    query = db.query(BalancingRule)
    if rule_id is not None:
        query = query.filter(BalancingRule.id == rule_id)
    return query.all()

# Create a new decision log entry (Access: Admin)
@app.post("/decision_logs/", response_model=DecisionLogResponse)
def create_decision_log(entry: DecisionLogCreate, db: Session = Depends(get_db), current_user: Users = Depends(get_current_admin_user)):
    db_entry = DecisionLog(**entry.model_dump())
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry

# Read decision logs with optional filters (Access: Admin)
@app.get("/decision_logs/", response_model=list[DecisionLogResponse])
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