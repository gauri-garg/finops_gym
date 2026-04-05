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
HF_TOKEN = os.getenv("FinOps") 



def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error={error_val}", flush=True)

def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)

async def main():
    if not HF_TOKEN:
        print("[DEBUG] Error: Secret 'FinOps' not found in environment!")
        return

    env = FinOpsEnv()
    task_id = os.getenv("TASK_ID", "zombie_cleanup")
    log_start(task=task_id, env="finops_gym_v1", model=MODEL_NAME)

    history, rewards = [], []
    steps_taken, score, success = 0, 0.0, False

    try:
        obs = env.reset(task_id=task_id)
        
        client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)
        
        for step in range(1, 11): 
            # Simple conversion for the prompt
            obs_json = obs.model_dump_json()
            prompt = f"Cloud Inventory: {obs_json}. Task: {task_id}. Choose action."
            
            completion = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "You are a Cloud FinOps AI. Output ONLY JSON: {'command': 'terminate', 'resource_id': 'id', 'new_size': 'none'}"},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            action_raw = completion.choices[0].message.content
            action_data = json.loads(action_raw)
            
            obs, reward, done, info = env.step(Action(**action_data))
            
            rewards.append(reward)
            steps_taken = step
            log_step(step=step, action=action_raw.replace("\n", ""), reward=reward, done=done, error=None)

            if done: break

        from env.tasks import get_task_score
        score = get_task_score(env, task_id)
        success = score >= 0.5

    except Exception as e:
        print(f"[DEBUG] Error: {e}")
    finally:
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)

if __name__ == "__main__":
    asyncio.run(main())