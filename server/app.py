import uvicorn
import argparse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Meta-Standard: Use absolute imports for the package structure
try:
    from env.engine import FinOpsEngine 
    from server.models import FinOpsAction, FinOpsObservation
except ImportError:
    # Fallback for local testing if needed
    from engine import FinOpsEngine
    from models import FinOpsAction, FinOpsObservation

app = FastAPI(title="FinOps-Gym-V1")

# Standard Hackathon Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the logic
engine = FinOpsEngine()

@app.get("/health")
def health_check():
    return {"status": "healthy", "environment": "finops-gym-v1"}

@app.post("/reset")
def reset(agent_id: str):
    return engine.reset(agent_id)

@app.post("/step")
def step(agent_id: str, action: FinOpsAction):
    # This matches the mentor's Pydantic model structure
    return engine.step(agent_id, action)

# --- MENTOR'S MAIN ENTRY POINT ---
def main():
    """
    This is the function the Meta Validator calls via 'serve'.
    It allows the bot to override the port.
    """
    parser = argparse.ArgumentParser(description="FinOps Gym Server")
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    
    args = parser.parse_args()
    
    # Start the Uvicorn server using the app object
    uvicorn.run(app, host=args.host, port=args.port)

if __name__ == "__main__":
    main()