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
    """
    Scrape products using ScrapingBee API
    Returns: list of {name, price, image_url, url, description}
    """
    products = []
    
    print(f"=== SCRAPINGBEE SCRAPING: {url} ===", flush=True)
    
    # Get API key from environment
    api_key = os.getenv('SCRAPINGBEE_API_KEY')
    if not api_key:
        raise Exception("SCRAPINGBEE_API_KEY not set in environment")
    
    # Call ScrapingBee API
    print("Calling ScrapingBee API...", flush=True)
    response = requests.get(
        'https://app.scrapingbee.com/api/v1/',
        params={
            'api_key': api_key,
            'url': url,
            'render_js': 'true',  # Render JavaScript
            'wait': 2000,  # Wait 2 seconds for content to load
        },
        timeout=60
    )
    
    if response.status_code != 200:
        raise Exception(f"ScrapingBee returned status {response.status_code}")
    
    print("✓ Got HTML from ScrapingBee", flush=True)
    
    # Parse HTML
    soup = BeautifulSoup(response.content, 'html.parser')
    page_title = soup.title.string if soup.title else url
    
    print(f"✓ Page title: {page_title}", flush=True)
    
    # Find products - try multiple selectors
    product_selectors = [
        'div.product-card, div.product-item, div.grid-product, div.grid__item',
        'li.product, div.product',
        'article[data-product], div[data-product-id]',
    ]
    
    elements = []
    for selector in product_selectors.split(', '):
        elements = soup.select(selector)
        if len(elements) > 3:
            print(f"✓ Found {len(elements)} products with: {selector}", flush=True)
            break
    
    if not elements or len(elements) < 3:
        print("✗ No products found", flush=True)
        return [], page_title
    
    print(f"Extracting data from {min(len(elements), max_products)} products...", flush=True)
    
    # Extract product data
    for idx, element in enumerate(elements[:max_products]):
        try:
            # Name
            name = None
            for selector in ['h2', 'h3', 'h4', '.product-title', '[class*="title"]']:
                name_el = element.select_one(selector)
                if name_el:
                    name = name_el.get_text().strip()
                    if name and 3 < len(name) < 200:
                        break
            
            # Price
            price = 0.0
            for selector in ['.price', '[class*="price"]', '.money']:
                price_el = element.select_one(selector)
                if price_el:
                    price_text = price_el.get_text().strip()
                    numbers = re.findall(r'\d+[.,]?\d*', price_text)
                    if numbers:
                        try:
                            price = float(numbers[0].replace(',', '.'))
                            break
                        except:
                            continue
            
            # Description
            description = None
            desc_el = element.select_one('.product-description, .description, p')
            if desc_el:
                description = desc_el.get_text().strip()[:500]
            
            # Image
            image_url = None
            img_el = element.select_one('img')
            if img_el:
                image_url = img_el.get('src') or img_el.get('data-src')
                if image_url and image_url.startswith('//'):
                    image_url = 'https:' + image_url
                elif image_url and not image_url.startswith('http'):
                    image_url = urljoin(url, image_url)
            
            # Product URL
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
                
                if (idx + 1) % 10 == 0:
                    print(f"  Processed {idx + 1}...", flush=True)
        
        except Exception as e:
            print(f"  Error on product {idx}: {e}", flush=True)
            continue
    
    print(f"✓ Extracted {len(products)} products", flush=True)
    return products, page_title

@router.post("/crawl")
async def crawl_website(req: CrawlRequest):
    """Crawl a website and extract products using ScrapingBee"""
    print(f"\n{'='*60}", flush=True)
    print(f"CRAWL REQUEST: {req.url}", flush=True)
    print(f"{'='*60}\n", flush=True)
    
    try:
        products, page_title = scrape_with_scrapingbee(req.url, 50)
        
        if not products:
            raise HTTPException(status_code=400, detail="No products found")
        
        print(f"✓ Got {len(products)} products", flush=True)
        
        # Supabase
        supabase = get_supabase_client()
        
        business_id = str(uuid.uuid4())
        business_data = {
            'id': business_id,
            'business_name': page_title or req.url,
            'website_url': req.url,
            'created_at': None,
        }
        
        supabase.table('businesses').insert(business_data).execute()
        print("✓ Business inserted", flush=True)
        
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
        
        print(f"✓ COMPLETE - {len(products)} products inserted\n", flush=True)
        
        return {
            "status": "success",
            "message": f"Successfully crawled {len(products)} products",
            "business_id": business_id,
            "product_count": len(products)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"✗✗✗ ERROR: {e}", flush=True)
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed: {str(e)}")
```

---

## **STEP 3: Update requirements.txt**

Replace `playwright==1.40.0` with:
```
beautifulsoup4==4.12.2