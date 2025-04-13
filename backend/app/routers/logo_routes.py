from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, validator
from ..services.stable_diffusion_service import StableDiffusionService
from typing import Optional
import base64

router = APIRouter()
sd_service = StableDiffusionService()

class LogoRequest(BaseModel):
    prompt: str

class LogoModificationRequest(BaseModel):
    modification_prompt: str
    reference_image: Optional[str] = None

    @validator('reference_image')
    def validate_base64(cls, v):
        if v is None:
            return v
        try:
            # Remove any whitespace
            v = v.strip()
            
            # Add padding if needed
            missing_padding = len(v) % 4
            if missing_padding:
                v += '=' * (4 - missing_padding)
            
            # Try to decode to verify it's valid base64
            base64.b64decode(v)
            return v
        except Exception as e:
            print(f"Base64 validation error: {str(e)}")
            print(f"String length: {len(v)}")
            print(f"Last 10 characters: {v[-10:] if len(v) >= 10 else v}")
            raise ValueError(f"Invalid base64 string: {str(e)}")

@router.post("/generate-logo")
async def generate_logo(request: LogoRequest):
    try:
        image_data = await sd_service.generate_initial_logo(request.prompt)
        print(len(image_data))
        return {"image": image_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/modify-logo")
async def modify_logo(request: LogoModificationRequest):
    try:
        if request.reference_image:
            print(f"Received base64 length: {len(request.reference_image)}")
            print(f"Last 10 characters: {request.reference_image[-10:]}")
        
        image_data = await sd_service.modify_logo(
            request.modification_prompt,
            [request.reference_image] if request.reference_image else None
        )
        return {"image": image_data}
    except Exception as e:
        print(f"Error in modify_logo: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 