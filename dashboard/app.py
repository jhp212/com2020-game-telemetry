from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates # Jinja2 will be used for templates
from database.main import *

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
        db.query(Telemetry).order_by(Telemetry.dateTime.desc()).limit(200).all()
    )
    
    telemetry_rows = []
    for t in raw:
        telemetry_rows.append(
            {
                "dateTime": t.dateTime,
                "user_id": t.user_id,
                "stage_id": t.stage_id,
                "telemetry_type": t.telemetry_type
            }
        )
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "title": "Telemetry Dashboard", "telemetry_rows": telemetry_rows}
    )
    


