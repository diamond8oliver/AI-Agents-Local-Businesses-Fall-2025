from typing import Dict, List
from datetime import datetime, timedelta

# Simple in-memory storage (use Redis in production)
conversation_history: Dict[str, List[Dict]] = {}

def get_conversation_history(session_id: str, max_messages: int = 10) -> List[Dict]:
    """Get recent conversation history for a session"""
    if session_id not in conversation_history:
        return []
    
    # Clean old messages (older than 1 hour)
    cutoff = datetime.utcnow() - timedelta(hours=1)
    conversation_history[session_id] = [
        msg for msg in conversation_history[session_id]
        if msg['timestamp'] > cutoff
    ]
    
    return conversation_history[session_id][-max_messages:]

def add_to_history(session_id: str, question: str, answer: str):
    """Add a Q&A pair to conversation history"""
    if session_id not in conversation_history:
        conversation_history[session_id] = []
    
    conversation_history[session_id].append({
        'question': question,
        'answer': answer,
        'timestamp': datetime.utcnow()
    })
