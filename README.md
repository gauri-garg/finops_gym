# FinOps-Gym-V1: AI-Driven Cloud Cost Optimization

![Python](https://img.shields.io/badge/python-3.10-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-v0.100+-green.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![HuggingFace](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-yellow)

## 🌟 Overview
**FinOps-Gym-V1** is a Reinforcement Learning (RL) environment designed to train and validate AI agents in the art of **Cloud Financial Management (FinOps)**. The environment simulates a cloud infrastructure where an agent must balance **Service Reliability** against **Infrastructure Cost**.

Built by **Gauri Garg (JECRC University)** for the Meta x Scaler OpenEnv Hackathon.

## 🏗️ Project Structure
```text
finops_gym/
├── env/
│   ├── __init__.py
│   ├── engine.py       # Core logic & Reward functions
│   ├── models.py       # Pydantic schemas for API validation
│   └── tasks.py        # Task-specific scoring logic (Meta Validator)
├── test/
│   └── test_api.py     # Integration tests for environment safety
├── Dockerfile          # Containerization for Hugging Face Spaces
├── server/             # FastAPI Server Entry point
│   └── app.py
├── inference.py        # AI Agent (Qwen-2.5-72B) implementation
├── openenv.yaml        # OpenEnv Environment configuration
└── requirements.txt    # Project dependencies

## 🧠 Multi-Node Architecture & Design

```mermaid
graph TD
    A[Inference Agent / Evaluator] -->|REST API - POST /step| B(FastAPI Server)
    B -->|Calls reset/step| C{FinOps Environment Engine}
    C -->|Simulates State| D[(Cloud Resources State)]
    D -->|Returns Observation| C
    C -->|Returns Dict| B
    B -->|Returns JSON| A
```
Our implementation explicitly adopts a **Multi-Node Architecture** by splitting the core simulation logic (`env/engine.py`) from the communication layer (`server/app.py`). 
This guarantees that an AI model can interact over the network asynchronously with the FinOps simulation just as it would with real AWS/GCP cloud APIs, rather than having the Python environment locally injected. The FastAPI server standardizes incoming JSON payloads into tightly typed Pydantic models (like `CloudResource`) ensuring rigorous type-safety across the network boundary.

## 🎯 Task Selection: Zombie Cleanup & Right-Sizing

**The "Why":** Cloud cost explosions rarely happen because of one massive mistake; they happen because of thousands of small, unmanaged resources—"Zombies" (abandoned idle instances) and over-provisioned databases. Resolving these requires an AI that can balance risk (e.g. is this production?) vs reward (cost savings). We chose this domain because it represents the most prominent real-world application of LLM agents acting autonomously in engineering teams today.

## 📊 Evaluation Results

Our reasoning LLM (`Qwen-2.5-72B-Instruct`) achieves optimal results across the environment by utilizing explicit step-by-step Chain of Thought reasoning logic before issuing deployment commands.

| Test Case | Action Taken | Result Status | Reward Accrued | Cost Savings |
|-----------|--------------|---------------|----------------|--------------|
| **Zombie Cleanup** | Terminate `srv-idle-static` | ✅ Success | `+0.416`  | **$0.0416/hr** |
| **Right-sizing** | Resize `db-main` | ✅ Success | `+0.425` | **50% DB cost drop** |
| **Safety Violation** | Prevented Prod kill | ✅ Success | `-5.0` (Penalty) | **$0.00** |


## 🛠️ Installation & Local Testing

### 1. Clone the repository
```bash
git clone [https://github.com/gauri-garg/finops-gym.git]
cd finops_gym

### 2. Install Dependencies
pip install -r requirements.txt

### 3. Run Integration Tests
Set your specific Hugging Face Space URL as an environment variable and run the test suite:

```bash
### Replace with your actual Space URL
export API_BASE_URL="[https://your-username-finops-gym.hf.space]"
python3 test/test_api.py