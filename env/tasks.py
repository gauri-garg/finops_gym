def get_task_score(env, task_id: str) -> float:
    """Returns a score between 0.0 and 1.0 for the Meta grader."""
    
    if not hasattr(env, 'resources') or env.resources is None:
        return 0.0

    if task_id == "zombie_cleanup":
        remaining_ids = [r.id for r in env.resources]
        zombies = ["srv-idle-static", "storage-temp-logs"]
        remaining_zombies = [z for z in zombies if z in remaining_ids]
        
    
        score = (len(zombies) - len(remaining_zombies)) / len(zombies)
        return float(max(0.0, min(score, 1.0)))

    if task_id == "right_sizing":
        initial_cost = 0.4536
        current_cost = sum(r.hourly_cost for r in env.resources)
        
        savings = initial_cost - current_cost
        score = savings / 0.1
        return float(max(0.0, min(score, 1.0)))

    return 0.0