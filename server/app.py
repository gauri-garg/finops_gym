from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder 
from env.engine import FinOpsEnv
from env.models import Action
import os

app = FastAPI(title="FinOps-Gym-Validator")
env = FinOpsEnv()

@app.get("/")
def health_check():
    return {"status": "online", "env": "finops_gym", "version": "2026.04.02"}

@app.post("/reset")
async def reset(data: dict = None):
    task_id = (data.get("task_id") if data else "zombie_cleanup") or "zombie_cleanup"
    obs = env.reset(task_id=task_id)
    return jsonable_encoder(obs.model_dump())

@app.post("/step")
async def step(action_data: dict):
    try:
        action = Action(**action_data)
        obs, reward, done, info = env.step(action)
        return jsonable_encoder({
            "observation": obs.model_dump(),
            "reward": float(reward),
            "done": bool(done),
            "info": info
        })
    except Exception as e:
        print(f"[DEBUG] Step Error: {e}") 
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/state")
async def state():
    return jsonable_encoder(env._get_obs("Current state request").model_dump())