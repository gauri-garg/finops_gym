def get_task_score(env, task_id: str = None, **kwargs) -> float:
    """Returns a score strictly between 0 and 1 for the Meta grader."""
    
    # Fallback for task_id (if not passed as argument but present in env)
    tid = task_id or getattr(env, 'task_id', 'zombie_cleanup')
    
    raw_score = 0.01 
    resources = getattr(env, 'resources', []) or []

    # Task 1: Zombie Cleanup (Easy)
    if tid == "zombie_cleanup":
        zombies = ["srv-idle-static", "storage-temp-logs"]
        remaining_ids = [r.id for r in resources]
        remaining_zombies = [z for z in zombies if z in remaining_ids]
        raw_score = ((len(zombies) - len(remaining_zombies)) / len(zombies)) * 0.9

    # Task 2: Right Sizing (Medium)
    elif tid == "right_sizing":
        # Sum of: 'db-main' (0.4536) + 'web-server-oversized' (0.68)
        initial_cost = 1.1336 
        current_cost = sum(r.hourly_cost for r in resources)
        savings = max(0, initial_cost - current_cost)
        # Goal: Save ~50% of the cost ($0.5 savings)
        raw_score = (savings / 0.6) * 0.9

    # Task 3: Disaster Recovery (Hard)
    elif tid == "disaster_recovery":
        # Focus: Keeping 'is_essential' alive
        essentials_alive = len([r for r in resources if r.is_essential])
        raw_score = (essentials_alive / 2.0) * 0.85

    # STRICT CLAMPING: Must be strictly between 0 and 1 (exclusive)
    # Using 0.01 as floor and 0.99 as ceiling to be safe
    return float(max(0.01, min(raw_score, 0.99)))

# Alias for possible variations in caller convention
score = get_task_score