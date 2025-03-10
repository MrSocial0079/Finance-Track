from fastapi import APIRouter
import random

router = APIRouter()

rewards = ["$5 Cashback", "10% Discount", "Bonus Points", "Try Again", "Free Coffee"]

@router.get("/spin-wheel")
def spin_wheel():
    reward = random.choice(rewards)
    return {"reward": reward}

challenges = [
    {"challenge": "Save $50 this week", "reward": "Extra 5% Cashback"},
    {"challenge": "Avoid eating out for a week", "reward": "Bonus Points"},
]

@router.get("/challenges")
def get_challenges():
    return challenges