from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
from src.database.supabase_client import get_supabase_client
from playwright.sync_api import sync_playwright
import time
import re
from urllib.parse import urljoin
import asyncio

router = APIRouter(prefix="/api", tags=["crawl"])

class CrawlRequest(BaseModel):
    url: str

def scrape_with_playwright(url: str, max_products: int = 50):
    """
    Scrape products from JavaScript-rendered sites using Playwright
    Returns: list of {name, price, image_url, url, description}
    """
    products = []
    
    with sync_playwright() as p:
        # Launch browser (headless for production)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            print(f"Loading page: {url}")
            # Go to URL and wait for content to load
            page.goto(url, timeout=30000, wait_until="networkidle")
            time.sleep(2)  # Extra wait for lazy-loaded content
            
            # Get page title for business name
            page_title = page.title()
            
            # Extract products - try multiple selectors
            product_selectors = [
                # Shopify
                'div.product-card, div.product-item, div.grid-product, div.grid__item',
                # WooCommerce
                'li.product, div.product, ul.products li',
                # Generic
                'article[data-product], div[data-product-id], [class*="product-"]',
                # Broader fallback
                'article, li[class*="product"], div[class*="product-card"]',
            ]
            
            elements = []
            for selector in product_selectors:
                elements = page.query_selector_all(selector)
                if len(elements) > 3:  # Need at least a few products
                    print(f"Found {len(elements)} products with selector: {selector}")
                    break
            
            if not elements or len(elements) < 3:
                print("No products found with standard selectors")
                browser.close()
                return [], page_title
            
            # Extract data from each product
            for element in elements[:max_products]:
                try:
                    # Try multiple name selectors
                    name_selectors = [
                        'h2', 'h3', 'h4',
                        '.product-title', '.product__title', '.product-card__title',
                        '[class*="title"]', '[class*="name"]',
                        'a[class*="product"]',
                    ]
                    name = None
                    for ns in name_selectors:
                        name_el = element.query_selector(ns)
                        if name_el:
                            name = name_el.inner_text().strip()
                            if name and len(name) > 3 and len(name) < 200:  # Valid name
                                break
                    
                    # Try multiple price selectors
                    price_selectors = [
                        '.price', 'span.price', 'div.price',
                        '[class*="price"]', '[data-price]',
                        '.money', 'span.money',
                    ]
                    price = 0.0
                    for ps in price_selectors:
                        price_el = element.query_selector(ps)
                        if price_el:
                            price_text = price_el.inner_text().strip()
                            # Extract numbers from "$99.99" or "99,99 €"
                            numbers = re.findall(r'\d+[.,]?\d*', price_text)
                            if numbers:
                                price_str = numbers[0].replace(',', '.')
                                try:
                                    price = float(price_str)
                                    break
                                except:
                                    continue
                    
                    # Description (optional)
                    description = None
                    desc_selectors = [
                        '.product-description', '.description',
                        '[class*="description"]', 'p',
                    ]
                    for ds in desc_selectors:
                        desc_el = element.query_selector(ds)
                        if desc_el:
                            description = desc_el.inner_text().strip()[:500]  # Max 500 chars
                            if description and len(description) > 10:
                                break
                    
                    # Image
                    image_url = None
                    img_el = element.query_selector('img')
                    if img_el:
                        image_url = img_el.get_attribute('src') or img_el.get_attribute('data-src')
                        if image_url and image_url.startswith('//'):
                            image_url = 'https:' + image_url
                        elif image_url and not image_url.startswith('http'):
                            image_url = urljoin(url, image_url)
                    
                    # Product URL
                    product_url = url  # Default to collection page
                    link_el = element.query_selector('a')
                    if link_el:
                        href = link_el.get_attribute('href')
                        if href:
                            if href.startswith('http'):
                                product_url = href
                            elif href.startswith('/'):
                                product_url = urljoin(url, href)
                    
                    # Only add if we got a valid name
                    if name and len(name) > 3:
                        products.append({
                            'name': name,
                            'price': price,
                            'image_url': image_url,
                            'url': product_url,
                            'description': description or f"Product: {name}",
                        })
                
                except Exception as e:
                    print(f"Error extracting product: {e}")
                    continue
            
            browser.close()
            return products, page_title
            
        except Exception as e:
            print(f"Playwright error: {e}")
            browser.close()
            return [], ""

@router.post("/crawl")
async def crawl_website(req: CrawlRequest):
    """Crawl a website and extract products using Playwright"""
    print(f"Starting crawl for URL: {req.url}", flush=True)
    
    try:
        # Add 90 second timeout
        print("About to call scrape_with_playwright...", flush=True)
        products, page_title = await asyncio.wait_for(
            asyncio.to_thread(scrape_with_playwright, req.url, 50),
            timeout=90.0
        )
        print(f"Scraping completed, got {len(products)} products", flush=True)
        
        if not products:
            raise HTTPException(status_code=400, detail="No products found on this website")
        
        print(f"Extracted {len(products)} products")
        
        # Connect to Supabase
        print("Connecting to Supabase...")
        supabase = get_supabase_client()
        print("Connected to Supabase")
        
        # Create business entry
        business_id = str(uuid.uuid4())
        business_data = {
            'id': business_id,
            'business_name': page_title or req.url,
            'website_url': req.url,
            'created_at': None,
        }
        
        print(f"Inserting business: {business_data}")
        supabase.table('businesses').insert(business_data).execute()
        print("Business inserted")
        
        # Prepare products for insertion
        products_to_insert = []
        for product in products:
            product_data = {
                'id': str(uuid.uuid4()),
                'business_id': business_id,
                'name': product['name'],
                'price': product['price'],
                'description': product['description'],
                'images': [product['image_url']] if product['image_url'] else [],
                'url': product['url'],
                'in_stock': True,
                'created_at': None,
            }
            products_to_insert.append(product_data)
        
        # Insert products in batches
        print(f"Inserting {len(products_to_insert)} products")
        batch_size = 100
        for i in range(0, len(products_to_insert), batch_size):
            batch = products_to_insert[i:i+batch_size]
            supabase.table('products').insert(batch).execute()
        
        print("Products inserted")
        
        return {
            "status": "success",
            "message": f"Successfully crawled {len(products)} products",
            "business_id": business_id,
            "product_count": len(products)
        }
    
    except asyncio.TimeoutError:
        print("ERROR: Scraping timed out after 90 seconds")
        raise HTTPException(status_code=500, detail="Scraping timed out - site may be too slow")
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: Crawl failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to crawl website: {str(e)}")