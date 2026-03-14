import json
import csv
import io
import re
import zipfile
from collections import Counter # Helpful for graphing
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException, Depends, Response, Form
from fastapi.responses import HTMLResponse, StreamingResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates # Jinja2 will be used for templates
import requests, os
from pydantic import BaseModel, field_validator # Will be used in POST requests
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
    
def api_delete_with_token(path: str, token: str) -> requests.Response:
    return requests.delete(
        f"{BASE_URL}{path}",
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

    if r.status_code == 403:
        return RedirectResponse(url="/request_admin_page", status_code=302)

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
    
    
    
    # Enemy difficulty heatmap graph
    
    stage_metrics = {}

    for t in telemetry:
        if not isinstance(t, dict):
            continue

        if t.get("telemetry_type") != "stage_end":
            continue

        stage_id = t.get("stage_id")
        data = t.get("data", {})

        if stage_id is None or not isinstance(data, dict):
            continue

        if stage_id not in stage_metrics:
            stage_metrics[stage_id] = {
                "damage_taken": [],
                "enemy_defeated": [],
                "tower_upgrade": [],
                "money_spent": []
            }

        stage_metrics[stage_id]["damage_taken"].append(int(data.get("damage_taken", 0) or 0))
        stage_metrics[stage_id]["enemy_defeated"].append(int(data.get("enemy_defeated", 0) or 0))
        stage_metrics[stage_id]["tower_upgrade"].append(int(data.get("tower_upgrade", 0) or 0))
        stage_metrics[stage_id]["money_spent"].append(int(data.get("money_spent", 0) or 0))

    heatmap_stage_labels = sorted(stage_metrics.keys())
    heatmap_metric_labels = ["Damage Taken", "Enemies Defeated", "Tower Upgrades"]

    heatmap_data = []

    for x_index, stage_id in enumerate(heatmap_stage_labels):
        metrics = stage_metrics[stage_id]

        avg_damage = sum(metrics["damage_taken"]) / len(metrics["damage_taken"]) if metrics["damage_taken"] else 0
        avg_enemies = sum(metrics["enemy_defeated"]) / len(metrics["enemy_defeated"]) if metrics["enemy_defeated"] else 0
        avg_upgrades = sum(metrics["tower_upgrade"]) / len(metrics["tower_upgrade"]) if metrics["tower_upgrade"] else 0

        heatmap_data.append({"x": stage_id, "y": "Damage Taken", "v": round(avg_damage, 2)})
        heatmap_data.append({"x": stage_id, "y": "Enemies Defeated", "v": round(avg_enemies, 2)})
        heatmap_data.append({"x": stage_id, "y": "Tower Upgrades", "v": round(avg_upgrades, 2)})

   
    # Economy chart 
   
    ENEMY_REWARD = 200  

    economy_labels = []
    avg_money_spent_values = []
    est_money_earned_values = []

    for stage_id in heatmap_stage_labels:
        metrics = stage_metrics[stage_id]

        avg_spent = sum(metrics["money_spent"]) / len(metrics["money_spent"]) if metrics["money_spent"] else 0
        avg_enemies = sum(metrics["enemy_defeated"]) / len(metrics["enemy_defeated"]) if metrics["enemy_defeated"] else 0
        est_earned = avg_enemies * ENEMY_REWARD

        economy_labels.append(stage_id)
        avg_money_spent_values.append(round(avg_spent, 2))
        est_money_earned_values.append(round(est_earned, 2))
    
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
            "stage_finished_json": json.dumps(stage_finished_values),
            
            "heatmap_stage_labels_json": json.dumps(heatmap_stage_labels),
            "heatmap_metric_labels_json": json.dumps(heatmap_metric_labels),
            "heatmap_data_json": json.dumps(heatmap_data),

            "economy_labels_json": json.dumps(economy_labels),
            "avg_money_spent_json": json.dumps(avg_money_spent_values),
            "est_money_earned_json": json.dumps(est_money_earned_values)
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
        
    extracted_data = []

    for t in telemetry:
        if not isinstance(t, dict):
            raise HTTPException(status_code=500, detail=f"Expected dict row, got {type(t)}: {t}")

        extracted_data.append(
            {
                "stage_start": t.get("stage_start"),
                "stage_end": t.get("stage_end"),
                "enemy_defeated": t.get("enemy_defeated"),
                "damage_taken": t.get("damage_taken"),
                "tower_spawn": t.get("tower_spawn"),
                "tower_upgrade": t.get("tower_upgrade"),
                "money_spent": t.get("money_spent"),
            }
        )

    total_money_spent = 0
    total_enemies_defeated = 0
    total_tower_upgrades = 0
    stage_count = 0
    total_stage_ends = 0
    total_stage_start = 0.1
    win_ratio = 0
    
    for t in telemetry:
        if not isinstance(t, dict):
            continue
        
        telemetry_type = t.get("telemetry_type")
        data = t.get("data", {})

        if telemetry_type == "stage_end":
            total_stage_ends += 1
            
        if telemetry_type == "stage_start":
            total_stage_start += 1
        
        if telemetry_type != "stage_end":
            continue

        if not isinstance(data, dict):
            continue

        total_money_spent += int(data.get("money_spent", 0) or 0)
        total_enemies_defeated += int(data.get("enemy_defeated", 0) or 0)
        total_tower_upgrades += int(data.get("tower_upgrade", 0) or 0)
        stage_count += 1
        win_ratio = (total_stage_ends / total_stage_start) * 100
        
    if stage_count == 0:
        average_money_spent = 0
        average_enemies_defeated = 0
        average_tower_upgrades = 0
    else:
        average_money_spent = total_money_spent / stage_count
        average_enemies_defeated = total_enemies_defeated / stage_count
        average_tower_upgrades = total_tower_upgrades / stage_count
    
    # Expected value constants
    MONEY_SPENT = 1
    ENEMIES_DEFEATED = 1000
    TOWER_UPGRADES = 1
    
    balancing_response= []
    if win_ratio > 95:
        balancing_response.append(
            {
                "balancing_area": "Win Rate",
                "expected_value": "80-95%",
                "actual_value": str(win_ratio),
                "issue": "Stage is too easy to complete",
                "balancing_suggestion": "Increase damage or health multiplier."
            }
        )
        
    if win_ratio < 80:
        balancing_response.append(
            {
                "balancing_area": "Win Rate",
                "expected_value": "80-95%",
                "actual_value": str(win_ratio),
                "issue": "Stage is too hard to complete",
                "balancing_suggestion": "Decrease damage or health multiplier."
            }
        )
        
    
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
    try:
        token = require_auth(request)
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)
    
    
  
    return templates.TemplateResponse(
        "simulation.html",
        {"request": request, "title": "Simulation"}
    )
    
