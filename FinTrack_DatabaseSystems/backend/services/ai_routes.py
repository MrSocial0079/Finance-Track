from fastapi import APIRouter
from pydantic import BaseModel
from services.ai_service import ai_service

class PromptRequest(BaseModel):
    prompt: str

router = APIRouter()

@router.post("/ask_gemini")
async def ask_gemini(request: PromptRequest):
    return await ai_service.get_ai_response(request.prompt)

    
@router.get("/ai_tips")
async def get_ai_tips():
    return await ai_service.get_ai_tips()