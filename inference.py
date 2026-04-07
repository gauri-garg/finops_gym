"""
Inference Script for FinOps-Gym-V1
===================================
MANDATORY
- Before submitting, ensure the following variables are defined in your environment configuration:
    API_BASE_URL   The API endpoint for the LLM.
    MODEL_NAME     The model identifier to use for inference.
    HF_TOKEN       Your Hugging Face / API key.
    LOCAL_IMAGE_NAME The name of the local image to use for the environment if you are using from_docker_image()
                     method

- Defaults are set only for API_BASE_URL and MODEL_NAME 
    (and should reflect your active inference setup):
    API_BASE_URL = os.getenv("API_BASE_URL", "<your-active-endpoint>")
    MODEL_NAME = os.getenv("MODEL_NAME", "<your-active-model>")
    
- The inference script must be named `inference.py` and placed in the root directory of the project
- Participants must use OpenAI Client for all LLM calls using above variables

STDOUT FORMAT
- The script must emit exactly three line types to stdout, in this order:

    [START] task=<task_name> env=<benchmark> model=<model_name>
    [STEP]  step=<n> action=<action_str> reward=<0.00> done=<true|false> error=<msg|null>
    [END]   success=<true|false> steps=<n> score=<score> rewards=<r1,r2,...,rn>

  Rules:
    - One [START] line at episode begin.
    - One [STEP] line per step, immediately after env.step() returns.
    - One [END] line after env.close(), always emitted (even on exception).
    - reward and rewards are formatted to 2 decimal places.
    - done and success are lowercase booleans: true or false.
    - error is the raw last_action_error string, or null if none.
    - All fields on a single line with no newlines within a line.
    - Each tasks should return score in (0, 1) strictly.
"""

import asyncio
import os
import json
import textwrap
import traceback
from typing import List, Optional
from openai import OpenAI

# Project imports
from env.engine import FinOpsEnv
from env.models import Action
from env.tasks import get_task_score

# Environment Configuration
API_KEY = os.getenv("HF_TOKEN") or os.getenv("FinOps")
API_BASE_URL = os.getenv("API_BASE_URL") or "https://router.huggingface.co/v1"
MODEL_NAME = os.getenv("MODEL_NAME") or "Qwen/Qwen2.5-72B-Instruct"
TASK_NAME = os.getenv("TASK_ID", "zombie_cleanup")
BENCHMARK = "finops-gym-v1"

MAX_STEPS = 10
SUCCESS_SCORE_THRESHOLD = 0.1

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    # Ensure action string has no newlines for log parsing
    clean_action = str(action).replace("\n", " ").strip()
    print(
        f"[STEP] step={step} action={clean_action} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )

def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in (rewards or [0.0]))
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)

def build_user_prompt(step: int, obs_json: str, last_reward: float, history: List[str]) -> str:
    history_block = "\n".join(history[-3:]) if history else "None"
    return textwrap.dedent(
        f"""
        Step: {step}
        Current Cloud Inventory: {obs_json}
        Last reward: {last_reward:.2f}
        Recent History:
        {history_block}
        
        Instruction: Identify underutilized resources. 
        Terminating idle non-essential resources saves money. 
        Resizing oversized production resources is safer than termination.
        Return a JSON object with "command" (terminate/resize/nop) and "resource_id".
        """
    ).strip()

async def get_model_action(client: OpenAI, step: int, obs_json: str, last_reward: float, history: List[str]) -> str:
    user_prompt = build_user_prompt(step, obs_json, last_reward, history)
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a professional FinOps Manager. You must return valid JSON."},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=150,
        )
        return (completion.choices[0].message.content or "").strip()
    except Exception as exc:
        # Fallback to NOP on failure
        return json.dumps({"command": "nop", "resource_id": "none"})

async def main() -> None:
    # Initialize components
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    env = FinOpsEnv()
    
    history: List[str] = []
    rewards: List[float] = []
    steps_taken = 0
    score = 0.01 # Default strictly positive
    success = False

    log_start(task=TASK_NAME, env=BENCHMARK, model=MODEL_NAME)

    try:
        # Reset environment
        obs = env.reset(task_id=TASK_NAME)
        last_reward = 0.0

        for step in range(1, MAX_STEPS + 1):
            # 1. Get action from model
            action_json = await get_model_action(client, step, obs.model_dump_json(), last_reward, history)
            
            try:
                action_data = json.loads(action_json)
                action_obj = Action(**action_data)
                
                # 2. Execute step
                obs, reward, done, info = env.step(action_obj)
                
                # 3. Log results
                error = None
                log_step(step=step, action=action_json, reward=reward, done=done, error=error)
                
                # 4. Update state
                rewards.append(reward)
                steps_taken = step
                last_reward = reward
                history.append(f"Step {step}: {action_data.get('command')} on {action_data.get('resource_id')} -> {reward:+.2f}")

                if done:
                    break
            except Exception as e:
                log_step(step=step, action=action_json, reward=0.0, done=True, error=str(e).replace('\n', ' '))
                break

        # Final grading using our custom robust grader
        try:
            score = get_task_score(env, TASK_NAME)
        except Exception:
            score = 0.01 # Fallback to valid range

        success = score >= SUCCESS_SCORE_THRESHOLD

    except Exception as e:
        # Unexpected fatal error
        pass
    finally:
        # Ensure [END] is always printed with score in (0, 1)
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)

if __name__ == "__main__":
    asyncio.run(main())