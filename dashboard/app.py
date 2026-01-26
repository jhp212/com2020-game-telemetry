from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates # Jinja2 will be used for templates
from database.main import *
import random

# Absolute path of dashboard/app.py
BASE_DIR = Path(__file__).resolve().parent


# FastAPI app
app = FastAPI()

# Mount static directory containing styling etc...
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

#This is where we connect Jinja2 (Templates)
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Root page for the dashboard
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    
    raw = (
        db.query(Telemetry).order_by(Telemetry.dateTime.desc()).limit(300).all()
    )
    
    telemetry_rows = []
    for t in raw:
        telemetry_rows.append(
            {
                "dateTime": t.dateTime,
                "user_id": t.user_id,
                "stage_id": t.stage_id,
                "telemetry_type": t.telemetry_type,
                "data": t.data,
            }
        )
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "title": "Telemetry Dashboard", "telemetry_rows": telemetry_rows}
    )
    
    
@app.get("/decisionLog", response_class=HTMLResponse)
async def decisionLog(request: Request, db: Session = Depends(get_db)):
    
    raw = (
        db.query(DecisionLog).order_by(DecisionLog.dateTime.desc()).limit(300).all()
    )
    
    decision_log_rows = []
    for d in raw:
        decision_log_rows.append(
            {
                "dateTime": d.dateTime,
                "id": d.id,
                "parameter_name" : d.parameter_name,
                "stage_id": d.stage_id,
                "change": d.change,
                "rationale": d.rationale,
                "evidence": d.evidence
            }
        )
        
    return templates.TemplateResponse(
        "decision_log.html",
        {"request": request, "title": "Decision Log", "decision_log_rows": decision_log_rows}
    )
    
@app.get("/parameters", response_class=HTMLResponse)
async def parameters(request: Request, db: Session = Depends(get_db)):
        
    raw = (
        db.query(Parameters).limit(300).all()
    )
        
    parameter_rows = []
    for p in raw:
        parameter_rows.append(
            {
                "name": p.name,
                "value": p.value,
            }
        )
            
    return templates.TemplateResponse(
        "parameters.html",
        {"request": request, "title": "Parameters", "decision_log_rows": parameter_rows}
    )



