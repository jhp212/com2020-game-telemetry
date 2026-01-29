import json
from collections import Counter
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates # Jinja2 will be used for templates
# from database.main import 
import requests, os

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

    # Chart 1: Money spent over time (uses nested data.amount)
    money_rows = [t for t in telemetry if t.get("telemetry_type") == "money_spent"]

    money_spent_labels = [t.get("dateTime") for t in money_rows]
    money_spent_values = [t.get("data", {}).get("amount") for t in money_rows]

    # Chart 2: Count of telemetry types
    type_counts = Counter(t.get("telemetry_type") for t in telemetry if t.get("telemetry_type"))
    type_labels = list(type_counts.keys())
    type_values = list(type_counts.values())

    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "title": "Home",
            "money_spent_labels_json": json.dumps(money_spent_labels),
            "money_spent_values_json": json.dumps(money_spent_values),
            "type_labels_json": json.dumps(type_labels),
            "type_values_json": json.dumps(type_values),
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



