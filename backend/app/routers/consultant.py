from fastapi import APIRouter, HTTPException
from ..models.chat import ChatRequest, ChatResponse, CritiqueRequest
from ..services.consultant_service import ConsultantService
from typing import List

router = APIRouter()
consultant_service = ConsultantService()

@router.post("/chat", response_model=ChatResponse)
async def chat_with_consultant(request: ChatRequest):
    try:
        response, chat_history = await consultant_service.get_chat_response(
            request.message,
            request.chat_history,
            request.image_base64
        )
        return ChatResponse(response=response, chat_history=chat_history)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/critique")
async def get_critique(request: CritiqueRequest):
    try:
        critique = await consultant_service.critique_latest_image(
            request.image_base64,
            request.previous_texts
        )
        return {"critique": critique}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat")
async def chat_with_consultant(message: str, previous_texts: List[str] = []):
    try:
        response = await consultant_service.chat(message, previous_texts)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))