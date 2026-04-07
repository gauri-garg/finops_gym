def get_task_score(env, task_id: str) -> float:
    """Returns a score strictly between 0 and 1 for the Meta grader."""
  
    if not hasattr(env, 'resources') or env.resources is None:
        return 0.001

    raw_score = 0.0

    # Task 1: Zombie Cleanup (Easy) 
    if task_id == "zombie_cleanup":
        remaining_ids = [r.id for r in env.resources]
        zombies = ["srv-idle-static", "storage-temp-logs"]
        remaining_zombies = [z for z in zombies if z in remaining_ids]
        raw_score = (len(zombies) - len(remaining_zombies)) / len(zombies)

    # Task 2: Right Sizing (Medium)
    elif task_id == "right_sizing":
        initial_cost = 0.4536
        current_cost = sum(r.hourly_cost for r in env.resources)
        savings = initial_cost - current_cost
        raw_score = savings / 0.1

    # Task 3: Disaster Recovery (Hard) 
    elif task_id == "disaster_recovery":
        essentials = [r for r in env.resources if r.is_essential]
        raw_score = len(essentials) / 2.5 

    return float(max(0.001, min(raw_score, 0.999)))