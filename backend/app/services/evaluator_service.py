import base64
from PIL import Image
import io
import numpy as np
from ..models.evaluator import ImageSubmission, EvaluationResult, HiddenMarkers
from openai import OpenAI
import os
from dotenv import load_dotenv
import json

class EvaluatorService:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        self.client = OpenAI(api_key=api_key)
        
    SYSTEM_PROMPT = '''You are a rigorous brand logo evaluator with unspoken expectations for café logo submissions. 
    You will assess user-submitted logos based on your personal criteria. Maximum score: 10 points.

    Core Evaluation Standards:
    1. Brand Element Detection (4 points):
       - Must clearly contain: 
         * Coffee-related elements (e.g., beans, cup) 
         * Green/eco-representing elements (e.g., leaves)
       - Abstract representations allowed but must be identifiable within 3 seconds
       - Deduct 2 points for each missing element (0 if both missing)

    2. Style Alignment (3 points):
       - Compared to reference image [EcoLux_logo.jpg] (described as: "two coffee beans forming leaf veins with negative space creating a coffee cup"):
         * Similarity <30% → 0 points
         * 30-50% → 2 points
         * >50% → 3 points

    3. Color Compliance (2 points):
       - Banned colors: Pure black (#000000), Bright orange (#FFA500)
       - Exemplary combinations: Dark green background + gold text (+0.5 bonus)

    4. Creative Flexibility (1 point):
       - Awarded for exceptional originality

    You must respond in the following JSON format:
    {
        "score": float between 0.0-10.0 with 1 decimal,
        "feedback": "1-2 sentence professional critique",
        "hidden_markers": {
            "missing_elements": ["coffee_bean", "leaf"] or [],
            "color_violations": ["#000000", "#FFA500"] or [],
            "similarity_score": float between 0.0-1.0
        }
    }'''

    def evaluate_logo(self, submission: ImageSubmission) -> EvaluationResult:
        # Convert base64 to image for processing
        try:
            image_data = base64.b64decode(submission.image)
            image = Image.open(io.BytesIO(image_data))
            
            # Convert image to RGB mode if it's not
            if image.mode != 'RGB':
                image = image.convert('RGB')
                
            # Save image to temporary buffer for analysis
            img_buffer = io.BytesIO()
            image.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            # Try to load reference image, if not found use a default message
            reference_image_data = None
            reference_image_path = os.path.join(os.path.dirname(__file__), '..', '..', 'reference_images', 'EcoLux_logo.jpg')
            
            if os.path.exists(reference_image_path):
                with open(reference_image_path, 'rb') as f:
                    reference_image_data = f.read()
            
            # Prepare messages for OpenAI
            messages = [
                {
                    "role": "system",
                    "content": self.SYSTEM_PROMPT
                }
            ]
            
            # Add user image
            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64.b64encode(img_buffer.getvalue()).decode('utf-8')}"
                        }
                    }
                ]
            })
            
            # Add reference image if available
            if reference_image_data:
                messages[1]["content"].append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64.b64encode(reference_image_data).decode('utf-8')}"
                    }
                })
                messages[1]["content"].append({
                    "type": "text",
                    "text": "Please evaluate the first logo design (submitted by user) by comparing it with the second image (reference logo). Use the provided criteria to assess the design."
                })
            else:
                messages[1]["content"].append({
                    "type": "text",
                    "text": "Please evaluate the logo design based on the provided criteria. The reference image is not available, so focus on the core design elements and principles."
                })
            
            # Send to OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=1000
            )
            
            # Log the raw response for debugging
            print("OpenAI Response:", response.choices[0].message.content)
            
            try:
                # Parse the response
                result = json.loads(response.choices[0].message.content)
                return EvaluationResult(
                    score=result["score"],
                    feedback=result["feedback"],
                    hidden_markers=HiddenMarkers(**result["hidden_markers"])
                )
            except json.JSONDecodeError as e:
                print(f"JSON Parse Error: {e}")
                print(f"Raw content: {response.choices[0].message.content}")
                # Return a default evaluation if JSON parsing fails
                return EvaluationResult(
                    score=0,
                    feedback="Unable to parse evaluation results. Please try again.",
                    hidden_markers=HiddenMarkers(
                        missing_elements=[],
                        color_violations=[],
                        similarity_score=0.0
                    )
                )
            except KeyError as e:
                print(f"Missing key in response: {e}")
                return self._create_error_result(f"Missing required field in OpenAI response: {str(e)}")
            
        except Exception as e:
            print(f"General error in evaluate_logo: {str(e)}")
            return self._create_error_result(str(e))

    def _create_error_result(self, error_message: str) -> EvaluationResult:
        return EvaluationResult(
            score=0.0,
            feedback=f"Error: {error_message}",
            hidden_markers=HiddenMarkers(
                missing_elements=["error"],
                color_violations=[],
                similarity_score=0.0
            )
        ) 