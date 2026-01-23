from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates # Jinja2 will be used for templates

# Absolute path of dashboard/app.py
BASE_DIR = Path(__file__).resolve().parent


# FastAPI app
app = FastAPI()

# Mount static directory containing styling etc...
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

#This is where we connect Jinja2 (Templates)
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


# Root page for the dashboard
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "title": "Telemetry Dashboard"}
    )
    


