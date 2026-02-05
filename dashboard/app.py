import json 
from collections import Counter # Helpful for graphing
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates # Jinja2 will be used for templates
import requests, os
from pydantic import BaseModel # Will be used in POST requests
from datetime import datetime

# Absolute path of dashboard/app.py
BASE_DIR = Path(__file__).resolve().parent
BASE_URL = os.getenv("API_URL", "http://127.0.0.1:10101")

# FastAPI app
app = FastAPI()

# Mount static directory containing styling etc...
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

#This is where we connect Jinja2 (Templates)
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


# root page
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    
    r = requests.get(f"{BASE_URL}/telemetry/")
    if not r.ok:
        raise HTTPException(status_code=r.status_code, detail=r.text)

    try:
        telemetry = r.json()
    except ValueError:
        raise HTTPException(
            status_code=500,
            detail=f"Telemetry API did not return JSON. Content-Type={r.headers.get('content-type')} Body starts: {r.text[:200]}"
        )

    

    #Variable definitions to hold y and x axis values
    
    type_counts = Counter(t.get("telemetry_type") for t in telemetry if t.get("telemetry_type"))
    
    type_labels = list(type_counts.keys())
    type_values = list(type_counts.values())
    
    stage_start_counts = Counter(t.get("stage_id") for t in telemetry if t.get("telemetry_type") == "stage_start" and t.get("stage_id") is not None)
    stage_labels = sorted(stage_start_counts.keys(), reverse=True)
    stage_values = [stage_start_counts[k] for k in stage_labels]
    
    stage_start_counts = Counter(t.get("stage_id") for t in telemetry if t.get("telemetry_type") == "stage_start" and t.get("stage_id") is not None)
    stage_end_counts = Counter(t.get("stage_id") for t in telemetry if t.get("telemetry_type") == "stage_end" and t.get("stage_id") is not None)
    stage_ids = sorted(stage_start_counts.keys())
    stage_started_values = [stage_start_counts[s] for s in stage_ids]
    stage_finished_values = [min(stage_start_counts[s], stage_end_counts.get(s, 0)) for s in stage_ids]
    
    
    return templates.TemplateResponse(
        "home.html",
        {
            
            "request": request,
            "title": "Home",
            
            # Returning as JSON so that we can use these through JS scripts.
            "type_labels_json": json.dumps(type_labels),                    
            "type_values_json": json.dumps(type_values),                    
            
            "stage_starts_json": json.dumps(stage_values),
            "stage_labels_json": json.dumps(stage_labels),
            
            "stage_id_labels_json": json.dumps(stage_ids),
            "stage_started_json": json.dumps(stage_started_values),
            "stage_finished_json": json.dumps(stage_finished_values)
        }
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
async def decisionLog(request: Request):
    
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


# A template for expected POST format
class ParameterUpdate(BaseModel):
    name: str
    value: float
      
      
@app.post("/parameters/")
async def proxy_update_parameter(data: ParameterUpdate):
    response = requests.post(
        f"{BASE_URL}/parameters/", 
        json=data.model_dump()
    )

    if not response.ok:
       
        raise HTTPException(
            status_code=response.status_code, 
            detail=f"Database API error: {response.text}"
        )
    return response.json()

class DecisionLogCreate(BaseModel):
    parameter_name: str
    stage_id: int
    change: str
    rationale: str
    evidence: str
    dateTime: datetime
    
@app.post("/decision_logs/")
async def proxy_create_decision_log(data: DecisionLogCreate):
    payload = data.model_dump()

    
    payload["dateTime"] = data.dateTime.isoformat()

    response = requests.post(
        f"{BASE_URL}/decision_logs/",
        json=payload
    )

    if not response.ok:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Database API error: {response.text}"
        )

    return response.json()
