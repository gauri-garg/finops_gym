from __future__ import annotations
import uuid
from typing import Tuple, List, Optional, Dict 
from env.models import Observation, Action, CloudResource, State

class FinOpsEnv:
    def __init__(self):
        self.max_steps = 10
        self.resources: List[CloudResource] = []
        self._state = State(episode_id=str(uuid.uuid4()))
        self.reset()

    def reset(self, task_id: str = "zombie_cleanup") -> Observation:
        self._state = State(
            episode_id=str(uuid.uuid4()),
            task_id=task_id,
            step_count=0,
            total_reward=0.0,
            is_done=False
        )
        
        if task_id == "zombie_cleanup":
            # Focus: Idle resources with 0% CPU
            self.resources = [
                CloudResource(id="srv-prod-01", resource_type="compute", size="m5.xlarge", cpu_util=0.85, hourly_cost=0.192, is_essential=True),
                CloudResource(id="srv-idle-static", resource_type="compute", size="t3.medium", cpu_util=0.0, hourly_cost=0.0416, is_essential=False),
                CloudResource(id="storage-temp-logs", resource_type="storage", size="500GB", cpu_util=0.01, hourly_cost=0.05, is_essential=False)
            ]
        elif task_id == "right_sizing":
            # Total cost: 1.1336
            self.resources = [
                CloudResource(id="db-main", resource_type="database", size="db.r5.4xlarge", cpu_util=0.05, hourly_cost=0.4536, is_essential=True),
                CloudResource(id="web-server-oversized", resource_type="compute", size="c5.4xlarge", cpu_util=0.10, hourly_cost=0.68, is_essential=True)
            ]
        elif task_id == "disaster_recovery":
            # Focus: Keeping 'is_essential' alive during a "budget emergency"
            self.resources = [
                CloudResource(id="critical-app-01", resource_type="compute", size="m5.large", cpu_util=0.50, hourly_cost=0.096, is_essential=True),
                CloudResource(id="critical-db-01", resource_type="database", size="db.m5.large", cpu_util=0.40, hourly_cost=0.17, is_essential=True),
                CloudResource(id="non-essential-dev", resource_type="compute", size="t3.nano", cpu_util=0.01, hourly_cost=0.0052, is_essential=False)
            ]
        else:
            # Fallback
            self.resources = [CloudResource(id="default-node", resource_type="compute", size="t3.micro", cpu_util=0.0, hourly_cost=0.01, is_essential=False)]
            
        return self._get_obs(f"Environment reset. Task: {task_id}")

    def step(self, action: Action) -> Tuple[Observation, float, bool, Dict]:
        self._state.step_count += 1
        reward = 0.0
        msg = f"Step {self._state.step_count}: Executed {action.command} on {action.resource_id}"
        
        target_idx = next((i for i, r in enumerate(self.resources) if r.id == action.resource_id), None)
        
        if target_idx is not None:
            resource = self.resources[target_idx]
            
            if action.command == "terminate":
                cost_saved = 0.0
                perf_penalty = 0.0
                if resource.is_essential:
                    perf_penalty = 50.0  # Massive penalty for killing prod
                    msg = f"CRITICAL FAILURE: Terminated essential resource {resource.id}!"
                else:
                    cost_saved = resource.hourly_cost * 10
                    msg = f"SUCCESS: Terminated {resource.id}. Saved ${resource.hourly_cost}/hr."
                    self.resources.pop(target_idx)
                
                reward = (cost_saved * 0.7) - (perf_penalty * 0.3)
            
            elif action.command == "resize":
                if action.new_size and action.new_size != "none":
                    old_cost = resource.hourly_cost
                    resource.hourly_cost *= 0.5 # Simplified cost reduction for resize
                    resource.cpu_util = min(1.0, resource.cpu_util * 2.0)
                    resource.size = action.new_size
                    
                    cost_saved = (old_cost - resource.hourly_cost) * 10
                    perf_penalty = 0.0
                    
                    if resource.cpu_util > 0.95:
                        perf_penalty = 20.0 if resource.service_level_agreement == "99.99%" else 10.0
                        msg = f"WARNING: {resource.id} performance bottleneck (SLA: {resource.service_level_agreement})!"
                    else:
                        msg = f"SUCCESS: {resource.id} right-sized."
                        
                    reward = (cost_saved * 0.7) - (perf_penalty * 0.3)
        
        elif action.command == "nop":
            # Penalty for doing nothing (opportunity cost)
            reward = -0.15 
            msg = "No operation performed."

        self._state.total_reward += reward
        
        # End conditions
        self._state.is_done = self._state.step_count >= self.max_steps or \
                             (self._state.task_id == "zombie_cleanup" and len(self.resources) <= 1)
        
        return self._get_obs(msg), float(reward), self._state.is_done, {}

    def _get_obs(self, log_msg: str) -> Observation:
        total_cost = sum(r.hourly_cost for r in self.resources)
        return Observation(
            resources=list(self.resources),
            total_hourly_cost=round(total_cost, 4),
            budget_limit=1.0,
            logs=[log_msg]
        )

    def state(self) -> State:
        return self._state