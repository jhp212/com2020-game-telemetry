from fastapi import FastAPI, Request, Response
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import mimetypes
import os
import httpx

mimetypes.add_type('application/wasm', '.wasm')

app = FastAPI()

# Get database API URL from environment variable
API_URL = os.getenv("API_URL", "http://localhost:10101")

# Add CORS middleware for API requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# API proxy endpoints
@app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_api(request: Request, path: str):
    """Proxy API requests to the database service"""
    # Construct the target URL
    target_url = f"{API_URL}/{path}"
    
    # Get query parameters
    if request.url.query:
        target_url = f"{target_url}?{request.url.query}"
    
    # Read the request body if present
    body = await request.body()
    
    # Forward the request to the database API
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=request.method,
                url=target_url,
                content=body if body else None,
                headers={key: value for key, value in request.headers.items() if key.lower() not in ["host", "content-length"]},
            )
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.headers.get("content-type"),
            )
        except Exception as e:
            return Response(
                content=f"Error proxying request: {str(e)}",
                status_code=502,
            )

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