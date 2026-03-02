import json
import csv
import io
import zipfile
from collections import Counter # Helpful for graphing
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException, Depends, Response, Form
from fastapi.responses import HTMLResponse, StreamingResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates # Jinja2 will be used for templates
import requests, os
from pydantic import BaseModel # Will be used in POST requests
from datetime import datetime
from simulation.simulator import *
from typing import Optional

# Absolute path of dashboard/app.py
BASE_DIR = Path(__file__).resolve().parent
BASE_URL = os.getenv("API_URL", "http://127.0.0.1:10101")


def api_get_with_token(path: str, token: str) -> requests.Response:
    return requests.get(
        f"{BASE_URL}{path}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )


def api_post_with_token(path: str, token: str, payload: dict) -> requests.Response:
    return requests.post(
        f"{BASE_URL}{path}",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )

# checking any point that needs authentication in order to test the token
def validate_token(token: str) -> bool:
    r = api_get_with_token("/telemetry", token)

    return r.status_code != 401

def get_cookie_token(request: Request) -> str | None:
    return request.cookies.get("access_token")

# returning users should possess a cookie, authenticate the cookie
def require_auth(request: Request) -> str:
    token = get_cookie_token(request)
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    if not validate_token(token):
        raise HTTPException(status_code=401, detail="Invalid/expired token")

    return token

# FastAPI app
app = FastAPI()

# Mount static directory containing styling etc...
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

#This is where we connect Jinja2 (Templates)
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


# root page
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    try:
        token = require_auth(request)
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)
    r = api_get_with_token("/telemetry", token)
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
    
    try:
        token = require_auth(request)
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)
    
   
    response = api_get_with_token("/telemetry", token)
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
    
    # we want to display the newest addition at the top, so reverse format via datetime
    telemetry.sort( key=lambda t: datetime.fromisoformat(t.get("dateTime")), reverse=True)
    
    # populate array with data in JSON format to be returned to the dashboard, accounting for HTTPException
    telemetry_rows = []
    for t in telemetry:
        if not isinstance(t, dict):
            raise HTTPException(status_code=500, detail=f"Expected dict row, got {type(t)}: {t}")
        raw_dt = t.get("dateTime")
        if not raw_dt:
            raise HTTPException(status_code=500, detail=f"Missing dateTime in telemetry entry: {t}")
        formatted_dt = datetime.fromisoformat(raw_dt).strftime("%d %b %Y, %H:%M:%S")
        
        telemetry_rows.append(
            {
                "dateTime": formatted_dt,
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
    
    try:
        token = require_auth(request)
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)
    
    response = api_get_with_token("/decision_logs", token)
    
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
    try:
        token = require_auth(request)
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)
        
    response = api_get_with_token("/parameters", token)
    
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
async def proxy_update_parameter(request: Request, data: ParameterUpdate):
    try:
        token = require_auth(request)
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)

    response = api_post_with_token("/parameters", token, data.model_dump())

    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=f"Database API error: {response.text}")

    return response.json()

class DecisionLogCreate(BaseModel):
    parameter_name: str
    stage_id: int
    change: str
    rationale: str
    evidence: str
    dateTime: datetime

    
@app.post("/decision_logs/")
async def proxy_create_decision_log(request: Request, data: DecisionLogCreate):
    try:
        token = require_auth(request)
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)

    payload = data.model_dump()
    payload["dateTime"] = data.dateTime.isoformat()

    response = api_post_with_token("/decision_logs", token, payload)

    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=f"Database API error: {response.text}")

    return response.json()


@app.get("/dashboard/export/csv")
async def export_dashboard_csv(request: Request):
 
    try:
        token = require_auth(request)
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)

    telemetry_resp = api_get_with_token("/telemetry", token)
    decision_resp = api_get_with_token("/decision_logs", token)
    params_resp = api_get_with_token("/parameters", token)
    
    
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


