from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Literal

class CloudResource(BaseModel):
    id: str
    resource_type: Literal["compute", "database", "storage"]
    size: str 
    cpu_util: float = Field(..., ge=0.0, le=1.0)
    hourly_cost: float
    is_essential: bool = False

class Action(BaseModel):
    command: Literal["terminate", "resize", "nop"]
    resource_id: str
    new_size: Optional[str] = None 

class Observation(BaseModel):
    resources: List[CloudResource]
    total_hourly_cost: float
    budget_limit: float
    logs: List[str]

    model_config = ConfigDict(from_attributes=True)