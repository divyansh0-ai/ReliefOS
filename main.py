from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from data import state
from ai_engine import smart_match, generate_impact_forecast, parse_field_report
import random

app = FastAPI(title="ReliefOS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ReportRequest(BaseModel):
    raw_text: str

@app.get("/api/data")
def get_data():
    return {
        "needs": state.needs.to_dict(orient="records") if not state.needs.empty else [],
        "volunteers": state.volunteers.to_dict(orient="records") if not state.volunteers.empty else [],
        "matches": state.matches,
        "impact": state.impact
    }

@app.post("/api/match")
def run_match():
    if state.needs.empty or state.volunteers.empty:
        raise HTTPException(status_code=400, detail="Data not loaded")
    
    matches = smart_match(state.needs, state.volunteers)
    state.matches = matches
    return {"matches": matches}

@app.post("/api/forecast")
def run_forecast():
    if not state.matches:
        raise HTTPException(status_code=400, detail="Must run match first")
    
    impact = generate_impact_forecast(state.needs, state.matches)
    state.impact = impact
    return {"impact": impact}

@app.post("/api/parse_report")
def parse_report(request: ReportRequest):
    result = parse_field_report(request.raw_text)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    from data import SECTOR_COORDS
    sector = result.get("location", "Sector 1")
    coords = SECTOR_COORDS.get(sector, (28.6448, 77.2167))
    
    new_need = {
        "id": state.next_id,
        "location": sector,
        "lat": result.get("lat", coords[0]),
        "lon": result.get("lon", coords[1]),
        "category": result.get("category", "Other"),
        "description": result.get("description", request.raw_text[:80]),
        "urgency_score": result.get("urgency_score", 5),
        "status": "Open",
        "assigned_to": None
    }
    
    new_df = pd.DataFrame([new_need])
    state.needs = pd.concat([state.needs, new_df], ignore_index=True)
    state.next_id += 1
    
    return {"result": result, "need": new_need}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
