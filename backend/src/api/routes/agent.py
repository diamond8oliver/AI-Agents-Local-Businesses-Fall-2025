from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from src.agents.smart_agent import answer_question_smart

router = APIRouter(prefix="/agent", tags=["agent"])

class AskRequest(BaseModel):
    question: str
    business_id: str = "4644670e-936f-4688-87ed-b38d0f9a8f47"
    k: int = 5

@router.post("/ask")
async def ask(req: AskRequest, request: Request):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="question is required")
    result = answer_question_smart(req.question, req.business_id, req.k)
    return result