class SimulationRequest(BaseModel):
    test_difficulty: str
    test_count: int
    level: int    
    
@app.post("/simulation/run")
async def runSimulation(payload: SimulationRequest):
    try:
        result = simulation(
            test_count=payload.test_count,
            level=payload.level,
            difficulty = payload.test_difficulty
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

    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": None},
    )


@app.post("/login")
async def login_action(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    remember: bool = Form(False),
):
    
    
    username = username.strip()

    if not username or not password:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Username and password are required",
            },
            status_code=400,
        )

 
    if len(password) < 6:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Password must be at least 6 characters long",
            },
            status_code=400,
        )

    r = requests.post(
        f"{BASE_URL}/auth/token",
        data={"username": username, "password": password},
        timeout=5
    )

    if not r.ok:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Invalid username or password",
            },
            status_code=401,
        )

    token = r.json().get("access_token")
    if not token:
        raise HTTPException(status_code=500, detail="No token from API")

    response = RedirectResponse(url="/", status_code=302)

    max_age = 60 * 60 * 24 if remember else None

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=max_age,
        path="/",
    )

    return response


@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("access_token", path="/")
    return response




@app.get("/anomalies", response_class=HTMLResponse)
async def anomalies(request: Request):
    try:
        token = require_auth(request)
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)

    response = api_get_with_token("/anomalies", token)
    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    try:
        anomalies = response.json()
    except ValueError:
        raise HTTPException(
            status_code=500,
            detail=f"Anomalies API did not return JSON. Content-Type={response.headers.get('content-type')} Body starts: {response.text[:200]}"
        )

    anomaly_response = []

    for a in anomalies:
        if not isinstance(a, dict):
            raise HTTPException(status_code=500, detail=f"Expected dict row, got {type(a)}: {a}")

        telemetry_ids = a.get("telemetry_ids", [])
        evidence_text = ", ".join(str(tid) for tid in telemetry_ids) if telemetry_ids else "No linked telemetry"

        anomaly_response.append(
            {
                "anomaly_category": a.get("anomaly_type", "Unknown"),
                "reasoning": a.get("resolution", "No resolution provided"),
                "evidence": evidence_text
            }
        )

    return templates.TemplateResponse(
        "anomalies.html",
        {
            "request": request,
            "title": "Anomalies",
            "anomaly_response": anomaly_response
        }
    )
    
    
    
