import os
from pathlib import Path
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .models.schemas import (
    MessageAnalyzeRequest,
    MessageAnalyzeResponse,
    UrlAnalyzeRequest,
    UrlAnalyzeResponse,
    HealthResponse,
)
from .analyzers.message_analyzer import analyze_message_content
from .analyzers.url_analyzer import analyze_url_content

app = FastAPI(
    title="VeriSafe API",
    description="Explainable fraud and phishing analysis platform by Team Shadow Paradox. Detect. Understand. Verify.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _get_frontend_dist() -> Path | None:
    """Find the built React frontend directory across development and production layouts."""
    env_dist = os.environ.get("FRONTEND_DIST")
    candidates = [
        Path(env_dist) if env_dist else None,
        Path.cwd() / "frontend" / "dist",
        Path.cwd() / "dist",
        Path.cwd().parent / "frontend" / "dist",
        Path(__file__).resolve().parent.parent.parent / "frontend" / "dist",
        Path(__file__).resolve().parent.parent / "frontend" / "dist",
        Path("/app/frontend/dist"),
        Path("/app/dist"),
    ]
    for candidate in candidates:
        if candidate and candidate.is_dir() and (candidate / "index.html").is_file():
            return candidate
    return None


# Mount static assets if compiled frontend exists
frontend_dist_path = _get_frontend_dist()
if frontend_dist_path:
    assets_dir = frontend_dist_path / "assets"
    if assets_dir.is_dir():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")


# -------------------------------------------------------------
# Error Handlers
# -------------------------------------------------------------

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    details = []
    messages = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error.get("loc", []) if loc != "body")
        msg = error.get("msg", "Invalid value")
        details.append({"field": field or "payload", "issue": msg})
        messages.append(f"{field}: {msg}" if field else msg)

    summary_message = "; ".join(messages) or "Validation failed for request parameters."
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": summary_message,
                "details": details,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            "detail": summary_message,
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": exc.detail,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            "detail": exc.detail,
        },
    )


# -------------------------------------------------------------
# API Endpoints
# -------------------------------------------------------------

@app.get(
    "/api/health",
    tags=["Health"],
    response_model=HealthResponse,
    summary="Health check endpoint",
)
def health_check():
    """Health check endpoint to verify service readiness."""
    return {
        "status": "ok",
        "service": "VeriSafe API",
        "version": "0.1.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post(
    "/api/messages/analyze",
    tags=["Analysis"],
    response_model=MessageAnalyzeResponse,
    summary="Analyze suspicious message text",
)
def analyze_message_endpoint(payload: MessageAnalyzeRequest):
    return analyze_message_content(payload)


@app.post(
    "/api/urls/analyze",
    tags=["Analysis"],
    response_model=UrlAnalyzeResponse,
    summary="Inspect suspicious URL and domain infrastructure",
)
def analyze_url_endpoint(payload: UrlAnalyzeRequest):
    return analyze_url_content(payload)


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    dist = _get_frontend_dist()
    if dist:
        favicon_path = dist / "favicon.ico"
        if favicon_path.is_file():
            return FileResponse(favicon_path)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# -------------------------------------------------------------
# Frontend UI Routes
# -------------------------------------------------------------

@app.get("/", include_in_schema=False)
async def serve_root():
    """Serves the React frontend index.html if built, otherwise API status."""
    dist = _get_frontend_dist()
    if dist and (dist / "index.html").is_file():
        return FileResponse(dist / "index.html")
    return {
        "message": "Welcome to VeriSafe API - Detect. Understand. Verify.",
        "docs": "/docs",
        "health": "/api/health",
    }


@app.get("/{full_path:path}", include_in_schema=False)
async def serve_spa_fallback(full_path: str):
    """Fallback handler to route client-side SPA navigation and static files."""
    if (
        full_path.startswith("api/")
        or full_path == "api"
        or full_path.startswith("docs")
        or full_path.startswith("redoc")
        or full_path == "openapi.json"
    ):
        raise HTTPException(status_code=404, detail="API endpoint not found")

    dist = _get_frontend_dist()
    if dist:
        requested_file = dist / full_path
        if full_path and requested_file.is_file():
            return FileResponse(requested_file)
        index_file = dist / "index.html"
        if index_file.is_file():
            return FileResponse(index_file)

    raise HTTPException(status_code=404, detail="Page not found")
