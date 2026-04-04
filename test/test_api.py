import requests
import os
# IMPORTANT: Change this to your actual Hugging Face Space URL
BASE_URL = os.getenv("API_BASE_URL", "https://your-space-name.hf.space")

def run_test(name, action_data):
    print(f"\n--- Testing: {name} ---")
    try:
        response = requests.post(f"{BASE_URL}/step", json=action_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Reward: {result['reward']}")
            print(f"📝 Logs: {result['observation']['logs'][-1]}")
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"💥 Connection Error: {e}")

# Reset the Environment
print("🔄 Resetting Environment...")
requests.post(f"{BASE_URL}/reset", json={"task_id": "zombie_cleanup"})

# TEST CASE 1: Terminate a 'Zombie' (Non-essential idle server)
run_test("Terminate Idle Resource", {
    "command": "terminate",
    "resource_id": "srv-idle-static"
})

# TEST CASE 2: Right-size a Resource
run_test("Resize Resource", {
    "command": "resize",
    "resource_id": "db-main",
    "new_size": "db.t3.small"
})

# TEST CASE 3: The "Error" Check (Killing Production)
run_test("Kill Production (Safety Test)", {
    "command": "terminate",
    "resource_id": "srv-prod-01"
})

run_test("Non-Existent Resource", {
    "command": "terminate",
    "resource_id": "srv-ghost-99"
})

run_test("Aggressive Downsizing", {
    "command": "resize",
    "resource_id": "db-main",
    "new_size": "t2.nano" # Extremely small
})

for i in range(3):
    run_test(f"NOP Spam {i+1}", {
        "command": "nop",
        "resource_id": "none"
    })