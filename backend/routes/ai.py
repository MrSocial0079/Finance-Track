from fastapi import APIRouter
import google.generativeai as genai
import os

router = APIRouter()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

@router.post("/analyze-spending")
def analyze_spending(data: dict):
    transactions = data["transactions"]
    prompt = f"Analyze these transactions and provide financial insights: {transactions}"

    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    
    return {"insights": response.text}