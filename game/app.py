from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
import mimetypes
import os

mimetypes.add_type('application/wasm', '.wasm')

app = FastAPI()

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