@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    
    token = get_cookie_token(request)
    if token and validate_token(token):
        return RedirectResponse(url="/", status_code=302)

    return templates.TemplateResponse(
        "signup.html",
        {"request": request, "error": None},
    )
    
@app.post("/register")
async def register_action(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    
    username = username.strip()

    if not username or not password:
        return templates.TemplateResponse(
            "signup.html",
            {
                "request": request,
                "error": "All fields are required",
            },
            status_code=400,
        )

    if len(username) < 3 or len(username) > 20:
        return templates.TemplateResponse(
            "signup.html",
            {
                "request": request,
                "error": "Username must be between 3 and 20 characters",
            },
            status_code=400,
        )

    if not all(c.isalnum() or c == "_" for c in username):
        return templates.TemplateResponse(
            "signup.html",
            {
                "request": request,
                "error": "Username can only contain letters, numbers, and underscores",
            },
            status_code=400,
        )

    if len(password) < 8:
        return templates.TemplateResponse(
            "signup.html",
            {
                "request": request,
                "error": "Password must be at least 8 characters long",
            },
            status_code=400,
        )

    if not any(c.isalpha() for c in password):
        return templates.TemplateResponse(
            "signup.html",
            {
                "request": request,
                "error": "Password must contain at least one letter",
            },
            status_code=400,
        )

    if not any(c.isdigit() for c in password):
        return templates.TemplateResponse(
            "signup.html",
            {
                "request": request,
                "error": "Password must contain at least one number",
            },
            status_code=400,
        )

    
    r = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "username": username,
            "password": password
        },
        timeout=5
    )

    if not r.ok:
        if r.status_code == 400:
            return templates.TemplateResponse(
                "signup.html",
                {
                    "request": request,
                    "error": "Username already exists",
                },
                status_code=400,
            )

        return templates.TemplateResponse(
            "signup.html",
            {
                "request": request,
                "error": "Registration failed. Please try again.",
            },
            status_code=r.status_code,
        )

    return RedirectResponse(url="/login", status_code=302)

@app.post("/users/promote/{username}")
async def promote_user(request: Request, username: str):
    try:
        token = require_auth(request)
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)

    response = requests.post(
        f"{BASE_URL}/auth/promote/{username}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )

    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    return RedirectResponse(url="/admin_requests", status_code=302)


@app.get("/users", response_class=HTMLResponse)
async def users_page(request: Request):

    try:
        token = require_auth(request)
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)

    response = api_get_with_token("/users", token)

    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    users = response.json()

    return templates.TemplateResponse(
        "users.html",
        {
            "request": request,
            "title": "Users",
            "users": users
        }
    )

@app.get("/admin_requests", response_class=HTMLResponse)
async def admin_requests(request: Request):

    try:
        token = require_auth(request)
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)

    response = api_get_with_token("/users/admin_requests", token)

    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    requests_list = response.json()

    return templates.TemplateResponse(
        "admin_requests.html",
        {
            "request": request,
            "title": "Admin Requests",
            "requests": requests_list
        }
    )    
    
