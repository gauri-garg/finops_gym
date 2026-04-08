def _compute_score(env, task_id: str) -> float:
    """Core scoring logic for a given task_id. Returns a float strictly in (0, 1)."""
    resources = getattr(env, 'resources', []) or []
    raw_score = 0.01

    # Task 1: Zombie Cleanup (Easy)
    if task_id == "zombie_cleanup":
        zombies = ["srv-idle-static", "storage-temp-logs"]
        remaining_ids = [r.id for r in resources]
        remaining_zombies = [z for z in zombies if z in remaining_ids]
        raw_score = ((len(zombies) - len(remaining_zombies)) / len(zombies)) * 0.9

    # Task 2: Right Sizing (Medium)
    elif task_id == "right_sizing":
        # Initial cost: 'db-main' (0.4536) + 'web-server-oversized' (0.68) = 1.1336
        initial_cost = 1.1336
        current_cost = sum(r.hourly_cost for r in resources)
        savings = max(0, initial_cost - current_cost)
        # Goal: Save ~60% of the cost (~$0.68 savings)
        raw_score = (savings / 0.6) * 0.9

    # Task 3: Disaster Recovery (Hard)
    elif task_id == "disaster_recovery":
        # Focus: Keeping 'is_essential' alive
        essentials_alive = len([r for r in resources if r.is_essential])
        raw_score = (essentials_alive / 2.0) * 0.85

    return float(max(0.01, min(raw_score, 0.99)))


def get_task_score(env, task_id: str = None, **kwargs) -> float:
    """Shared grader — resolves task_id from argument or environment state."""
    tid = (
        task_id
        or getattr(env, 'task_id', None)
        or getattr(getattr(env, '_state', None), 'task_id', None)
        or 'zombie_cleanup'
    )
    return _compute_score(env, tid)


def grader_zombie_cleanup(env, **kwargs) -> float:
    """Grader for Task 1: Zombie Cleanup. Score strictly in (0, 1)."""
    return _compute_score(env, "zombie_cleanup")


def grader_right_sizing(env, **kwargs) -> float:
    """Grader for Task 2: Right Sizing. Score strictly in (0, 1)."""
    return _compute_score(env, "right_sizing")


def grader_disaster_recovery(env, **kwargs) -> float:
    """Grader for Task 3: Disaster Recovery. Score strictly in (0, 1)."""
    return _compute_score(env, "disaster_recovery")


score = get_task_score