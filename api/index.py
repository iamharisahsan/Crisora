from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from crisis_service import run_crisis_simulation


class SimulationRequest(BaseModel):
    crisis_type: str = Field(..., min_length=1)
    severity: int = Field(..., ge=1, le=10)


app = FastAPI(title="Crisora API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

DIST_DIR = Path(__file__).resolve().parents[1] / "frontend" / "dist"
INDEX_FILE = DIST_DIR / "index.html"


@app.get("/api/meta")
def meta():
    return {
        "scenarios": [
            "Data Breach (100k User Records Exposed)",
            "Rogue Executive Tweet Flounders Stock",
            "Critical Cloud Infrastructure Outage",
        ],
        "severity_default": 8,
        "api_ready": True,
    }


@app.post("/api/simulate")
def simulate(request: SimulationRequest):
    try:
        return run_crisis_simulation(request.crisis_type, request.severity)
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unexpected simulation failure: {exc}") from exc


if DIST_DIR.exists():
    assets_dir = DIST_DIR / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")


@app.get("/")
def serve_root():
    if INDEX_FILE.exists():
        response = FileResponse(INDEX_FILE)
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        return response
    return {
        "message": "Frontend build not found.",
        "hint": "Run `cd frontend && npm run build` before deploying.",
    }


@app.get("/{path:path}")
def serve_spa(path: str):
    if path.startswith("api/"):
        raise HTTPException(status_code=404, detail="Not found")
    if INDEX_FILE.exists():
        response = FileResponse(INDEX_FILE)
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        return response
    raise HTTPException(status_code=404, detail="Frontend build not found")