@app.post("/request_admin")
async def request_admin(request: Request):
    
    try:
        token = require_auth(request)
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)

    response = requests.post(
        f"{BASE_URL}/auth/request_admin",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )

    if not response.ok:
        if response.status_code == 400:
            return templates.TemplateResponse(
                "request_admin.html",
                {
                    "request": request,
                    "title": "Admin Access Required",
                    "message": response.json().get("detail", "Admin request already submitted.")
                },
                status_code=400,
            )
        raise HTTPException(status_code=response.status_code, detail=response.text)

    return templates.TemplateResponse(
        "request_admin.html",
        {
            "request": request,
            "title": "Admin Access Required",
            "message": "Your admin request has been submitted successfully."
        }
    )

@app.get("/request_admin_page", response_class=HTMLResponse)
async def request_admin_page(request: Request):
    try:
        require_auth(request)
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)

    return templates.TemplateResponse(
        "request_admin.html",
        {
            "request": request,
            "title": "Admin Access Required",
            "message": None
        }
    )
    
def detect_anomalies_from_telemetry(telemetry: list[dict]) -> list[dict]:
    
    anomalies = []

    tower_upgrade_counts = {}
    stage_started = set()
    stage_ended = set()
    tower_spawned_by_stage = {}

    for t in telemetry:
        if not isinstance(t, dict):
            continue

        telemetry_id = t.get("id")
        telemetry_type = t.get("telemetry_type")
        stage_id = t.get("stage_id")
        data = t.get("data", {})

        if not isinstance(data, dict):
            data = {}

        if telemetry_type == "stage_start" and stage_id is not None:
            stage_started.add(stage_id)

        if telemetry_type == "stage_end" and stage_id is not None:
            stage_ended.add(stage_id)

        if telemetry_type == "tower_spawn":
            tower_type = data.get("tower_type", "unknown")
            key = (stage_id, tower_type)
            tower_spawned_by_stage.setdefault(key, 0)
            tower_spawned_by_stage[key] += 1

            x = int(data.get("xPos", -1) or -1)
            y = int(data.get("yPos", -1) or -1)

            if x < 0 or y < 0 or x > 15 or y > 15:
                anomalies.append(
                    {
                        "telemetry_ids": [telemetry_id],
                        "anomaly_type": "Invalid Tower Position",
                        "resolution": f"Tower spawned at invalid position ({x}, {y}). Check map boundary validation."
                    }
                )

        if telemetry_type == "tower_upgrade":
            tower_type = data.get("tower_type", "unknown")
            key = (stage_id, tower_type)

            tower_upgrade_counts.setdefault(key, [])
            tower_upgrade_counts[key].append(telemetry_id)

            upgrade_level = int(data.get("upgrade_level", 0) or 0)

            if upgrade_level > 5:
                anomalies.append(
                    {
                        "telemetry_ids": [telemetry_id],
                        "anomaly_type": "Impossible Tower Upgrade Level",
                        "resolution": f"Tower upgrade level {upgrade_level} exceeds the allowed maximum. Check upgrade cap validation."
                    }
                )

            if tower_spawned_by_stage.get(key, 0) == 0:
                anomalies.append(
                    {
                        "telemetry_ids": [telemetry_id],
                        "anomaly_type": "Tower Upgraded Before Spawn",
                        "resolution": f"Tower type '{tower_type}' was upgraded in stage {stage_id} before any spawn event was recorded."
                    }
                )

        if telemetry_type == "damage_taken":
            amount = int(data.get("amount", 0) or 0)

            if amount < 0:
                anomalies.append(
                    {
                        "telemetry_ids": [telemetry_id],
                        "anomaly_type": "Negative Damage Value",
                        "resolution": f"Damage value {amount} is invalid. Check telemetry logging and combat calculations."
                    }
                )

            if amount > 100:
                anomalies.append(
                    {
                        "telemetry_ids": [telemetry_id],
                        "anomaly_type": "Excessive Damage Taken",
                        "resolution": f"Damage value {amount} exceeds the expected upper limit. Check enemy damage balancing."
                    }
                )

        if telemetry_type == "money_spent":
            amount = int(data.get("amount", 0) or 0)

            if amount < 0:
                anomalies.append(
                    {
                        "telemetry_ids": [telemetry_id],
                        "anomaly_type": "Negative Spend Value",
                        "resolution": f"Money spent value {amount} is invalid. Check economy transaction logging."
                    }
                )

            if amount > 10000:
                anomalies.append(
                    {
                        "telemetry_ids": [telemetry_id],
                        "anomaly_type": "Impossible Money Spend",
                        "resolution": f"Money spent value {amount} exceeds the allowed threshold. Check economy validation."
                    }
                )

        if telemetry_type == "enemy_defeated":
            enemy_health = int(data.get("enemy_health", 0) or 0)

            if enemy_health <= 0:
                anomalies.append(
                    {
                        "telemetry_ids": [telemetry_id],
                        "anomaly_type": "Invalid Enemy Health",
                        "resolution": f"Enemy defeated event recorded with health {enemy_health}. Check enemy state logging."
                    }
                )

    for (stage_id, tower_type), telemetry_ids in tower_upgrade_counts.items():
        if len(telemetry_ids) > 5:
            anomalies.append(
                {
                    "telemetry_ids": telemetry_ids,
                    "anomaly_type": "Impossible Tower Upgrade Count",
                    "resolution": f"Tower type '{tower_type}' was upgraded {len(telemetry_ids)} times in stage {stage_id}. Check duplicate upgrade logging or cap enforcement."
                }
            )

    for stage_id in stage_ended:
        if stage_id not in stage_started:
            linked_ids = [
                t.get("id")
                for t in telemetry
                if isinstance(t, dict)
                and t.get("stage_id") == stage_id
                and t.get("telemetry_type") == "stage_end"
                and t.get("id") is not None
            ]

            if linked_ids:
                anomalies.append(
                    {
                        "telemetry_ids": linked_ids,
                        "anomaly_type": "Stage End Without Start",
                        "resolution": f"Stage {stage_id} has a stage_end event without a matching stage_start."
                    }
                )

    results = []
    seen = set()

    for anomaly in anomalies:
        key = (
            anomaly["anomaly_type"],
            tuple(sorted(anomaly["telemetry_ids"]))
        )
        if key not in seen:
            seen.add(key)
            results.append(anomaly)

    return results   


@app.post("/anomalies/run")
async def run_anomaly_detection(request: Request):
    
    try:
        token = require_auth(request)
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)

    telemetry_response = api_get_with_token("/telemetry", token)
    if not telemetry_response.ok:
        raise HTTPException(status_code=telemetry_response.status_code, detail=telemetry_response.text)

    existing_anomalies_response = api_get_with_token("/anomalies", token)
   
    if not existing_anomalies_response.ok:
        raise HTTPException(status_code=existing_anomalies_response.status_code, detail=existing_anomalies_response.text)

    try:
        telemetry = telemetry_response.json()
        existing_anomalies = existing_anomalies_response.json()
    except ValueError:
        raise HTTPException(status_code=500, detail="API did not return valid JSON")


    if not isinstance(telemetry, list):
        raise HTTPException(status_code=500, detail="Expected telemetry list from API")

    detected_anomalies = detect_anomalies_from_telemetry(telemetry)
    existing_keys = set()
    
    
    for a in existing_anomalies:
        if not isinstance(a, dict):
            continue

        anomaly_type = a.get("anomaly_type")
        telemetry_ids = a.get("telemetry_ids", [])

        if isinstance(telemetry_ids, list):
            existing_keys.add((anomaly_type, tuple(sorted(telemetry_ids))))

    for anomaly in detected_anomalies:
        key = (anomaly["anomaly_type"], tuple(sorted(anomaly["telemetry_ids"])))

        if key in existing_keys:
            continue

        post_response = api_post_with_token("/anomalies", token, anomaly)


        if not post_response.ok:
            raise HTTPException(
                status_code=post_response.status_code,
                detail=f"Failed to create anomaly: {post_response.text}"
            )


    return RedirectResponse(url="/anomalies", status_code=302) 

@app.post("/anomalies/clear")
async def clear_anomalies(request: Request):
    try:
        token = require_auth(request)
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)

    response = api_delete_with_token("/anomalies/clear-all", token)

    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    return RedirectResponse(url="/anomalies", status_code=302)