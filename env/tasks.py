def _extract_resources(env):
    try:
        return getattr(env, 'resources', getattr(env, 'get', {}).get('resources', [])) or []
    except Exception:
        return []

def grader_zombie_cleanup(env=None, action=None, observation=None, **kwargs) -> float:
    try:
        obs = observation or env
        resources = _extract_resources(obs)
        if not resources:
            return 0.50
        zombies = ["srv-idle-static", "storage-temp-logs"]
        remaining_ids = [getattr(r, 'id', r.get('id', '')) if isinstance(r, dict) else r.id for r in resources]
        remaining_zombies = [z for z in zombies if z in remaining_ids]
        if not zombies: return 0.50
        raw_score = ((len(zombies) - len(remaining_zombies)) / len(zombies))
        return float(max(0.01, min(raw_score, 0.99)))
    except Exception:
        return 0.50

def grader_right_sizing(env=None, action=None, observation=None, **kwargs) -> float:
    try:
        obs = observation or env
        resources = _extract_resources(obs)
        if not resources:
            return 0.50
        initial_cost = 1.1336
        current_cost = sum(getattr(r, 'hourly_cost', r.get('hourly_cost', 0)) if isinstance(r, dict) else r.hourly_cost for r in resources)
        savings = max(0, initial_cost - current_cost)
        raw_score = (savings / 0.6)
        if raw_score > 1.0: raw_score = 0.99
        return float(max(0.01, min(raw_score, 0.99)))
    except Exception:
        return 0.50

def grader_disaster_recovery(env=None, action=None, observation=None, **kwargs) -> float:
    try:
        obs = observation or env
        resources = _extract_resources(obs)
        if not resources:
            return 0.50
        essentials_alive = len([r for r in resources if (getattr(r, 'is_essential', r.get('is_essential', False)) if isinstance(r, dict) else r.is_essential)])
        raw_score = (essentials_alive / 2.0)
        return float(max(0.01, min(raw_score, 0.99)))
    except Exception:
        return 0.50

def get_task_score(env, task_id: str = None, **kwargs) -> float:
    tid = (task_id or getattr(env, 'task_id', None) or getattr(getattr(env, '_state', None), 'task_id', None) or 'zombie_cleanup')
    if tid == "right_sizing":
        return grader_right_sizing(env)
    elif tid == "disaster_recovery":
        return grader_disaster_recovery(env)
    else:
        return grader_zombie_cleanup(env)

score = get_task_score
