from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from src.database.supabase_client import get_supabase_client

router = APIRouter(prefix="/product-crawl", tags=["product-crawl"])

class CrawlRequest(BaseModel):
    start_url: str
    max_pages: int = 100
    business_id: str

async def is_product_page(url: str, soup: BeautifulSoup) -> bool:
    """Detect if this is a product page"""
    if '/products/' in url or '/product/' in url:
        return True
    if soup.find('meta', property='og:type', content='product'):
        return True
    return False

async def scrape_shopify_product(url: str) -> Dict:
    """Scrape Shopify product using JSON API"""
    try:
        if '/products/' in url:
            json_url = url.split('?')[0] + '.json'
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(json_url)
                response.raise_for_status()
                data = response.json()
                
                if 'product' not in data:
                    return None
                
                product_data = data['product']
                variants = product_data.get('variants', [])
                
                colors = set()
                sizes = set()
                
                option1_name = product_data.get('options', [{}])[0].get('name', '').lower() if product_data.get('options') else ''
                option2_name = product_data.get('options', [{}])[1].get('name', '').lower() if len(product_data.get('options', [])) > 1 else ''
                
                for variant in variants:
                    opt1 = variant.get('option1')
                    opt2 = variant.get('option2')
                    
                    if opt1:
                        if 'size' in option1_name or any(c.isdigit() for c in str(opt1)):
                            sizes.add(opt1)
                        else:
                            colors.add(opt1)
                    
                    if opt2:
                        if 'size' in option2_name or any(c.isdigit() for c in str(opt2)):
                            sizes.add(opt2)
                        else:
                            colors.add(opt2)
                
                in_stock = any(v.get('available', False) for v in variants)
                
                price = None
                if variants:
                    prices = [float(v['price']) for v in variants if v.get('price')]
                    price = min(prices) if prices else None
                
                images = [img['src'] for img in product_data.get('images', [])[:3]]
                
                return {
                    'url': url,
                    'name': product_data.get('title'),
                    'price': price,
                    'description': product_data.get('body_html', '')[:500] if product_data.get('body_html') else None,
                    'colors': list(colors),
                    'sizes': list(sizes),
                    'in_stock': in_stock,
                    'category': product_data.get('product_type'),
                    'brand': product_data.get('vendor'),
                    'images': images
                }
    except:
        return None

async def crawl_and_extract(start_url: str, max_pages: int, business_id: str) -> Dict:
    """Crawl website and extract products"""
    visited = set()
    to_visit = [start_url]
    products = []
    
    base_domain = urlparse(start_url).netloc
    
    async with httpx.AsyncClient(timeout=30) as client:
        while to_visit and len(visited) < max_pages:
            url = to_visit.pop(0)
            
            if url in visited:
                continue
            
            try:
                response = await client.get(url)
                response.raise_for_status()
                visited.add(url)
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Check if product page
                if await is_product_page(url, soup):
                    product = await scrape_shopify_product(url)
                    if product:
                        product['business_id'] = business_id
                        products.append(product)
                
                # Find more links
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    full_url = urljoin(url, href)
                    
                    if urlparse(full_url).netloc == base_domain and full_url not in visited:
                        to_visit.append(full_url)
            
            except:
                continue
    
    # Save to Supabase
    if products:
        supabase = get_supabase_client()
        supabase.table('products').upsert(products).execute()
    
    return {
        "pages_crawled": len(visited),
        "products_found": len(products)
    }

@router.post("/")
async def crawl_products(req: CrawlRequest, background_tasks: BackgroundTasks):
    """Crawl a website and extract product data"""
    if not req.start_url.startswith("http"):
        raise HTTPException(status_code=400, detail="start_url must start with http/https")
    
    # Run crawl in background
    result = await crawl_and_extract(req.start_url, req.max_pages, req.business_id)
    
    return result
