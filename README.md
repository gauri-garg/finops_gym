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