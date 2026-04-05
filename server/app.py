import uvicorn
import argparse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

try:
    from env.engine import FinOpsEnv 
    from env.models import Action, Observation
    from pydantic import BaseModel
except ImportError:
    # Fallback for local testing if needed
    from engine import FinOpsEnv
    from models import Action, Observation
    from pydantic import BaseModel

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

def main():
    parser = argparse.ArgumentParser(description="FinOps Gym Server")
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    
    args = parser.parse_args()
    
    # Start the Uvicorn server using the app object
    uvicorn.run(app, host=args.host, port=args.port)

if __name__ == "__main__":
    main()