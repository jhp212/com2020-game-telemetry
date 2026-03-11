from sqlalchemy import Column, Integer, String, JSON, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database.database import Base # type: ignore

class Telemetry(Base):
    __tablename__ = "Telemetry"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("Users.id", ondelete="CASCADE"), index=True, nullable=False)
    stage_id = Column(Integer, nullable=False)
    telemetry_type = Column(String(30), nullable=False)
    dateTime = Column(DateTime, default=datetime.now, nullable=False)
    data = Column(JSON)
    user = relationship("Users", back_populates="telemetry")
    anomalies = relationship("Anomalies", secondary="TelemetryAnomaly", back_populates="telemetry")

class Parameters(Base):
    __tablename__ = "Parameters"
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
    parameter_name = Column(String(50), ForeignKey("Parameters.name"), nullable=False)
    stage_id = Column(Integer, nullable=True)
    change = Column(String, nullable=False)
    rationale = Column(String, nullable=True)
    evidence = Column(String, nullable=True)
    dateTime = Column(DateTime, default=datetime.now, nullable=False)
    parameter = relationship("Parameters", back_populates="decisions")

class Users(Base):
    __tablename__ = "Users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False, unique=True, index=True)
    password_hash = Column(String(128), nullable=False)
    is_admin = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    is_requesting_admin = Column(Integer, default=0)
    telemetry = relationship("Telemetry", back_populates="user", cascade="all, delete-orphan")

class Anomalies(Base):
    __tablename__ = "Anomalies"
    id = Column(Integer, primary_key=True, index=True)
    anomaly_type = Column(String, nullable=False)
    resolution = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    telemetry = relationship("Telemetry", secondary="TelemetryAnomaly", back_populates="anomalies")

class TelemetryAnomaly(Base):
    __tablename__ = "TelemetryAnomaly"
    telemetry_id = Column(Integer, ForeignKey("Telemetry.id"), primary_key=True)
    anomaly_id = Column(Integer, ForeignKey("Anomalies.id"), primary_key=True)
    telemetry = relationship("Telemetry", viewonly=True)
    anomaly = relationship("Anomalies", viewonly=True)
