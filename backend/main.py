from fastapi import FastAPI
from routes import users, transactions, gamification, ai

app = FastAPI(title="Finance Tracker API")

# Include API routes
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
app.include_router(gamification.router, prefix="/gamification", tags=["Gamification"])
app.include_router(ai.router, prefix="/ai", tags=["AI"])

@app.get("/")
def home():
    return {"message": "Welcome to Finance Tracker API!"}