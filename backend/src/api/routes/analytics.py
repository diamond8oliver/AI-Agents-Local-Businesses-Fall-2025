from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
from src.database.supabase_client import get_supabase_client

router = APIRouter(prefix="/analytics", tags=["analytics"])

class ConversationLog(BaseModel):
    business_id: str
    question: str
    answer: str
    products_found: int
    timestamp: Optional[datetime] = None

@router.post("/log-conversation")
async def log_conversation(log: ConversationLog):
    """Log a conversation for analytics"""
    supabase = get_supabase_client()
    
    data = {
        'business_id': log.business_id,
        'question': log.question,
        'answer': log.answer,
        'products_found': log.products_found,
        'timestamp': (log.timestamp or datetime.utcnow()).isoformat()
    }
    
    supabase.table('conversation_logs').insert(data).execute()
    return {"status": "logged"}

@router.get("/stats/{business_id}")
async def get_stats(business_id: str):
    """Get analytics stats for a business"""
    supabase = get_supabase_client()
    
    # Total conversations
    total = supabase.table('conversation_logs').select('id', count='exact').eq('business_id', business_id).execute()
    
    # Last 30 days
    thirty_days_ago = (datetime.utcnow() - timedelta(days=30)).isoformat()
    recent = supabase.table('conversation_logs').select('*').eq('business_id', business_id).gte('timestamp', thirty_days_ago).execute()
    
    avg_products = sum(c.get('products_found', 0) for c in recent.data) / len(recent.data) if recent.data else 0
    
    return {
        'total_conversations': total.count or 0,
        'conversations_last_30_days': len(recent.data) if recent.data else 0,
        'avg_products_per_query': round(avg_products, 2)
    }
