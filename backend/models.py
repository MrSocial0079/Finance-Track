from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Transaction(BaseModel):
    amount: float
    category: str
    type: str  # "income" or "expense"
    date: Optional[datetime] = datetime.now()