from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import uuid
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
import os
import traceback

from src.database.supabase_client import get_supabase_client

router = APIRouter(prefix="/api", tags=["crawl"])


class CrawlRequest(BaseModel):
    url: str
    business_name: Optional[str] = None


class CrawlResponse(BaseModel):
    business_id: str
    products_found: int
    message: str


def scrape_with_scrapingbee(url: str, max_products: int = 50) -> tuple[List[dict], str]:
    """
    Scrape products using ScrapingBee API with improved extraction logic
    Returns: (list of products, page_title)
    """
    products = []
    
    print(f"\n{'='*60}", flush=True)
    print(f"SCRAPINGBEE SCRAPING: {url}", flush=True)
    print(f"{'='*60}\n", flush=True)
    
    # Get API key from environment
    api_key = os.getenv('SCRAPINGBEE_API_KEY')
    if not api_key:
        raise Exception("SCRAPINGBEE_API_KEY not set in environment variables")
    
    # Call ScrapingBee API
    print("→ Calling ScrapingBee API...", flush=True)
    try:
        response = requests.get(
            'https://app.scrapingbee.com/api/v1/',
            params={
                'api_key': api_key,
                'url': url,
                'render_js': 'true',  # Render JavaScript
                'wait': 3000,  # Wait 3 seconds for content to load
                'premium_proxy': 'false',  # Use regular proxy (free tier)
            },
            timeout=90
        )
        
        if response.status_code != 200:
            error_msg = f"ScrapingBee returned status {response.status_code}"
            if response.status_code == 401:
                error_msg = "Invalid ScrapingBee API key"
            elif response.status_code == 429:
                error_msg = "ScrapingBee rate limit exceeded"
            raise Exception(error_msg)
        
        print(f"✓ Got {len(response.content)} bytes from ScrapingBee", flush=True)
        
    except requests.Timeout:
        raise Exception("ScrapingBee request timed out after 90 seconds")
    except requests.RequestException as e:
        raise Exception(f"ScrapingBee request failed: {str(e)}")
    
    # Parse HTML
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract page title
    page_title = url
    if soup.title and soup.title.string:
        page_title = soup.title.string.strip()
    print(f"✓ Page title: {page_title}", flush=True)
    
    # Try multiple product container selectors (ordered by likelihood)
    product_selectors = [
        # Shopify specific
        'div.product-card, div.product-item, div.grid-product, div.grid__item',
        # WooCommerce specific
        'li.product, div.product',
        # Generic e-commerce
        'article[data-product], div[data-product-id], div[data-product]',
        # More generic patterns
        'div[class*="product-"], div[class*="product_"]',
        'div[class*="item-"], div[class*="item_"]',
    ]
    
    elements = []
    matched_selector = None
    
    for selector_group in product_selectors:
        for selector in selector_group.split(', '):
            found = soup.select(selector)
            if len(found) >= 3:  # Need at least 3 products to consider it valid
                elements = found
                matched_selector = selector
                break
        if elements:
            break
    
    if not elements or len(elements) < 3:
        print("✗ No products found with standard selectors", flush=True)
        return [], page_title
    
    print(f"✓ Found {len(elements)} product elements with: {matched_selector}", flush=True)
    print(f"→ Extracting data from {min(len(elements), max_products)} products...\n", flush=True)
    
    # Extract product data
    extracted_count = 0
    for idx, element in enumerate(elements[:max_products]):
        try:
            product_data = extract_product_data(element, url, idx)
            
            if product_data and product_data['name']:
                products.append(product_data)
                extracted_count += 1
                
                # Progress update every 10 products
                if extracted_count % 10 == 0:
                    print(f"  → Processed {extracted_count} products...", flush=True)
        
        except Exception as e:
            print(f"  ✗ Error on product {idx}: {str(e)}", flush=True)
            continue
    
    print(f"\n✓ Successfully extracted {len(products)} products", flush=True)
    return products, page_title


