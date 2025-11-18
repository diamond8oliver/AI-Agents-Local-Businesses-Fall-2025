cat > src/api/routes/crawl.py << 'ENDOFFILE'
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
from src.database.supabase_client import get_supabase_client
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import os

router = APIRouter(prefix="/api", tags=["crawl"])

class CrawlRequest(BaseModel):
    url: str

def scrape_with_scrapingbee(url: str, max_products: int = 50):
    products = []
    print(f"=== SCRAPINGBEE SCRAPING: {url} ===", flush=True)
    
    api_key = os.getenv('SCRAPINGBEE_API_KEY')
    if not api_key:
        raise Exception("SCRAPINGBEE_API_KEY not set")
    
    print("Calling ScrapingBee API...", flush=True)
    response = requests.get(
        'https://app.scrapingbee.com/api/v1/',
        params={
            'api_key': api_key,
            'url': url,
            'render_js': 'true',
            'wait': 2000,
        },
        timeout=60
    )
    
    if response.status_code != 200:
        raise Exception(f"ScrapingBee returned status {response.status_code}")
    
    print("✓ Got HTML from ScrapingBee", flush=True)
    
    soup = BeautifulSoup(response.content, 'html.parser')
    page_title = soup.title.string if soup.title else url
    print(f"✓ Page title: {page_title}", flush=True)
    
    product_selectors = [
        'div.product-card',
        'div.product-item',
        'li.product',
        'div.product',
    ]
    
    elements = []
    for selector in product_selectors:
        elements = soup.select(selector)
        if len(elements) > 3:
            print(f"✓ Found {len(elements)} products with: {selector}", flush=True)
            break
    
    if not elements or len(elements) < 3:
        print("✗ No products found", flush=True)
        return [], page_title
    
    for idx, element in enumerate(elements[:max_products]):
        try:
            name = None
            for sel in ['h2', 'h3', '.product-title']:
                name_el = element.select_one(sel)
                if name_el:
                    name = name_el.get_text().strip()
                    if name and 3 < len(name) < 200:
                        break
            
            price = 0.0
            for sel in ['.price', '[class*="price"]']:
                price_el = element.select_one(sel)
                if price_el:
                    price_text = price_el.get_text().strip()
                    numbers = re.findall(r'\d+[.,]?\d*', price_text)
                    if numbers:
                        try:
                            price = float(numbers[0].replace(',', '.'))
                            break
                        except:
                            continue
            
            description = None
            desc_el = element.select_one('.description, p')
            if desc_el:
                description = desc_el.get_text().strip()[:500]
            
            image_url = None
            img_el = element.select_one('img')
            if img_el:
                image_url = img_el.get('src') or img_el.get('data-src')
                if image_url and image_url.startswith('//'):
                    image_url = 'https:' + image_url
                elif image_url and not image_url.startswith('http'):
                    image_url = urljoin(url, image_url)
            
            product_url = url
            link_el = element.select_one('a')
            if link_el:
                href = link_el.get('href')
                if href:
                    if href.startswith('http'):
                        product_url = href
                    elif href.startswith('/'):
                        product_url = urljoin(url, href)
            
            if name and len(name) > 3:
                products.append({
                    'name': name,
                    'price': price,
                    'image_url': image_url,
                    'url': product_url,
                    'description': description or f"Product: {name}",
                })
        
        except Exception as e:
            print(f"Error on product {idx}: {e}", flush=True)
            continue
    
    print(f"✓ Extracted {len(products)} products", flush=True)
    return products, page_title

@router.post("/crawl")
async def crawl_website(req: CrawlRequest):
    print(f"CRAWL REQUEST: {req.url}", flush=True)
    
    try:
        products, page_title = scrape_with_scrapingbee(req.url, 50)
        
        if not products:
            raise HTTPException(status_code=400, detail="No products found")
        
        supabase = get_supabase_client()
        
        business_id = str(uuid.uuid4())
        business_data = {
            'id': business_id,
            'business_name': page_title or req.url,
            'website_url': req.url,
            'created_at': None,
        }
        
        supabase.table('businesses').insert(business_data).execute()
        
        products_to_insert = []
        for product in products:
            products_to_insert.append({
                'id': str(uuid.uuid4()),
                'business_id': business_id,
                'name': product['name'],
                'price': product['price'],
                'description': product['description'],
                'images': [product['image_url']] if product['image_url'] else [],
                'url': product['url'],
                'in_stock': True,
                'created_at': None,
            })
        
        batch_size = 100
        for i in range(0, len(products_to_insert), batch_size):
            batch = products_to_insert[i:i+batch_size]
            supabase.table('products').insert(batch).execute()
        
        print(f"✓ COMPLETE - {len(products)} products", flush=True)
        
        return {
            "status": "success",
            "message": f"Successfully crawled {len(products)} products",
            "business_id": business_id,
            "product_count": len(products)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: {e}", flush=True)
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed: {str(e)}")
ENDOFFILE