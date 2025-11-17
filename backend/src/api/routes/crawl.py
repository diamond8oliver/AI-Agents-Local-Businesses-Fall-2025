from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
from src.database.supabase_client import get_supabase_client
from playwright.async_api import async_playwright
import re
from urllib.parse import urljoin

router = APIRouter(prefix="/api", tags=["crawl"])

class CrawlRequest(BaseModel):
    url: str

async def scrape_with_playwright(url: str, max_products: int = 50):
    """
    Scrape products from JavaScript-rendered sites using Playwright ASYNC
    Returns: list of {name, price, image_url, url, description}
    """
    products = []
    
    print("=== STARTING PLAYWRIGHT ASYNC ===", flush=True)
    
    async with async_playwright() as p:
        print("Launching Chromium...", flush=True)
        browser = await p.chromium.launch(headless=True)
        print("✓ Browser launched", flush=True)
        
        page = await browser.new_page()
        print("✓ Page created", flush=True)
        
        try:
            print(f"Navigating to: {url}", flush=True)
            await page.goto(url, timeout=30000, wait_until="networkidle")
            print("✓ Page loaded", flush=True)
            
            await page.wait_for_timeout(2000)
            print("✓ Waited for content", flush=True)
            
            page_title = await page.title()
            print(f"✓ Page title: {page_title}", flush=True)
            
            # Extract products
            product_selectors = [
                'div.product-card, div.product-item, div.grid-product, div.grid__item',
                'li.product, div.product, ul.products li',
                'article[data-product], div[data-product-id], [class*="product-"]',
                'article, li[class*="product"], div[class*="product-card"]',
            ]
            
            elements = []
            for selector in product_selectors:
                elements = await page.query_selector_all(selector)
                if len(elements) > 3:
                    print(f"✓ Found {len(elements)} products with: {selector}", flush=True)
                    break
            
            if not elements or len(elements) < 3:
                print("✗ No products found", flush=True)
                await browser.close()
                return [], page_title
            
            print(f"Extracting from {min(len(elements), max_products)} products...", flush=True)
            
            for idx, element in enumerate(elements[:max_products]):
                try:
                    # Name
                    name_selectors = ['h2', 'h3', 'h4', '.product-title', '.product__title', '[class*="title"]']
                    name = None
                    for ns in name_selectors:
                        name_el = await element.query_selector(ns)
                        if name_el:
                            name = (await name_el.inner_text()).strip()
                            if name and 3 < len(name) < 200:
                                break
                    
                    # Price
                    price_selectors = ['.price', 'span.price', '[class*="price"]', '.money']
                    price = 0.0
                    for ps in price_selectors:
                        price_el = await element.query_selector(ps)
                        if price_el:
                            price_text = (await price_el.inner_text()).strip()
                            numbers = re.findall(r'\d+[.,]?\d*', price_text)
                            if numbers:
                                try:
                                    price = float(numbers[0].replace(',', '.'))
                                    break
                                except:
                                    continue
                    
                    # Description
                    description = None
                    desc_el = await element.query_selector('.product-description, .description, p')
                    if desc_el:
                        description = (await desc_el.inner_text()).strip()[:500]
                    
                    # Image
                    image_url = None
                    img_el = await element.query_selector('img')
                    if img_el:
                        image_url = await img_el.get_attribute('src') or await img_el.get_attribute('data-src')
                        if image_url and image_url.startswith('//'):
                            image_url = 'https:' + image_url
                        elif image_url and not image_url.startswith('http'):
                            image_url = urljoin(url, image_url)
                    
                    # URL
                    product_url = url
                    link_el = await element.query_selector('a')
                    if link_el:
                        href = await link_el.get_attribute('href')
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
            await browser.close()
            return products, page_title
            
        except Exception as e:
            print(f"✗ Error: {e}", flush=True)
            import traceback
            traceback.print_exc()
            await browser.close()
            return [], ""

@router.post("/crawl")
async def crawl_website(req: CrawlRequest):
    """Crawl a website and extract products using Playwright"""
    print(f"\n{'='*60}", flush=True)
    print(f"CRAWL REQUEST: {req.url}", flush=True)
    print(f"{'='*60}\n", flush=True)
    
    try:
        # Use async Playwright directly (no thread needed)
        products, page_title = await scrape_with_playwright(req.url, 50)
        
        if not products:
            raise HTTPException(status_code=400, detail="No products found")
        
        print(f"✓ Got {len(products)} products", flush=True)
        
        # Supabase
        print("Connecting to Supabase...", flush=True)
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
        
        # Insert in batches
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