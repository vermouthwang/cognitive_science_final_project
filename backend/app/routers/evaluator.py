from fastapi import APIRouter, HTTPException
from ..models.evaluator import ImageSubmission, EvaluationResult
from ..services.evaluator_service import EvaluatorService

router = APIRouter()
evaluator_service = EvaluatorService()

@router.post("/evaluate", response_model=EvaluationResult)
async def evaluate_logo(submission: ImageSubmission):
    try:
        result = evaluator_service.evaluate_logo(submission)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 