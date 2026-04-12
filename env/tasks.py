from openenv.core.rubrics.base import Rubric

class ZombieCleanupGrader(Rubric):
    def forward(self, action, observation) -> float:
        # Some envs or validators might pass `env` as observation, or a dict, or Pydantic model
        resources = getattr(observation, 'resources', [])
        if not resources and isinstance(observation, dict):
            resources = observation.get('resources', [])
        
        zombies = ["srv-idle-static", "storage-temp-logs"]
        remaining_ids = [getattr(r, 'id', r.get('id', '')) if isinstance(r, dict) else r.id for r in resources]
        remaining_zombies = [z for z in zombies if z in remaining_ids]
        raw_score = ((len(zombies) - len(remaining_zombies)) / len(zombies)) * 0.9
        
        return float(max(0.01, min(raw_score, 0.99)))

class RightSizingGrader(Rubric):
    def forward(self, action, observation) -> float:
        resources = getattr(observation, 'resources', [])
        if not resources and isinstance(observation, dict):
            resources = observation.get('resources', [])
            
        initial_cost = 1.1336
        current_cost = sum(getattr(r, 'hourly_cost', r.get('hourly_cost', 0)) if isinstance(r, dict) else r.hourly_cost for r in resources)
        savings = max(0, initial_cost - current_cost)
        raw_score = (savings / 0.6) * 0.9
        
        return float(max(0.01, min(raw_score, 0.99)))

class DisasterRecoveryGrader(Rubric):
    def forward(self, action, observation) -> float:
        resources = getattr(observation, 'resources', [])
        if not resources and isinstance(observation, dict):
            resources = observation.get('resources', [])
            
        essentials_alive = len([r for r in resources if (getattr(r, 'is_essential', r.get('is_essential', False)) if isinstance(r, dict) else r.is_essential)])
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
    
    if tid == "right_sizing":
        return RightSizingGrader()(None, env)
    elif tid == "disaster_recovery":
        return DisasterRecoveryGrader()(None, env)
    else:
        return ZombieCleanupGrader()(None, env)

# Compatibility aliases
grader_zombie_cleanup = ZombieCleanupGrader()
grader_right_sizing = RightSizingGrader()
grader_disaster_recovery = DisasterRecoveryGrader()
score = get_task_score