import sys
import os
# Add parent directory to path to reach env module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from env.engine import FinOpsEnv
from env.tasks import get_task_score

def test_grader_range():
    env = FinOpsEnv()
    tasks = ["zombie_cleanup", "right_sizing", "disaster_recovery"]
    
    print("\n--- Verifying Grader Scores (Strict Range Check) ---")
    
    for tid in tasks:
        # Reset env to the task
        env.reset(task_id=tid)
        
        # Test initial state score
        initial_score = get_task_score(env, tid)
        print(f"Task: {tid:20} | Initial Score: {initial_score:.4f} | OK: {0.0 < initial_score < 1.0}")
        assert 0.0 < initial_score < 1.0, f"Initial score {initial_score} out of range for {tid}"
        
        # Test "perfect" state score (simulated)
        if tid == "zombie_cleanup":
            env.resources = [r for r in env.resources if r.id == "srv-prod-01"] # Terminated zombies
        elif tid == "right_sizing":
            for r in env.resources:
                r.hourly_cost *= 0.1 # Massive savings
        elif tid == "disaster_recovery":
            # Keep essentials alive
            pass
            
        perfect_score = get_task_score(env, tid)
        print(f"Task: {tid:20} | Perfect Score: {perfect_score:.4f} | OK: {0.0 < perfect_score < 1.0}")
        assert 0.0 < perfect_score < 1.0, f"Perfect score {perfect_score} out of range for {tid}"

        # Test "failed" state score
        env.resources = [] # Everything dead
        failed_score = get_task_score(env, tid)
        print(f"Task: {tid:20} | Failed Score:  {failed_score:.4f} | OK: {0.0 < failed_score < 1.0}")
        assert 0.0 < failed_score < 1.0, f"Failed score {failed_score} out of range for {tid}"
        print("-" * 60)

    print("\n✅ All grader checks passed! Scores are strictly between 0 and 1.")

if __name__ == "__main__":
    try:
        test_grader_range()
    except Exception as e:
        print(f"\n❌ Verification failed: {e}")
        sys.exit(1)
