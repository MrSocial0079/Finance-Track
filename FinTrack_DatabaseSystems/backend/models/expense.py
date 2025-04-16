from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ExpenseCreate(BaseModel):
    amount: float
    category: str
    description: str
    date: Optional[datetime] = None

class Expense(ExpenseCreate):
    id: str
    user_id: str
    created_at: datetime
