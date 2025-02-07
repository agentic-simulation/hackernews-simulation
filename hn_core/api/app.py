from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from hn_core.simulation import run as simulation

from .model import PostRequest, SimulationRequest

app = FastAPI()


@app.post("/run")
def run(request: PostRequest):
    """endpoint for running simulatio"""
    try:
        profile, result = simulation.run(
            title=request.title,
            url=request.url,
            text=request.text,
            model="gpt-4o-mini",
            num_agents=request.param.num_agents,
            total_time_steps=request.param.total_time_steps,
            batch_size=request.param.batch_size,
            k=request.param.k,
        )

        return JSONResponse(content={"agent_profile": profile, "result": result})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health_check():
    return {"status": "healthy"}
