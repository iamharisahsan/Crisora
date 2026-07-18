import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from crisis_service import run_crisis_simulation


class SimulationRequest(BaseModel):
    crisis_type: str = Field(..., min_length=1)
    severity: int = Field(..., ge=1, le=10)


app = FastAPI(title="Crisis Matrix API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "Crisis Matrix API is running.",
        "frontend": "Use the React app in /frontend.",
    }


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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host=os.environ.get("HOST", "0.0.0.0"),
        port=int(os.environ.get("PORT", "8000")),
        reload=True,
    )