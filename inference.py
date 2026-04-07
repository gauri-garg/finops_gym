import asyncio
import os
import json
import textwrap
from typing import List, Optional
from openai import OpenAI
from env.engine import FinOpsEnv
from env.models import Action

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN") or os.getenv("FinOps") # Check both common names 

LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME") or os.getenv("IMAGE_NAME")

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str] = None) -> None:
    clean_action = str(action).replace("\n", " ").replace("\r", " ").strip()
    error_val = error if error else "null"
    done_val = str(done).lower() # Must be lowercase 
     
    print(f"[STEP] step={step} action={clean_action} reward={reward:.2f} done={done_val} error={error_val}", flush=True)

def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None: 
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    success_val = str(success).lower() 
    
    print(f"[END] success={success_val} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)

async def main():
    if not HF_TOKEN:
        print("[DEBUG] Error: HF_TOKEN secret not found!", flush=True)
        return

    env = FinOpsEnv()
    task_id = os.getenv("TASK_ID", "zombie_cleanup")
    
    log_start(task=task_id, env="finops_gym_v1", model=MODEL_NAME)

    steps_taken, current_rewards, success = 0, [], False

    try:
        obs = env.reset(task_id=task_id)
        client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)
        
        for step in range(1, 11): 
            obs_json = obs.model_dump_json()
            prompt = f"Cloud Inventory: {obs_json}. Task: {task_id}. Choose action."
            
            completion = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "You are a FinOps AI. Output ONLY JSON: {'command': 'terminate', 'resource_id': 'id'}"},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            action_raw = completion.choices[0].message.content
            action_data = json.loads(action_raw)
            
            # Step the environment
            obs, reward, done, info = env.step(Action(**action_data))
            
            current_rewards.append(reward)
            steps_taken = step
            
            log_step(step=step, action=action_raw, reward=reward, done=done)

            if done: 
                break

        from env.tasks import get_task_score
        final_score = get_task_score(env, task_id)
        success = final_score >= 0.1 # Example threshold 
        
        log_end(success=success, steps=steps_taken, score=final_score, rewards=current_rewards)

    except Exception as e:
        print(f"Runtime Error: {e}", flush=True)
        log_end(success=False, steps=steps_taken, score=0.0, rewards=current_rewards)

if __name__ == "__main__":
    asyncio.run(main())