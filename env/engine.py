from __future__ import annotations
import numpy as np
from typing import Tuple, List, Optional, Dict 
from env.models import Observation, Action, CloudResource

class FinOpsEnv:
    def __init__(self):
        self.max_steps = 10
        self.current_step = 0
        self.resources: List[CloudResource] = []
        self.task_id = "zombie_cleanup"
        self.reset()

    def reset(self, task_id: str = "zombie_cleanup") -> Observation:
        self.current_step = 0
        self.task_id = task_id
        
        self.resources = [
            CloudResource(id="srv-prod-01", resource_type="compute", size="m5.xlarge", cpu_util=0.02, hourly_cost=0.192, is_essential=True),
            CloudResource(id="db-main", resource_type="database", size="db.m5.large", cpu_util=0.45, hourly_cost=0.170, is_essential=True),
            CloudResource(id="srv-idle-static", resource_type="compute", size="t3.medium", cpu_util=0.0, hourly_cost=0.0416, is_essential=False),
            CloudResource(id="storage-temp-logs", resource_type="storage", size="500GB", cpu_util=0.01, hourly_cost=0.05, is_essential=False)
        ]
        return self._get_obs(f"Environment reset. Task: {task_id}")

    def step(self, action: Action) -> Tuple[Observation, float, bool, Dict]:
        self.current_step += 1
        reward = 0.0
        msg = f"Step {self.current_step}: Executed {action.command} on {action.resource_id}"
        
        # Find the target resource
        target_idx = next((i for i, r in enumerate(self.resources) if r.id == action.resource_id), None)
        
        if target_idx is not None:
            # Create a local reference so we don't pop the wrong one
            resource = self.resources[target_idx]
            
            if action.command == "terminate":
                if resource.is_essential:
                    reward -= 5.0  # Scaled penalty
                    msg = f"CRITICAL FAILURE: Terminated essential resource {resource.id}!"
                else:
                    # Reward proportional to the money saved
                    reward += (resource.hourly_cost * 10) 
                    msg = f"SUCCESS: Terminated {resource.id}. Saved ${resource.hourly_cost}/hr."
                    self.resources.pop(target_idx)
            
            elif action.command == "resize":
                if action.new_size and action.new_size != "none":
                    old_cost = resource.hourly_cost
                    resource.hourly_cost *= 0.5
                    resource.cpu_util *= 2.0
                    resource.size = action.new_size
                    
                    if resource.cpu_util > 0.95:
                        reward -= 1.0 
                        msg = f"WARNING: {resource.id} performance bottleneck!"
                    else:
                        reward += (old_cost - resource.hourly_cost) * 5
                        msg = f"SUCCESS: {resource.id} right-sized."
        
        elif action.command == "nop":
            reward -= 0.1 
            msg = "No operation performed."

        done = self.current_step >= self.max_steps or len(self.resources) <= 2 # Finish when zombies are gone
        return self._get_obs(msg), float(reward), done, {}

    def _get_obs(self, log_msg: str) -> Observation:
        total_cost = sum(r.hourly_cost for r in self.resources)
        return Observation(
            resources=list(self.resources),
            total_hourly_cost=round(total_cost, 4),
            budget_limit=1.0,
            logs=[log_msg]
        )

    def state(self) -> Observation:
        return self._get_obs("State requested.")