@app.get("/balancing", response_class=HTMLResponse)
async def dashboard_balancing(request: Request):
    
    try:
        token = require_auth(request)
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)
    
    response = api_get_with_token("/telemetry", token)
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
        
    data_dump = []
    
    for t in telemetry:
        if not isinstance(t, dict):
            raise HTTPException(status_code=500, detail=f"Expected dict row, got {type(t)}: {t}")
        data_dump.append(
            {
                "data": t.get("data")
            }
        )
    
    extracted_data = []
    for d in data_dump:
           extracted_data.append(
               {
                   "stage_start": d.get("data", {}).get("stage_start"),
                   "stage_end": d.get("data", {}).get("stage_end"),
                   "enemy_defeated": d.get("data", {}).get("enemy_defeated"),
                   "damage_taken": d.get("data", {}).get("damage_taken"),
                   "tower_spawn": d.get("data", {}).get("tower_spawn"),
                   "tower_upgrade": d.get("data", {}).get("tower_upgrade"),
                   "money_spent": d.get("data", {}).get("money_spent"),
                   
               }
           )
           
    # initialise total variables
    total_money_spent = 0
    total_enemies_defeated = 0
    total_tower_upgrades = 0
    
    
    
    for item in extracted_data:
        total_money_spent += int(item.get("money_spent"))
        total_enemies_defeated += int(item.get("enemy_defeated"))
        total_tower_upgrades += int(item.get("tower_upgrade"))
        
    
    # calculating the averages of each event 
    n = len(extracted_data)
    average_money_spent = total_money_spent / n
    average_enemies_defeated = total_enemies_defeated / n
    average_tower_upgrades = total_tower_upgrades / n
    
    # Expected value constants
    MONEY_SPENT = 4000
    ENEMIES_DEFEATED = 100
    TOWER_UPGRADES = 10
    
    balancing_response= []
    
    if(average_money_spent > MONEY_SPENT):
        balancing_response.append(
            {
                "balancing_area": "Game Economy",
                "expected_value": str(MONEY_SPENT),
                "actual_value": str(average_money_spent),
                "issue": "Players able to spend more money than expected",
                "balancing_suggestion": "Decrease money given by each defeated enemy"
            }
        )
    if(average_tower_upgrades > TOWER_UPGRADES):
        balancing_response.append(
            {
                "balancing_area": "Upgrades",
                "expected_value": str(TOWER_UPGRADES),
                "actual_value": str(average_tower_upgrades),
                "issue": "Players are able to upgrade their towers too many times resulting in unbalanced level difficulty",
                "balancing_suggestion": "Increase tower upgrade cost"
            }
        )
        
    if(average_enemies_defeated < ENEMIES_DEFEATED):
        balancing_response.append(
            {
                "balancing_area": "Defeating Enemies",
                "expected_value": str(ENEMIES_DEFEATED),
                "actual_value": str(average_enemies_defeated),
                "issue": "Players are struggling to defeat most enemies",
                "balancing_suggestion": "Decrease enemy health"
            }
        )
        
    
        
    
    
    
    return templates.TemplateResponse(
        "balancing.html",
        {"request": request, "title": "Balancing", "balancing_response": balancing_response}
    )
    
    
@app.get("/simulation", response_class=HTMLResponse)
async def getSimulation(request: Request):
  
    return templates.TemplateResponse(
        "simulation.html",
        {"request": request, "title": "Simulation"}
    )
    
class SimulationRequest(BaseModel):
    test_count: int
    level: int    
    
@app.post("/simulation/run")
async def runSimulation(payload: SimulationRequest):
    try:
        result = simulation(
            test_count=payload.test_count,
            level=payload.level
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    
    return [
        {
            "success_rate": result["success_rate"],
            "suggestedAction": result["suggestedAction"]
        }
    ]
    
    
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    token = get_cookie_token(request)
    if token and validate_token(token):
        return RedirectResponse(url="/", status_code=302)

    with open(BASE_DIR / "authentication/login.html", "r") as loginPage:
        return HTMLResponse(content=loginPage.read())


@app.post("/login")
async def login_action(
    username: str = Form(...),
    password: str = Form(...),
    remember: bool = Form(False),
):
    r = requests.post(
        f"{BASE_URL}/auth/token",
        data={"username": username, "password": password},
        timeout=5
    )

    if not r.ok:
        raise HTTPException(status_code=401, detail="The username or password you have entered is incorrect")

    token = r.json().get("access_token")
    if not token:
        raise HTTPException(status_code=500, detail="No token from API")

    response = RedirectResponse(url="/", status_code=302)

   
    max_age = 60 * 60 * 24 if remember else None

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,   # WE WILL SET THIS TO TRUE AT DEPLOYMENT ( HTTPS )
        samesite="lax",
        max_age=max_age,
        path="/"
    )
    
    return response


@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("access_token", path="/")
    return response