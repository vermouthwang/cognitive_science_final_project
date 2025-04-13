import base64
from PIL import Image
import io
from ..models.evaluator import ImageSubmission
from ..services.evaluator_service import EvaluatorService

def test_evaluator():
    # Create evaluator service instance
    evaluator = EvaluatorService()
    
    # Create a simple test image
    img = Image.new('RGB', (100, 100), color='green')
    
    # Convert image to base64
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
    
    # Create submission
    submission = ImageSubmission(
        image=img_base64,
        current_round=1
    )
    
    # Evaluate
    result = evaluator.evaluate_logo(submission)
    
    print("Test Result:")
    print(f"Score: {result.score}")
    print(f"Feedback: {result.feedback}")
    print(f"Hidden Markers: {result.hidden_markers}")

if __name__ == "__main__":
    test_evaluator() 