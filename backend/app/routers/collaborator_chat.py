from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from ..services.collaborator_service import CollaboratorService
from ..services.stable_diffusion_service import StableDiffusionService
import base64
import os

router = APIRouter()
collaborator_service = CollaboratorService()
sd_service = StableDiffusionService()
#TODO: check the whole design of collaborator chat
class ChatMessage(BaseModel):
    message: str
    history: List[Dict[str, str]]

class UploadRequest(BaseModel):
    user_image: Optional[str] = None  # base64 encoded image
    ai_image: Optional[str] = None    # base64 encoded image from previous generation
    chat_history: List[Dict[str, str]]

@router.post("/chat")
async def chat(request: ChatMessage):
    try:
        response = await collaborator_service.chat(request.message, request.history)
        # print(response)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/conclude-round")
async def conclude_round(request: UploadRequest):
    try:
        # Generate modification prompt from chat history
        modification_prompt = await collaborator_service.generate_modification_prompt(
            request.chat_history
        )
        
        # Collect all available reference images
        reference_images = []
        if request.ai_image:
            reference_images.append(request.ai_image)
        # if request.user_image:
        #     reference_images.append(request.user_image)

        # If no reference images, it's the first round #TODO: carefully in the frontend, the user img should came from last round upload result
        if not reference_images:
            initial_logo = await sd_service.generate_initial_logo(
                prompt=modification_prompt,
            )
            return {
                "new_logo": initial_logo,
                "generated_prompt": modification_prompt
            }
         # For testing, hard code a reference image
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        reference_images_address = os.path.join(current_dir, "fakedata", "logo1.png")
        #change to base64
        with open(reference_images_address, "rb") as image_file:
            reference_images.append(base64.b64encode(image_file.read()).decode('utf-8'))
        #TODO: remove the hard code
        modified_logo = await sd_service.modify_logo(
            modification_prompt=modification_prompt,
            reference_images=reference_images
        )
        
        return {
            "new_logo": modified_logo,
            "generated_prompt": modification_prompt
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 