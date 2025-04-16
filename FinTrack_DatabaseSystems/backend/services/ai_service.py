import os
import requests

class AIService:
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.gemini_api_url = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent"

    async def get_ai_tips(self):
        prompt = (
            "Give me 5 actionable, easy-to-understand financial literacy tips for young adults. "
            "Format the answer as a numbered list, each tip concise and practical."
        )
        headers = {"Content-Type": "application/json"}
        params = {"key": self.gemini_api_key}
        data = {
            "contents": [
                {"parts": [{"text": prompt}]}
            ]
        }
        try:
            response = requests.post(self.gemini_api_url, headers=headers, params=params, json=data, timeout=10) 
            response.raise_for_status()
            tips_text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            return {"tips": tips_text}
        except Exception as e:
            return {
                "tips": (
                    "1. Track your expenses and income regularly.\n"
                    "2. Build an emergency fund covering 3-6 months of expenses.\n"
                    "3. Avoid high-interest debt and pay off credit cards monthly.\n"
                    "4. Set short-term and long-term financial goals.\n"
                    "5. Invest early to take advantage of compound interest."
                ),
                "error": str(e)
            }

    async def get_ai_response(self, prompt: str):
        headers = {"Content-Type": "application/json"}
        params = {"key": self.gemini_api_key}
        data = {
            "contents": [
                {"parts": [{"text": prompt}]}
            ]
        }
        try:
            response = requests.post(self.gemini_api_url, headers=headers, params=params, json=data, timeout=30)
            response.raise_for_status()
            answer = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            return {"answer": answer}
        except Exception as e:
            return {"answer": "Sorry, there was an error.", "error": str(e)}

ai_service = AIService()