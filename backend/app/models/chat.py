from pydantic import BaseModel
from typing import List, Optional, Dict, Union
from fastapi import UploadFile

class MessageContent(BaseModel):
    text: str
    image: Optional[str] = None

class ChatMessage(BaseModel):
    role: str
    content: Union[str, MessageContent]

class ChatRequest(BaseModel):
    message: str
    chat_history: Optional[List[ChatMessage]] = []
    image_base64: Optional[str] = None  # Base64 encoded image string

class ChatResponse(BaseModel):
    response: str
    chat_history: List[ChatMessage]

class CritiqueRequest(BaseModel):
    image_base64: str
    previous_texts: List[str] = [] 