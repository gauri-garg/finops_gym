import sys
import os
# Add parent directory to path to reach env module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from env.engine import FinOpsEnv
from env.tasks import (
    get_task_score,
    grader_zombie_cleanup,
    grader_right_sizing,
    grader_disaster_recovery,
)

# Map task_id -> dedicated grader (as the validator will call them)
TASK_GRADERS = {
    "zombie_cleanup":    grader_zombie_cleanup,
    "right_sizing":      grader_right_sizing,
    "disaster_recovery": grader_disaster_recovery,
}

def test_grader_range():
    env = FinOpsEnv()

    print("\n--- Verifying Per-Task Grader Scores (Strict Range Check) ---")

    for tid, grader_fn in TASK_GRADERS.items():
        # Reset env to the task
        env.reset(task_id=tid)

        # --- 1. Initial state ---
        initial_score = grader_fn(env=env)
        ok = 0.0 < initial_score < 1.0
        print(f"Task: {tid:20} | Initial Score: {initial_score:.4f} | OK: {ok}")
        assert ok, f"Initial score {initial_score} out of range for {tid}"

        # --- 2. "Perfect" state ---
        env.reset(task_id=tid)  # fresh reset before modifying
        if tid == "zombie_cleanup":
            env.resources = [r for r in env.resources if r.id == "srv-prod-01"]
        elif tid == "right_sizing":
            for r in env.resources:
                r.hourly_cost *= 0.1  
        elif tid == "disaster_recovery":
            pass                        

        perfect_score = grader_fn(env=env)
        ok = 0.0 < perfect_score < 1.0
        print(f"Task: {tid:20} | Perfect Score: {perfect_score:.4f} | OK: {ok}")
        assert ok, f"Perfect score {perfect_score} out of range for {tid}"

        # --- 3. "Failed" state (empty env) ---
        env.resources = []
        failed_score = grader_fn(env=env)
        ok = 0.0 < failed_score < 1.0
        print(f"Task: {tid:20} | Failed Score:  {failed_score:.4f} | OK: {ok}")
        assert ok, f"Failed score {failed_score} out of range for {tid}"

        # --- 4. Shared grader resolves task_id from env._state ---
        env.reset(task_id=tid)
        shared_score = get_task_score(env) 
        ok = 0.0 < shared_score < 1.0
        print(f"Task: {tid:20} | Shared Grader: {shared_score:.4f} | OK: {ok}")
        assert ok, f"Shared grader score {shared_score} out of range for {tid}"

        print("-" * 65)

    print("\n✅ All grader checks passed! Scores are strictly between 0 and 1.")


if __name__ == "__main__":
    try:
        test_grader_range()
    except Exception as e:
        print(f"\n❌ Verification failed: {e}")
        sys.exit(1)
