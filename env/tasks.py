def get_task_score(env, task_id: str) -> float:
    """Returns a score strictly between 0 and 1 for the Meta grader."""
    
    raw_score = 0.01 

    if not hasattr(env, 'resources') or env.resources is None:
        return 0.005 

    # Task 1: Zombie Cleanup (Easy)
    if task_id == "zombie_cleanup":
        remaining_ids = [r.id for r in env.resources]
        zombies = ["srv-idle-static", "storage-temp-logs"]
        remaining_zombies = [z for z in zombies if z in remaining_ids]
        raw_score = ((len(zombies) - len(remaining_zombies)) / len(zombies)) * 0.9

    # Task 2: Right Sizing (Medium)
    elif task_id == "right_sizing":
        initial_cost = 0.4536
        current_cost = sum(r.hourly_cost for r in env.resources)
        savings = max(0, initial_cost - current_cost)
        # FIX: Scaled and capped to stay strictly below 1.0 
        raw_score = (savings / 0.5) * 0.9

    # Task 3: Disaster Recovery (Hard)
    elif task_id == "disaster_recovery":
        essentials_alive = len([r for r in env.resources if r.is_essential])
        raw_score = (essentials_alive / 2.0) * 0.85

    return float(max(0.005, min(raw_score, 0.995)))