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
                'render_js': 'true',
                'wait': 3000,
                'premium_proxy': 'false',
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
            if len(found) >= 3:
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
                
                if extracted_count % 10 == 0:
                    print(f"  → Processed {extracted_count} products...", flush=True)
        
        except Exception as e:
            print(f"  ✗ Error on product {idx}: {str(e)}", flush=True)
            continue
    
    print(f"\n✓ Successfully extracted {len(products)} products", flush=True)
    return products, page_title


def extract_category_from_name(name: str) -> Optional[str]:
    """
    Extract product category from name using comprehensive keyword matching
    Works for any type of product across multiple industries
    """
    if not name:
        return None
    
    name_lower = name.lower()
    
    # Comprehensive category keywords (order matters - check specific before general)
    categories = {
        # Clothing & Fashion
        'Jeans': ['jean', 'denim'],
        'Shirts & Tops': ['tee', 't-shirt', 'shirt', 'top', 'blouse', 'tank', 'polo', 'button-up', 'button-down'],
        'Hoodies & Sweatshirts': ['hoodie', 'sweatshirt', 'sweater', 'pullover', 'crewneck'],
        'Jackets & Coats': ['jacket', 'coat', 'puffer', 'windbreaker', 'blazer', 'parka', 'vest'],
        'Shorts': ['short'],
        'Pants': ['pant', 'trouser', 'jogger', 'sweatpant', 'chino', 'cargo'],
        'Dresses & Skirts': ['dress', 'skirt', 'gown', 'maxi', 'midi'],
        'Shoes': ['shoe', 'sneaker', 'boot', 'sandal', 'heel', 'loafer', 'slipper', 'clog'],
        'Accessories': ['hat', 'cap', 'beanie', 'scarf', 'glove', 'belt', 'tie', 'watch', 'sunglasses', 'bag', 'backpack', 'wallet', 'purse'],
        'Socks & Underwear': ['sock', 'underwear', 'brief', 'boxer', 'bra'],
        
        # Electronics & Tech
        'Computers & Laptops': ['laptop', 'computer', 'macbook', 'pc', 'desktop', 'chromebook'],
        'Phones & Tablets': ['phone', 'iphone', 'android', 'tablet', 'ipad', 'smartphone'],
        'Audio': ['headphone', 'earbuds', 'airpod', 'speaker', 'soundbar', 'microphone'],
        'Cameras': ['camera', 'lens', 'gopro', 'dslr', 'mirrorless'],
        'Gaming': ['gaming', 'playstation', 'xbox', 'nintendo', 'console', 'controller'],
        'Smart Home': ['smart home', 'alexa', 'echo', 'nest', 'ring', 'thermostat'],
        'TV & Video': ['tv', 'television', 'monitor', 'display', 'projector'],
        
        # Home & Garden
        'Furniture': ['chair', 'table', 'desk', 'sofa', 'couch', 'bed', 'dresser', 'shelf', 'cabinet'],
        'Kitchen': ['pan', 'pot', 'knife', 'blender', 'mixer', 'toaster', 'cookware', 'cutlery'],
        'Bedding': ['sheet', 'pillow', 'blanket', 'comforter', 'duvet', 'mattress'],
        'Decor': ['lamp', 'rug', 'curtain', 'mirror', 'frame', 'vase', 'candle'],
        'Garden & Outdoor': ['plant', 'seed', 'garden', 'lawn', 'grill', 'patio'],
        'Tools': ['drill', 'hammer', 'saw', 'wrench', 'screwdriver', 'toolbox'],
        
        # Sports & Outdoors
        'Camping & Hiking': ['tent', 'sleeping bag', 'backpack', 'hiking', 'camp'],
        'Fitness': ['dumbbell', 'yoga', 'weight', 'treadmill', 'exercise', 'gym'],
        'Bikes': ['bike', 'bicycle', 'cycling'],
        'Skateboards': ['skateboard', 'deck', 'longboard'],
        'Water Sports': ['surfboard', 'kayak', 'paddleboard', 'swim'],
        'Team Sports': ['basketball', 'football', 'soccer', 'baseball', 'tennis'],
        
        # Beauty & Personal Care
        'Skincare': ['serum', 'moisturizer', 'cleanser', 'toner', 'cream', 'lotion', 'sunscreen'],
        'Makeup': ['lipstick', 'foundation', 'mascara', 'eyeshadow', 'blush', 'makeup'],
        'Hair Care': ['shampoo', 'conditioner', 'hair oil', 'hair mask', 'styling'],
        'Fragrance': ['perfume', 'cologne', 'fragrance', 'scent'],
        'Bath & Body': ['body wash', 'soap', 'bath', 'shower'],
        
        # Food & Beverages
        'Coffee & Tea': ['coffee', 'tea', 'espresso'],
        'Snacks': ['chip', 'cookie', 'candy', 'chocolate', 'snack'],
        'Beverages': ['juice', 'soda', 'water', 'drink'],
        
        # Books & Media
        'Books': ['book', 'novel', 'textbook', 'cookbook'],
        'Music': ['vinyl', 'cd', 'album', 'record'],
        'Movies': ['dvd', 'blu-ray', 'movie'],
        
        # Toys & Games
        'Toys': ['toy', 'doll', 'action figure', 'lego', 'puzzle'],
        'Board Games': ['board game', 'card game', 'game'],
        
        # Baby & Kids
        'Baby Gear': ['stroller', 'crib', 'car seat', 'baby carrier'],
        'Baby Clothing': ['onesie', 'baby clothes', 'infant'],
        
        # Health & Wellness
        'Supplements': ['vitamin', 'supplement', 'protein', 'probiotic'],
        'Medical': ['thermometer', 'blood pressure', 'first aid'],
        
        # Pet Products
        'Pet Supplies': ['dog', 'cat', 'pet', 'leash', 'collar', 'pet food'],
        
        # Office & Stationery
        'Office Supplies': ['pen', 'pencil', 'notebook', 'paper', 'binder', 'stapler'],
        
        # Automotive
        'Auto Parts': ['tire', 'battery', 'oil', 'filter', 'brake', 'spark plug'],
        
        # Jewelry
        'Jewelry': ['ring', 'necklace', 'bracelet', 'earring', 'chain'],
    }
    
    # Check for category matches
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in name_lower:
                return category
    
    # Default category
    return 'Other'


