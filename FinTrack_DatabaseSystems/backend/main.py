from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
from dotenv import load_dotenv
from models.expense import ExpenseCreate, Expense
from models.transaction import TransactionCreate, Transaction
from services.firebase import firebase_service
from services.auth import auth_service
from firebase_admin import auth
from pydantic import BaseModel, EmailStr
from typing import Optional

import requests

API_KEY = "AIzaSyAgAfmEkKUNXxN73E5KtXUNuJEUYK55zM4"

def test_gemini_api_key():
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [
            {"parts": [{"text": "Hello!"}]}
        ]
    }

    response = requests.post(url, headers=headers, json=data)
    if "candidates" in response.json():
        print("Gemini API key is working!")
    else:
        print("Something went wrong:", response.json())

# Call the function
test_gemini_api_key()




# Load environment variables
load_dotenv()

app = FastAPI(title="Fintrack API")

from services.ai_routes import router as ai_routes
app.include_router(ai_routes, prefix="/ai", tags=["ai"])



# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)





class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None

class SigninRequest(BaseModel):
    email: EmailStr
    password: str


@app.post("/auth/signup")
async def signup(request: SignupRequest):
    try:
        user = firebase_service.signup_with_email(
            email=request.email, 
            password=request.password, 
            name=request.name
        )
        return {
            "message": "User created successfully", 
            "uid": user["uid"], 
            "email": user["email"]
            # Don't return token to prevent automatic login
        }
    except ValueError as ve:
        # Handle specific validation errors with 400 status code
        error_msg = str(ve)
        if "Too many sign-up attempts" in error_msg:
            # Rate limiting error
            raise HTTPException(status_code=429, detail=error_msg)
        else:
            # Other validation errors
            raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        # Handle other errors
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/auth/signin")
async def signin(request: SigninRequest):
    try:
        user = firebase_service.signin_with_email(
            email=request.email, 
            password=request.password
        )
        return {
            "message": "Sign in successful", 
            "uid": user["uid"], 
            "email": user["email"],
            "token": user["token"]
        }
    except ValueError as ve:
        # Handle specific validation errors
        error_msg = str(ve)
        if "Too many sign-in attempts" in error_msg:
            # Rate limiting error
            raise HTTPException(status_code=429, detail=error_msg)
        elif "No user found" in error_msg or "Invalid password" in error_msg:
            # Authentication errors
            raise HTTPException(status_code=401, detail=error_msg)
        else:
            # Other validation errors
            raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        # Handle other errors
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/auth/verify-token")
async def verify_token(user_data: dict = Depends(auth_service.verify_token)):
    return user_data

# Email verification routes
class EmailRequest(BaseModel):
    email: EmailStr

@app.post("/auth/request-verification")
async def request_verification(request: EmailRequest):
    try:
        # Get the user by email
        user = auth.get_user_by_email(request.email)
        
        # Get the appropriate redirect URL from config
        redirect_url = config.EmailVerificationConfig.get_redirect_url()
        
        # Configure the action URL for verification
        action_code_settings = auth.ActionCodeSettings(
            url=redirect_url,
            handle_code_in_app=True
        )
        
        # Generate email verification link
        verification_link = auth.generate_email_verification_link(
            request.email,
            action_code_settings
        )
        
        print(f"Email verification link generated for: {request.email}")
        
        # Only show verification link in development mode
        if config.is_development():
            print(f"Verification link: {verification_link}")
            return {
                "verification_link": verification_link, 
                "message": "Verification link generated successfully",
                "mode": "development"
            }
        else:
            print("Verification email sent to user in production mode")
            return {
                "message": "Verification email sent successfully to your email address",
                "mode": "production"
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/auth/check-verification")
async def check_verification(email: str):
    try:
        # Get the user by email
        user = auth.get_user_by_email(email)
        
        # Return the email verification status
        return {"email": email, "email_verified": user.email_verified}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/")
async def root():
    return {"message": "Welcome to Fintrack API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/expenses/")
async def create_expense(expense: ExpenseCreate, user_id: str = Depends(auth_service.verify_token)):
    try:
        result = await firebase_service.add_expense(user_id, expense.model_dump())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/expenses/")
async def get_expenses(user_id: str = Depends(auth_service.verify_token)):
    try:
        expenses = await firebase_service.get_expenses(user_id)
        return expenses
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/insights/")
async def get_insights(user_id: str = Depends(auth_service.verify_token)):
    try:
        expenses = await firebase_service.get_expenses(user_id)
        insights = await ai_service.get_spending_insights(expenses)
        return {"insights": insights}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Transaction endpoints
@app.post("/transactions", response_model=dict)
async def create_transaction(transaction: TransactionCreate, user_id: str = Depends(auth_service.verify_token)):
    try:
        result = await firebase_service.add_transaction(user_id, transaction.model_dump())
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/transactions", response_model=dict)
async def get_transactions(user_id: str = Depends(auth_service.verify_token)):
    try:
        transactions = await firebase_service.get_transactions(user_id)
        return {"status": "success", "data": transactions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/transactions/{transaction_id}", response_model=dict)
async def get_transaction(transaction_id: str, user_id: str = Depends(auth_service.verify_token)):
    try:
        transaction = await firebase_service.get_transaction(transaction_id)
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        if transaction.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this transaction")
        return {"status": "success", "data": transaction}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/transactions/{transaction_id}", response_model=dict)
async def update_transaction(transaction_id: str, transaction: TransactionCreate, user_id: str = Depends(auth_service.verify_token)):
    try:
        # First check if transaction exists and belongs to user
        existing = await firebase_service.get_transaction(transaction_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Transaction not found")
        if existing.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to update this transaction")
            
        # Update the transaction
        result = await firebase_service.update_transaction(transaction_id, transaction.model_dump())
        return {"status": "success", "data": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/transactions/{transaction_id}", response_model=dict)
async def delete_transaction(transaction_id: str, user_id: str = Depends(auth_service.verify_token)):
    try:
        # First check if transaction exists and belongs to user
        existing = await firebase_service.get_transaction(transaction_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Transaction not found")
        if existing.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this transaction")
            
        # Delete the transaction
        result = await firebase_service.delete_transaction(transaction_id)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