def extract_product_data(element: BeautifulSoup, base_url: str, idx: int) -> Optional[dict]:
    """
    Extract structured product data from a product element
    Returns dict with name, price, image_url, url, description or None if invalid
    """
    
    # ===== PRODUCT NAME EXTRACTION (IMPROVED) =====
    name = None
    name_selectors = [
        # Specific class-based selectors (most reliable)
        'h2.product-title',
        'h3.product-name',
        'h4.product__title',
        '.product-card__title',
        '.product-title',
        '.product-name',
        
        # Attribute-based selectors
        '[data-product-name]',
        '[data-product-title]',
        
        # Link-based selectors (product links often contain name)
        'a.product-link',
        'a.product-card__link',
        'a[href*="/products/"]',
        
        # Generic heading selectors (fallback)
        '.product-card h2',
        '.product-card h3',
        '.product-card h4',
        'h2', 'h3', 'h4',
    ]
    
    for selector in name_selectors:
        name_el = element.select_one(selector)
        if name_el:
            # Try data attribute first
            if name_el.get('data-product-name'):
                potential_name = name_el.get('data-product-name').strip()
            elif name_el.get('data-product-title'):
                potential_name = name_el.get('data-product-title').strip()
            else:
                potential_name = name_el.get_text().strip()
            
            # Validate the name
            if validate_product_name(potential_name):
                name = potential_name
                break
    
    # If still no name, try getting it from the first link's title or aria-label
    if not name:
        link_el = element.select_one('a')
        if link_el:
            if link_el.get('title'):
                name = link_el.get('title').strip()
            elif link_el.get('aria-label'):
                name = link_el.get('aria-label').strip()
    
    # Final validation
    if not name or not validate_product_name(name):
        return None
    
    # ===== PRICE EXTRACTION =====
    price = 0.0
    price_selectors = [
        '.price',
        '[class*="price"]',
        '.money',
        '[data-product-price]',
        'span[class*="Price"]',
        'div[class*="price"]',
    ]
    
    for selector in price_selectors:
        price_el = element.select_one(selector)
        if price_el:
            # Try data attribute first
            if price_el.get('data-product-price'):
                price_text = price_el.get('data-product-price')
            else:
                price_text = price_el.get_text().strip()
            
            # Extract numbers from price text
            # Handle formats: $99.99, €99,99, 99.99, 99,99
            numbers = re.findall(r'\d+[.,]?\d*', price_text)
            if numbers:
                try:
                    # Take the first number found, replace comma with period
                    price = float(numbers[0].replace(',', '.'))
                    break
                except ValueError:
                    continue
    
    # ===== IMAGE EXTRACTION =====
    image_url = None
    img_el = element.select_one('img')
    
    if img_el:
        # Try multiple image source attributes
        for attr in ['src', 'data-src', 'data-lazy-src', 'data-srcset']:
            img_src = img_el.get(attr)
            if img_src:
                # Handle protocol-relative URLs
                if img_src.startswith('//'):
                    image_url = 'https:' + img_src
                elif img_src.startswith('http'):
                    image_url = img_src
                elif img_src.startswith('/'):
                    image_url = urljoin(base_url, img_src)
                else:
                    image_url = urljoin(base_url, img_src)
                
                # Clean up srcset if needed (take first URL)
                if ' ' in image_url:
                    image_url = image_url.split(' ')[0]
                
                break
    
    # ===== PRODUCT URL EXTRACTION =====
    product_url = base_url
    link_el = element.select_one('a')
    
    if link_el:
        href = link_el.get('href')
        if href:
            if href.startswith('http'):
                product_url = href
            elif href.startswith('/'):
                product_url = urljoin(base_url, href)
            else:
                product_url = urljoin(base_url, href)
    
    # ===== DESCRIPTION EXTRACTION =====
    description = None
    desc_selectors = [
        '.product-description',
        '.description',
        '[class*="description"]',
        'p',
    ]
    
    for selector in desc_selectors:
        desc_el = element.select_one(selector)
        if desc_el:
            desc_text = desc_el.get_text().strip()
            if len(desc_text) > 10:  # Need reasonable description
                description = desc_text[:500]  # Limit to 500 chars
                break
    
    # Use product name as fallback description
    if not description:
        description = f"Product: {name}"
    
    # Return structured product data
    return {
        'name': name,
        'price': price,
        'image_url': image_url,
        'url': product_url,
        'description': description,
    }