def extract_colors_from_name(name: str) -> List[str]:
    """Extract colors from product name"""
    if not name:
        return []
    
    name_lower = name.lower()
    colors = ['black', 'white', 'red', 'blue', 'green', 'yellow', 'orange', 'purple', 'pink', 'gray', 'grey', 'brown', 'beige', 'navy', 'olive', 'burgundy', 'maroon', 'teal', 'cream', 'tan', 'vintage']
    
    found_colors = []
    for color in colors:
        if color in name_lower:
            found_colors.append(color.capitalize())
    
    return list(set(found_colors))  # Remove duplicates


def extract_sizes_from_name(name: str) -> List[str]:
    """Extract sizes from product name"""
    if not name:
        return []
    
    name_lower = name.lower()
    sizes = ['xs', 'small', 's', 'medium', 'm', 'large', 'l', 'xl', 'xxl', '2xl', '3xl', 
             'one size', 'os', '7', '7.5', '8', '8.5', '9', '9.5', '10', '10.5', '11', '11.5', '12']
    
    found_sizes = []
    for size in sizes:
        # Match whole words
        if f' {size} ' in f' {name_lower} ' or name_lower.endswith(f' {size}'):
            found_sizes.append(size.upper())
    
    return list(set(found_sizes))


def extract_product_data(element: BeautifulSoup, base_url: str, idx: int) -> Optional[dict]:
    """
    Extract structured product data from a product element
    Returns dict with name, price, image_url, url, description, category, colors, sizes or None if invalid
    """
    
    # ===== PRODUCT NAME EXTRACTION =====
    name = None
    name_selectors = [
        'h2.product-title',
        'h3.product-name',
        'h4.product__title',
        '.product-card__title',
        '.product-title',
        '.product-name',
        '[data-product-name]',
        '[data-product-title]',
        'a.product-link',
        'a.product-card__link',
        'a[href*="/products/"]',
        '.product-card h2',
        '.product-card h3',
        '.product-card h4',
        'h2', 'h3', 'h4',
    ]
    
    for selector in name_selectors:
        name_el = element.select_one(selector)
        if name_el:
            if name_el.get('data-product-name'):
                potential_name = name_el.get('data-product-name').strip()
            elif name_el.get('data-product-title'):
                potential_name = name_el.get('data-product-title').strip()
            else:
                potential_name = name_el.get_text().strip()
            
            if validate_product_name(potential_name):
                name = potential_name
                break
    
    if not name:
        link_el = element.select_one('a')
        if link_el:
            if link_el.get('title'):
                name = link_el.get('title').strip()
            elif link_el.get('aria-label'):
                name = link_el.get('aria-label').strip()
    
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
            if price_el.get('data-product-price'):
                price_text = price_el.get('data-product-price')
            else:
                price_text = price_el.get_text().strip()
            
            numbers = re.findall(r'\d+[.,]?\d*', price_text)
            if numbers:
                try:
                    price = float(numbers[0].replace(',', '.'))
                    break
                except ValueError:
                    continue
    
    # ===== IMAGE EXTRACTION =====
    image_url = None
    img_el = element.select_one('img')
    
    if img_el:
        for attr in ['src', 'data-src', 'data-lazy-src', 'data-srcset']:
            img_src = img_el.get(attr)
            if img_src:
                if img_src.startswith('//'):
                    image_url = 'https:' + img_src
                elif img_src.startswith('http'):
                    image_url = img_src
                elif img_src.startswith('/'):
                    image_url = urljoin(base_url, img_src)
                else:
                    image_url = urljoin(base_url, img_src)
                
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
            if len(desc_text) > 10:
                description = desc_text[:500]
                break
    
    if not description:
        description = f"Product: {name}"
    
    # ===== CATEGORY, COLORS, SIZES EXTRACTION =====
    category = extract_category_from_name(name)
    colors = extract_colors_from_name(name)
    sizes = extract_sizes_from_name(name)
    
    # Return structured product data
    return {
        'name': name,
        'price': price,
        'image_url': image_url,
        'url': product_url,
        'description': description,
        'category': category,
        'colors': colors,
        'sizes': sizes,
    }


def validate_product_name(name: str) -> bool:
    """
    Validate that a product name is legitimate
    Returns True if valid, False otherwise
    """
    if not name:
        return False
    
    if len(name) < 3 or len(name) > 200:
        return False
    
    invalid_names = [
        'product', 'products', 'item', 'items',
        'shop', 'buy now', 'add to cart', 'quick view',
        'view details', 'learn more', 'see more',
        'sale', 'new', 'featured'
    ]
    
    if name.lower() in invalid_names:
        return False
    
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
                'images': [product['image_url']] if product['image_url'] else [],
                'url': product['url'],
                'in_stock': True,
                'category': product.get('category'),
                'colors': product.get('colors', []),
                'sizes': product.get('sizes', []),
                'created_at': datetime.utcnow().isoformat(),
            })
        
        # Insert products in batches
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
        raise
        
    except Exception as e:
        error_msg = f"Crawl failed: {str(e)}"
        print(f"\n✗ ERROR: {error_msg}", flush=True)
        print(traceback.format_exc(), flush=True)
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to crawl website: {str(e)}"
        )