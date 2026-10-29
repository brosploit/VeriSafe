from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="VeriSafe API",
    description="Explainable fraud and phishing analysis platform by Team Shadow Paradox. Detect. Understand. Verify.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for local development (e.g. frontend dev server)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
def root():
    """Root endpoint welcoming users and directing to interactive documentation."""
    return {
        "message": "Welcome to VeriSafe API - Detect. Understand. Verify.",
        "docs": "/docs",
        "health": "/api/health",
    }


@app.get("/api/health", tags=["Health"])
def health_check():
    """Health check endpoint to verify service readiness."""
    return {
        "status": "ok",
        "service": "VeriSafe API",
    }

