from fastapi import APIRouter, HTTPException
from src.database.supabase_client import get_supabase_client

router = APIRouter(prefix="/tiers", tags=["tiers"])

@router.get("/list")
async def list_tiers():
    """Get all available pricing tiers"""
    supabase = get_supabase_client()
    result = supabase.table('pricing_tiers').select('*').execute()
    return {"tiers": result.data}

@router.get("/check-limits/{business_id}")
async def check_limits(business_id: str):
    """Check usage limits for a business"""
    supabase = get_supabase_client()
    
    # Get business with tier info
    business = supabase.table('businesses').select('*, pricing_tiers(*)').eq('id', business_id).single().execute()
    
    if not business.data:
        raise HTTPException(status_code=404, detail="Business not found")
    
    tier = business.data.get('pricing_tiers', {})
    
    # Count products
    products = supabase.table('products').select('id', count='exact').eq('business_id', business_id).execute()
    product_count = products.count or 0
    
    # Count conversations this month
    from datetime import datetime, timedelta
    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0).isoformat()
    conversations = supabase.table('conversation_logs').select('id', count='exact').eq('business_id', business_id).gte('timestamp', month_start).execute()
    conversation_count = conversations.count or 0
    
    return {
        "tier_name": tier.get('name', 'Free'),
        "limits": {
            "max_products": tier.get('max_products', 50),
            "max_conversations": tier.get('max_conversations', 100)
        },
        "current_usage": {
            "products": product_count,
            "conversations_this_month": conversation_count
        },
        "limits_exceeded": {
            "products": product_count > tier.get('max_products', 50),
            "conversations": conversation_count > tier.get('max_conversations', 100)
        }
    }
