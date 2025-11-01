"""EvalSwipe FastAPI Application."""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routes
from routes import traces, annotations, tags, sessions, prompt_improvement, braintrust, export_data

# Initialize FastAPI app
app = FastAPI(
    title="EvalSwipe API",
    description="API for AI trace review and evaluation",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(traces.router, prefix="/api/traces", tags=["Traces"])
app.include_router(annotations.router, prefix="/api/annotations", tags=["Annotations"])
app.include_router(tags.router, prefix="/api/tags", tags=["Tags"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["Sessions"])
app.include_router(prompt_improvement.router, prefix="/api/prompt-improvement", tags=["Prompt Improvement"])
app.include_router(braintrust.router, prefix="/api/braintrust", tags=["Braintrust"])
app.include_router(export_data.router, prefix="/api/export", tags=["Export"])

# Serve static frontend files
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")


@app.get("/")
async def read_root():
    """Serve the main frontend page."""
    return FileResponse(os.path.join(frontend_path, "index.html"))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": os.getenv("ENV", "development")
    }


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "true").lower() == "true"

    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=debug,
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )
