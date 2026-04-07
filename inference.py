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

def log_step(step: int, reward: float) -> None:
    print(f"[STEP] step={step} reward={reward:.2f}", flush=True)

def log_end(task: str, score: float, steps: int) -> None:
    print(f"[END] task={task} score={score:.3f} steps={steps}", flush=True)

async def main():
    if not HF_TOKEN:
        print("[DEBUG] Error: Secret 'FinOps' not found in environment!")
        return

    env = FinOpsEnv()
    task_id = os.getenv("TASK_ID", "zombie_cleanup")
    
    log_start(task=task_id, env="finops_gym_v1", model=MODEL_NAME)

    steps_taken, total_reward = 0, 0.0

    try:
        obs = env.reset(task_id=task_id)
        client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)
        
        for step in range(1, 11): 
            obs_json = obs.model_dump_json()
            prompt = f"Cloud Inventory: {obs_json}. Task: {task_id}. Choose action."
            
            completion = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "You are an advanced Cloud FinOps AI. Optimize cost by terminating idle resources. Output ONLY JSON: {'command': '<terminate|resize|nop>', 'resource_id': '<id>', 'new_size': '<size|none>'}"},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            action_data = json.loads(completion.choices[0].message.content)
            
            obs, reward, done, info = env.step(Action(**action_data))
            
            total_reward += reward
            steps_taken = step
            
            log_step(step=step, reward=reward)

            if done: 
                break

        from env.tasks import get_task_score
        final_score = get_task_score(env, task_id)
        
        log_end(task=task_id, score=final_score, steps=steps_taken)

    except Exception as e:
        print(f"Runtime Error: {e}", flush=True)

if __name__ == "__main__":
    asyncio.run(main())