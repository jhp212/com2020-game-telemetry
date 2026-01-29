from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates # Jinja2 will be used for templates
from database.main import *
import requests

# Absolute path of dashboard/app.py
BASE_DIR = Path(__file__).resolve().parent
BASE_URL = "http://127.0.0.1:10101"

# FastAPI app
app = FastAPI()

# Mount static directory containing styling etc...
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

#This is where we connect Jinja2 (Templates)
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


# root page
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    
    return templates.TemplateResponse(
        "base.html",
        {"request": request, "title": "Home"}
    )


# dashboard
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    
    response = requests.get(f"{BASE_URL}/telemetry/")
    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    
    
    # confirm what was received and print status and type if not json
    try:
        telemetry = response.json()
    except ValueError:
        raise HTTPException(
            status_code=500,
            detail=f"Telemetry API did not return JSON. Content-Type={response.headers.get('content-type')} Body starts: {response.text[:200]}"
        )
    
    # populate dict to be returned to the dashboard, accounting for HTTPException
    telemetry_rows = []
    for t in telemetry:
        if not isinstance(t, dict):
            raise HTTPException(status_code=500, detail=f"Expected dict row, got {type(t)}: {t}")
        telemetry_rows.append(
            {
                "dateTime": t.get("dateTime"),
                "user_id": t.get("user_id"),
                "stage_id": t.get("stage_id"),
                "telemetry_type": t.get("telemetry_type"),
                "data": t.get("data"),
            }
        )
        
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "title": "Telemetry Dashboard", "telemetry_rows": telemetry_rows}
    )
    
    
@app.get("/decisionLog", response_class=HTMLResponse)
async def decisionLog(request: Request, db: Session = Depends(get_db)):
    
    response = requests.get(f"{BASE_URL}/decision_logs/")
    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=response.text)
   
    
    try:
        decisionLog = response.json()
    except ValueError:
        raise HTTPException(
            status_code=500,
            detail=f"Telemetry API did not return JSON. Content-Type={response.headers.get('content-type')} Body starts: {response.text[:200]}"
        )
    
    
    
    decision_log_rows = []
    for d in decisionLog:
        if not isinstance(d, dict):
            raise HTTPException(status_code=500, detail=f"Expected dict row, got {type(d)}: {d}")
        
        decision_log_rows.append(
            {
                "dateTime": d.get("dateTime"),
                "id": d.get("id"),
                "parameter_name" : d.get("parameter_name"),
                "stage_id": d.get("stage_id"),
                "change": d.get("change"),
                "rationale": d.get("rationale"),
                "evidence": d.get("evidence")
            }
        )
        
    return templates.TemplateResponse(
        "decision_log.html",
        {"request": request, "title": "Decision Log", "decision_log_rows": decision_log_rows}
    )
    
@app.get("/parameters", response_class=HTMLResponse)
async def parameters(request: Request):
        
    response = requests.get(f"{BASE_URL}/parameters/")
    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=response.text)
   
    
    try:
        parameters = response.json()
    except ValueError:
        raise HTTPException(
            status_code=500,
            detail=f"Telemetry API did not return JSON. Content-Type={response.headers.get('content-type')} Body starts: {response.text[:200]}"
        )
        
        
    parameter_rows = []
    for p in parameters:
        if not isinstance(p, dict):
            raise HTTPException(status_code=500, detail=f"Expected dict row, got {type(p)}: {p}")
        
        parameter_rows.append(
            {
                "name": p.get("name"),
                "value": p.get("value"),
            }
        )
            
    return templates.TemplateResponse(
        "parameters.html",
        {"request": request, "title": "Parameters", "parameter_rows": parameter_rows}
    )



