from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime

class ImageSubmission(BaseModel):
    image: str  # Base64 encoded image
    current_round: int

class HiddenMarkers(BaseModel):
    missing_elements: List[str]
    color_violations: List[str]
    similarity_score: float

class EvaluationResult(BaseModel):
    score: float
    feedback: str
    hidden_markers: HiddenMarkers
    timestamp: datetime = datetime.now() 