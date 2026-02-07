import json
import csv
import io
import zipfile
from collections import Counter # Helpful for graphing
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
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

    # simple error handling
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
    
    # all "******_counts" one liners below simply count every instance of an event per given key such as "stage id" to be displayed as a bar graph
    
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
    
    # populate array with data in JSON format to be returned to the dashboard, accounting for HTTPException
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
    # return to template to be displayed      
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "title": "Telemetry Dashboard", "telemetry_rows": telemetry_rows}
    )
    
    
@app.get("/decisionLog", response_class=HTMLResponse)
async def decisionLog(request: Request):
    
    response = requests.get(f"{BASE_URL}/decision_logs/")
    
    # simple error handling
    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=response.text)
   
    # simple error handling
    try:
        decisionLog = response.json()
    except ValueError:
        raise HTTPException(
            status_code=500,
            detail=f"Telemetry API did not return JSON. Content-Type={response.headers.get('content-type')} Body starts: {response.text[:200]}"
        )
    
    
    # forming an array of decision log data in JSON format to be displayed on the decision log table
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
        
    # return to template to be displayed      
    return templates.TemplateResponse(
        "decision_log.html",
        {"request": request, "title": "Decision Log", "decision_log_rows": decision_log_rows}
    )
    
@app.get("/parameters", response_class=HTMLResponse)
async def parameters(request: Request):
        
    response = requests.get(f"{BASE_URL}/parameters/")
    
    # simple error handling
    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=response.text)
   
    
    # simple error handling
    try:
        parameters = response.json()
    except ValueError:
        raise HTTPException(
            status_code=500,
            detail=f"Telemetry API did not return JSON. Content-Type={response.headers.get('content-type')} Body starts: {response.text[:200]}"
        )
        
    # forming an array of parameter names and values to be displayed
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
    
    #return to template to be displayed        
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
    
    # after making a parameter change we want the change to be displayed on the parameters table by posting it to the DB
    response = requests.post(
        f"{BASE_URL}/parameters/", 
        json=data.model_dump()
    )

    
     # simple error handling
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

    # post the parameter change we made as a json payload to the decision log
    response = requests.post(
        f"{BASE_URL}/decision_logs/",
        json=payload
    )

    
    # simple error handling
    if not response.ok:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Database API error: {response.text}"
        )

    return response.json()


@app.get("/dashboard/export/csv")
async def export_dashboard_csv():
    
    # request data from all datasets
    telemetry_resp = requests.get(f"{BASE_URL}/telemetry/")
    decision_resp = requests.get(f"{BASE_URL}/decision_logs/")
    params_resp = requests.get(f"{BASE_URL}/parameters/")
    
    
    if not telemetry_resp.ok:
        raise HTTPException(status_code=telemetry_resp.status_code, detail=telemetry_resp.text)
    if not decision_resp.ok:
        raise HTTPException(status_code=decision_resp.status_code, detail=decision_resp.text)
    if not params_resp.ok:
        raise HTTPException(status_code=params_resp.status_code, detail=params_resp.text)

    telemetry = telemetry_resp.json()
    decision_logs = decision_resp.json()
    parameters = params_resp.json()
    
    
    # writing to buffer memory instead of real file for better performance
    zip_buffer = io.BytesIO()

    # initialise the zip file inn write mode
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as z:

        # telemetry dashboard
        telemetry_csv = io.StringIO()
        writer = csv.writer(telemetry_csv)
        writer.writerow(["dateTime", "user_id", "stage_id", "telemetry_type", "data"])
        for t in telemetry:
            writer.writerow([
                t.get("dateTime"),
                t.get("user_id"),
                t.get("stage_id"),
                t.get("telemetry_type"),
                t.get("data")
            ])
        z.writestr("telemetry.csv", telemetry_csv.getvalue())

        # decision logs
        decision_csv = io.StringIO()
        writer = csv.writer(decision_csv)
        writer.writerow([
            "dateTime",
            "parameter_name",
            "stage_id",
            "change",
            "rationale",
            "evidence"
        ])
        for d in decision_logs:
            writer.writerow([
                d.get("dateTime"),
                d.get("parameter_name"),
                d.get("stage_id"),
                d.get("change"),
                d.get("rationale"),
                d.get("evidence")
            ])
        z.writestr("decision_logs.csv", decision_csv.getvalue())

        # parameters
        params_csv = io.StringIO()
        writer = csv.writer(params_csv)
        writer.writerow(["name", "value"])
        for p in parameters:
            writer.writerow([
                p.get("name"),
                p.get("value")
            ])
        z.writestr("parameters.csv", params_csv.getvalue())

    # reset cursor back to the start
    zip_buffer.seek(0)



    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": "attachment; filename=telemetry_export.zip"
        }
    )
