import uvicorn
import argparse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from pydantic import BaseModel

try:
    from env.engine import FinOpsEnv 
    from env.models import Action, Observation, State
    from env.tasks import get_task_score
except ImportError:
    # Fallback for local testing if needed
    from engine import FinOpsEnv
    from models import Action, Observation, State
    from tasks import get_task_score

class ResetRequest(BaseModel):
    task_id: str = "zombie_cleanup"

app = FastAPI(title="FinOps-Gym-V1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the logic
engine = FinOpsEnv()

@app.get("/health")
def health_check():
    return {"status": "healthy", "environment": "finops-gym-v1"}

@app.post("/reset")
def reset(request: Optional[ResetRequest] = None):
    task_id = request.task_id if request else "zombie_cleanup"
    return engine.reset(task_id)

@app.post("/step")
def step(action: Action):
    obs, reward, done, info = engine.step(action)
    return {
        "observation": obs,
        "reward": reward,
        "done": done,
        "info": info
    }

@app.get("/state")
def get_state():
    """Returns the current episode metadata."""
    return engine.state()

@app.post("/score")
def score(request: Optional[ResetRequest] = None):
    """Explicit scoring endpoint for the validator."""
    task_id = request.task_id if request else getattr(engine.state(), 'task_id', 'zombie_cleanup')
    current_score = get_task_score(engine, task_id)
    return {
        "task_id": task_id,
        "score": round(current_score, 4),
        "status": "success"
    }

def main():
    parser = argparse.ArgumentParser(description="FinOps Gym Server")
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    
    args = parser.parse_args()
    
    # Start the Uvicorn server using the app object
    uvicorn.run(app, host=args.host, port=args.port)

if __name__ == "__main__":
    main()