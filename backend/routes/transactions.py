from fastapi import APIRouter, Depends, HTTPException
from models import Transaction
from database import get_db
from typing import List

router = APIRouter()

@router.post("/")
def add_transaction(transaction: Transaction):
    db = get_db()
    doc_ref = db.collection("transactions").add(transaction.dict())
    return {"message": "Transaction added", "id": doc_ref[1].id}

@router.get("/", response_model=List[dict])
def get_transactions():
    db = get_db()
    transactions = db.collection("transactions").stream()
    return [{"id": t.id, **t.to_dict()} for t in transactions]

@router.put("/{transaction_id}")
def update_transaction(transaction_id: str, transaction: Transaction):
    db = get_db()
    doc_ref = db.collection("transactions").document(transaction_id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="Transaction not found")
    doc_ref.update(transaction.dict())
    return {"message": "Transaction updated successfully"}

@router.delete("/{transaction_id}")
def delete_transaction(transaction_id: str):
    db = get_db()
    doc_ref = db.collection("transactions").document(transaction_id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="Transaction not found")
    doc_ref.delete()
    return {"message": "Transaction deleted successfully"}