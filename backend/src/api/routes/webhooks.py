from fastapi import APIRouter, BackgroundTasks
import httpx
from src.database.supabase_client import get_supabase_client

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

async def trigger_crawl(business_id: str, website_url: str):
    """Background task to crawl website"""
    async with httpx.AsyncClient(timeout=300.0) as client:
        try:
            await client.post(
                "http://localhost:8000/product-crawl/",
                json={
                    "start_url": website_url,
                    "max_pages": 100,
                    "business_id": business_id
                }
            )
        except Exception as e:
            print(f"Crawl error: {e}")

@router.post("/business-created")
async def business_created(background_tasks: BackgroundTasks, business_id: str, website_url: str):
    """Webhook triggered when a business signs up"""
    supabase = get_supabase_client()
    
    # Log the webhook
    supabase.table('webhook_logs').insert({
        'business_id': business_id,
        'event': 'business_created',
        'status': 'processing'
    }).execute()
    
    # Trigger crawl in background
    background_tasks.add_task(trigger_crawl, business_id, website_url)
    
    return {"status": "crawl_scheduled"}
