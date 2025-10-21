from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.agents.rag_agent import answer_question


router = APIRouter(prefix="/agent", tags=["agent"])


class AskRequest(BaseModel):
    question: str
    k: int = 5


@router.post("/ask")
async def ask(req: AskRequest, request: Request):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="question is required")
    result = answer_question(req.question, k=req.k)
    return result


