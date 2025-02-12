from typing import Optional

from pydantic import BaseModel


class SimulationRequest(BaseModel):
    model: str = "gpt-4o-mini"
    num_agents: Optional[int] = None
    total_time_steps: Optional[int] = 24
    batch_size: Optional[int] = 10
    k: Optional[float] = 1.0


class PostRequest(BaseModel):
    title: str
    url: Optional[str] = None
    text: Optional[str] = None
    param: SimulationRequest
