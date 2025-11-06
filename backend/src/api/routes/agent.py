from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from src.agents.smart_agent import answer_question_smart
from src.agents.conversation_memory import get_conversation_history, add_to_history
import uuid

router = APIRouter(prefix="/agent", tags=["agent"])

class AskRequest(BaseModel):
    question: str
    business_id: str = "4644670e-936f-4688-87ed-b38d0f9a8f47"
    session_id: Optional[str] = None
    k: int = 5

@router.post("/ask")
async def ask(req: AskRequest, request: Request):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="question is required")
    
    # Generate session ID if not provided
    session_id = req.session_id or str(uuid.uuid4())
    
    # Get conversation history
    history = get_conversation_history(session_id)
    
    # Get answer with memory context
    result = answer_question_smart(req.question, req.business_id, req.k, history)
    
    # Add to history
    add_to_history(session_id, req.question, result['answer'])
    
    # Include session ID in response
    result['session_id'] = session_id
    
    return result
