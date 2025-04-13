import requests
import base64
import os
from typing import Optional, List
import json
from PIL import Image
import io
import random
import hashlib

class StableDiffusionService:
    def __init__(self):
        self.api_url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
        self.img2img_url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/image-to-image"
        self.api_key = os.getenv("STABILITY_API_KEY")
        self.headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    def _resize_image(self, image_data: bytes) -> bytes:
        """
        Resize image to 1024x1024 while maintaining aspect ratio and padding if necessary
        """
        # Open image from bytes
        image = Image.open(io.BytesIO(image_data))
        
        # Calculate new dimensions while maintaining aspect ratio
        width, height = image.size
        ratio = min(1024/width, 1024/height)
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        
        # Resize image
        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Create new image with white background
        new_image = Image.new("RGB", (1024, 1024), (255, 255, 255))
        
        # Paste resized image in the center
        paste_x = (1024 - new_width) // 2
        paste_y = (1024 - new_height) // 2
        new_image.paste(image, (paste_x, paste_y))
        
        # Convert to bytes
        img_byte_arr = io.BytesIO()
        new_image.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()

    async def generate_initial_logo(self, prompt: str) -> str:
        """
        Generate initial logo based on text prompt
        """
        payload = {
            "text_prompts": [{"text": f"professional logo design: design one single logo with the following instructions: {prompt}", "weight": 1}],
            "cfg_scale": 7,
            "height": 1024,
            "width": 1024,
            "samples": 1,
            "steps": 50,
        }

        response = requests.post(self.api_url, headers=self.headers, json=payload)
        if response.status_code == 200:
            image_data = response.json()["artifacts"][0]["base64"]
            return image_data
        else:
            raise Exception(f"Error generating logo: {response.text}")

    async def modify_logo(self, modification_prompt: str, reference_images: Optional[List[str]] = None) -> str:
        """
        Modify logo using img2img endpoint with the previous AI-generated image
        """
        if not reference_images or not reference_images[0]:
            raise ValueError("Reference image is required for modification")

        try:
            # Clean and pad the base64 string
            base64_str = reference_images[0].strip()
            missing_padding = len(base64_str) % 4
            if missing_padding:
                base64_str += '=' * (4 - missing_padding)

            init_image = base64.b64decode(base64_str)
            
            files = {
                'init_image': ('init_image.png', init_image, 'image/png')
            }
            
            data = {
                'text_prompts[0][text]': f"design one single logo with the following instructions: make the logo main color as blue",
                'text_prompts[0][weight]': '1',
                'image_strength': '0.85',  # Increased from 0.35 to 0.7 to allow more influence from the new prompt
                'cfg_scale': '11',
                'samples': '1',
                'steps': '50',
                'seed': str(random.randint(0, 4294967295)), # Using full 32-bit random seed range
                # Add style preset for more consistent results
                'style_preset': 'digital-art',
            }

            print(f"Sending modification request with prompt: {modification_prompt}")
            response = requests.post(
                self.img2img_url,
                headers=self.headers,
                files=files,
                data=data
            )

            if response.status_code == 200:
                result_base64 = response.json()["artifacts"][0]["base64"]
                print("[DEBUG] Image Hash:", hashlib.md5(result_base64.encode()).hexdigest())
                return response.json()["artifacts"][0]["base64"]
            else:
                print(f"API Error Response: {response.text}")
                raise Exception(f"Error modifying logo: {response.text}")

        except Exception as e:
            print(f"Error in modify_logo: {str(e)}")
            raise