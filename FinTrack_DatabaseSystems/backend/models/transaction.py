from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"

class TransactionCreate(BaseModel):
    amount: float = Field(..., gt=0, description="Transaction amount (must be positive)")
    description: str = Field(..., min_length=1, max_length=200)
    category: str = Field(..., min_length=1, max_length=50)
    date: datetime = Field(default_factory=datetime.now)
    type: TransactionType = Field(..., description="Type of transaction")
    tags: Optional[List[str]] = Field(default=None, description="Optional tags for the transaction")
    notes: Optional[str] = Field(default=None, max_length=500)
    
class Transaction(TransactionCreate):
    id: str
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
