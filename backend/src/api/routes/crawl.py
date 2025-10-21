from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from src.crawlers.web_crawler import crawl_site
from src.agents.knowledge_base import get_chroma_client, get_collection, upsert_documents, query_similar


router = APIRouter(prefix="/crawl", tags=["crawl"])


class CrawlRequest(BaseModel):
    start_url: str
    max_pages: int = 30


@router.post("")
async def crawl(req: CrawlRequest):
    if not req.start_url.startswith("http"):
        raise HTTPException(status_code=400, detail="start_url must start with http/https")
    pages = crawl_site(req.start_url, max_pages=req.max_pages)
    client = get_chroma_client()
    collection = get_collection(client, name="business_kb")
    added = upsert_documents(collection, pages)
    return {"pages_crawled": len(pages), "documents_added": added}


@router.get("/search")
async def search(q: str = Query(..., min_length=2), k: int = 5):
    client = get_chroma_client()
    collection = get_collection(client, name="business_kb")
    results = query_similar(collection, q, k=k)
    return {"results": results}


