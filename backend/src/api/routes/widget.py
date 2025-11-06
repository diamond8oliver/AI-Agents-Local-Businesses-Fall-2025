from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional
from src.database.supabase_client import get_supabase_client

router = APIRouter(prefix="/widget", tags=["widget"])

class WidgetSettings(BaseModel):
    business_id: str
    primary_color: Optional[str] = "#FF6B35"
    position: Optional[str] = "bottom-right"
    bubble_icon: Optional[str] = "💬"

@router.post("/settings/{business_id}")
async def update_widget_settings(business_id: str, settings: WidgetSettings):
    """Update widget customization settings"""
    supabase = get_supabase_client()
    
    data = {
        'business_id': business_id,
        'primary_color': settings.primary_color,
        'position': settings.position,
        'bubble_icon': settings.bubble_icon
    }
    
    # Upsert settings
    supabase.table('widget_settings').upsert(data).execute()
    return {"status": "updated", "settings": data}

@router.get("/settings/{business_id}")
async def get_widget_settings(business_id: str):
    """Get widget customization settings"""
    supabase = get_supabase_client()
    
    result = supabase.table('widget_settings').select('*').eq('business_id', business_id).execute()
    
    if not result.data:
        # Return defaults
        return {
            "primary_color": "#FF6B35",
            "position": "bottom-right",
            "bubble_icon": "💬"
        }
    
    return result.data[0]

@router.get("/widget.js")
async def get_widget_script():
    """Serve the widget JavaScript file"""
    with open('static/widget.js', 'r') as f:
        content = f.read()
    return Response(content=content, media_type="application/javascript")