def validate_product_name(name: str) -> bool:
    """
    Validate that a product name is legitimate
    Returns True if valid, False otherwise
    """
    if not name:
        return False
    
    # Length checks
    if len(name) < 3 or len(name) > 200:
        return False
    
    # Reject generic placeholder names
    invalid_names = [
        'product', 'products', 'item', 'items',
        'shop', 'buy now', 'add to cart', 'quick view',
        'view details', 'learn more', 'see more',
        'sale', 'new', 'featured'
    ]
    
    if name.lower() in invalid_names:
        return False
    
    # Must contain at least one alphanumeric character
    if not re.search(r'[a-zA-Z0-9]', name):
        return False
    
    return True


@router.post("/crawl", response_model=CrawlResponse)
async def crawl_website(req: CrawlRequest):
    """
    Crawl a business website, extract products, store in Supabase
    Returns business_id for chatbot initialization
    """
    print(f"\n{'='*80}", flush=True)
    print(f"NEW CRAWL REQUEST", flush=True)
    print(f"URL: {req.url}", flush=True)
    print(f"Business Name: {req.business_name or 'Not provided'}", flush=True)
    print(f"{'='*80}\n", flush=True)
    
    try:
        # Scrape products
        products, page_title = scrape_with_scrapingbee(req.url, max_products=50)
        
        if not products:
            print("\n✗ CRAWL FAILED: No products found", flush=True)
            raise HTTPException(
                status_code=400,
                detail="No products found on this website. Please try a page with product listings (like /shop or /collections)."
            )
        
        print(f"\n→ Preparing to store {len(products)} products in database...", flush=True)
        
        # Generate unique business ID
        business_id = str(uuid.uuid4())
        
        # Determine business name
        business_name = req.business_name or page_title or req.url
        
        # Connect to Supabase
        supabase = get_supabase_client()
        
        # Insert business record
        business_data = {
            'id': business_id,
            'business_name': business_name,
            'website_url': req.url,
            'created_at': datetime.utcnow().isoformat(),
        }
        
        print(f"→ Inserting business: {business_name}", flush=True)
        supabase.table('businesses').insert(business_data).execute()
        print("✓ Business record created", flush=True)
        
        # Prepare products for insertion
        products_to_insert = []
        for product in products:
            products_to_insert.append({
                'business_id': business_id,
                'name': product['name'],
                'price': product['price'],
                'description': product['description'],
                'images': [product['image_url']] if product['image_url'] else [],  # FIXED: Changed from image_url to images array
                'url': product['url'],
                'in_stock': True,  # Default to in stock
                'created_at': datetime.utcnow().isoformat(),
            })
        
        # Insert products in batches (Supabase has limits)
        batch_size = 50
        for i in range(0, len(products_to_insert), batch_size):
            batch = products_to_insert[i:i + batch_size]
            print(f"→ Inserting products batch {i//batch_size + 1} ({len(batch)} products)...", flush=True)
            supabase.table('products').insert(batch).execute()
        
        print(f"\n✓ CRAWL SUCCESS: Stored {len(products)} products", flush=True)
        print(f"✓ Business ID: {business_id}", flush=True)
        print(f"{'='*80}\n", flush=True)
        
        return CrawlResponse(
            business_id=business_id,
            products_found=len(products),
            message=f"Successfully crawled {len(products)} products from {business_name}"
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (expected errors)
        raise
        
    except Exception as e:
        # Log unexpected errors with full traceback
        error_msg = f"Crawl failed: {str(e)}"
        print(f"\n✗ ERROR: {error_msg}", flush=True)
        print(traceback.format_exc(), flush=True)
        
        # Return user-friendly error
        raise HTTPException(
            status_code=500,
            detail=f"Failed to crawl website: {str(e)}"
        )