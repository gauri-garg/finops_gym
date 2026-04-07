import asyncio
import os
import json
from openai import OpenAI
from env.engine import FinOpsEnv
from env.models import Action

# Mandatory Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN") or os.getenv("FinOps")

async def main():
    env = FinOpsEnv()
    task_id = os.getenv("TASK_ID", "zombie_cleanup")
    
    print(f"[START] task={task_id} env=finops_gym_v1 model={MODEL_NAME}", flush=True)

    steps_taken, current_rewards = 0, []
    final_score = 0.0

    try:
        obs = env.reset(task_id=task_id)
        client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)
        
        for step in range(1, 11): 
            completion = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": f"Inventory: {obs.model_dump_json()}"}],
                response_format={"type": "json_object"}
            )
            
            action_raw = completion.choices[0].message.content
            action_data = json.loads(action_raw)
            obs, reward, done, info = env.step(Action(**action_data))
            
            current_rewards.append(reward)
            steps_taken = step
            
            # [STEP] Block
            clean_action = action_raw.replace("\n", " ")
            print(f"[STEP] step={step} action={clean_action} reward={reward:.2f} done={str(done).lower()} error=null", flush=True)

            if done: break

        from env.tasks import get_task_score
        final_score = get_task_score(env, task_id)

    except Exception:
        pass
    finally:
        # [END] Block 
        rewards_str = ",".join(f"{r:.2f}" for r in current_rewards)
        success = "true" if final_score >= 0.1 else "false"
        print(f"[END] success={success} steps={steps_taken} score={final_score:.3f} rewards={rewards_str}", flush=True)

if __name__ == "__main__":
    asyncio.run(main())