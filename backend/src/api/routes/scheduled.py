from fastapi import APIRouter
from src.database.supabase_client import get_supabase_client
import httpx

router = APIRouter(prefix="/scheduled", tags=["scheduled"])

@router.post("/crawl-all-businesses")
async def crawl_all_businesses():
    """Daily cron job to recrawl all business websites"""
    supabase = get_supabase_client()
    
    # Get all businesses with websites
    businesses = supabase.table('businesses').select('id, website').execute()
    
    results = []
    
    async with httpx.AsyncClient(timeout=300.0) as client:
        for business in businesses.data:
            if business.get('website'):
                try:
                    response = await client.post(
                        "https://web-production-902d.up.railway.app/product-crawl/",
                        json={
                            "start_url": business['website'],
                            "max_pages": 100,
                            "business_id": business['id']
                        }
                    )
                    results.append({
                        "business_id": business['id'],
                        "status": "success",
                        "data": response.json()
                    })
                except Exception as e:
                    results.append({
                        "business_id": business['id'],
                        "status": "error",
                        "error": str(e)
                    })
    
    return {"businesses_crawled": len(results), "results": results}
