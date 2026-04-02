from fastapi import FastAPI, HTTPException
from env.engine import FinOpsEnv
from env.models import Action
import os

# This variable MUST be named 'app' for uvicorn main:app to work
app = FastAPI(title="FinOps-Gym-Validator")
env = FinOpsEnv()

@app.get("/")
def health_check():
    return {"status": "online", "env": "finops_gym"}

@app.post("/reset")
async def reset(data: dict = None):
    task_id = data.get("task_id", "zombie_cleanup") if data else "zombie_cleanup"
    obs = env.reset(task_id=task_id)
    # Using model_dump() for Pydantic V2 compatibility
    return obs.model_dump()

@app.post("/step")
async def step(action_data: dict):
    try:
        action = Action(**action_data)
        obs, reward, done, info = env.step(action)
        return {
            "observation": obs.model_dump(),
            "reward": float(reward),
            "done": bool(done),
            "info": info
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/state")
async def state():
    return env._get_obs("Current state request").model_dump()