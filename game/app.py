from fastapi import FastAPI, Request, Response
from fastapi.responses import FileResponse
import mimetypes
import os
import httpx

mimetypes.add_type('application/wasm', '.wasm')

app = FastAPI()

# Backend database API URL (use Docker service name on the compose network)
DATABASE_API_URL = os.getenv("DATABASE_API_URL", "http://database_api:10101")

# Middleware to add security headers
@app.middleware("http")
async def add_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    return response

@app.get("/")
async def root():
    return await serve_file("tower_defense_project.html")

@app.get("/{path:path}")
async def serve_file(path: str):
    path = path or "tower_defense_project.html"
    full = os.path.join("build", path)
    if not os.path.exists(full):
        full = os.path.join("build", "tower_defense_project.html")
    response = FileResponse(full)
    if path.endswith('.wasm') or path.endswith('.side.wasm'):
        response.headers['Content-Type'] = 'application/wasm'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    return response


# Proxy endpoints so the HTML5 client can use same-origin requests
@app.post("/telemetry/")
async def proxy_telemetry(request: Request):
    body = await request.body()
    headers = {"Content-Type": request.headers.get("content-type", "application/json")}
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{DATABASE_API_URL}/telemetry/", content=body, headers=headers)
    return Response(content=resp.content, status_code=resp.status_code, media_type=resp.headers.get("content-type", "application/json"))


@app.get("/parameters/")
async def proxy_parameters(request: Request):
    qs = request.url.query
    url = f"{DATABASE_API_URL}/parameters/"
    if qs:
        url = url + "?" + qs
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
    return Response(content=resp.content, status_code=resp.status_code, media_type=resp.headers.get("content-type", "application/json"))