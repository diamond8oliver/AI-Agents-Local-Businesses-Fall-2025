"""
Crawl endpoint for scraping business websites and storing products
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
import uuid
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from src.database.supabase_client import get_supabase_client
import traceback

router = APIRouter()

class CrawlRequest(BaseModel):
    url: HttpUrl
    business_name: str = None

class CrawlResponse(BaseModel):
    business_id: str
    products_found: int
    message: str

@router.post("/crawl", response_model=CrawlResponse)
async def crawl_website(request: CrawlRequest):
    try:
        print(f"Starting crawl for URL: {request.url}", flush=True)
        business_id = str(uuid.uuid4())
        
        response = requests.get(str(request.url), timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        print(f"Successfully fetched URL", flush=True)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        products = extract_products(soup, str(request.url))
        print(f"Extracted {len(products)} products", flush=True)
        
        if not products:
            raise HTTPException(status_code=400, detail="No products found on this website")
        
        print("Connecting to Supabase...", flush=True)
        supabase = get_supabase_client()
        print("Connected to Supabase", flush=True)
        
        business_data = {
            'id': business_id,
            'business_name': request.business_name or extract_business_name(soup),
            'website_url': str(request.url),
            'created_at': datetime.utcnow().isoformat()
        }
        
        print(f"Inserting business: {business_data}", flush=True)
        supabase.table('businesses').insert(business_data).execute()
        print("Business inserted", flush=True)
        
        for product in products:
            product['business_id'] = business_id
            product['created_at'] = datetime.utcnow().isoformat()
        
        print(f"Inserting {len(products)} products", flush=True)
        supabase.table('products').insert(products).execute()
        print("Products inserted", flush=True)
        
        return CrawlResponse(
            business_id=business_id,
            products_found=len(products),
            message=f"Successfully crawled {len(products)} products"
        )
        
    except requests.RequestException as e:
        error_msg = f"Failed to fetch website: {str(e)}"
        print(f"ERROR: {error_msg}", flush=True)
        print(traceback.format_exc(), flush=True)
        raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        error_msg = f"Crawl failed: {str(e)}"
        print(f"ERROR: {error_msg}", flush=True)
        print(traceback.format_exc(), flush=True)
        raise HTTPException(status_code=500, detail=error_msg)


def extract_products(soup: BeautifulSoup, base_url: str) -> list:
    products = []
    
    product_selectors = [
        '.product',
        '.product-item',
        '[itemtype*="Product"]',
        '.woocommerce-loop-product',
        '.product-card'
    ]
    
    product_elements = []
    for selector in product_selectors:
        found = soup.select(selector)
        if found:
            product_elements = found
            break
    
    if not product_elements:
        product_elements = find_products_by_pattern(soup)
    
    for element in product_elements[:50]:
        try:
            name = extract_product_name(element)
            price = extract_price(element)
            description = extract_description(element)
            image_url = extract_image(element, base_url)
            
            if name:
                products.append({
                    'name': name,
                    'price': price,
                    'description': description or f"Product: {name}",
                    'images': [image_url] if image_url else [],
                    'url': base_url
                })
        except Exception as e:
            continue
    
    return products


def find_products_by_pattern(soup: BeautifulSoup) -> list:
    products = []
    price_elements = soup.find_all(string=lambda text: text and ('$' in text or '€' in text or '£' in text))
    
    for price_elem in price_elements[:50]:
        parent = price_elem.parent
        heading = parent.find_previous(['h1', 'h2', 'h3', 'h4'])
        if heading and len(heading.get_text(strip=True)) > 0:
            products.append(parent)
    
    return products


def extract_product_name(element) -> str:
    name_elem = element.find(['h1', 'h2', 'h3', 'h4', 'a'])
    if name_elem:
        return name_elem.get_text(strip=True)
    
    name_elem = element.find(attrs={'itemprop': 'name'})
    if name_elem:
        return name_elem.get_text(strip=True)
    
    name_elem = element.find(class_=lambda x: x and ('name' in x.lower() or 'title' in x.lower()))
    if name_elem:
        return name_elem.get_text(strip=True)
    
    return "Product"


def extract_price(element) -> float:
    price_elem = element.find(attrs={'itemprop': 'price'})
    if price_elem and price_elem.get('content'):
        try:
            return float(price_elem['content'])
        except:
            pass
    
    price_elem = element.find(class_=lambda x: x and 'price' in x.lower())
    if price_elem:
        price_text = price_elem.get_text(strip=True)
        import re
        match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
        if match:
            try:
                return float(match.group())
            except:
                pass
    
    text = element.get_text()
    import re
    price_match = re.search(r'\$\s*([\d,]+\.?\d*)', text.replace(',', ''))
    if price_match:
        try:
            return float(price_match.group(1))
        except:
            pass
    
    return 0.0


def extract_description(element) -> str:
    desc_elem = element.find(attrs={'itemprop': 'description'})
    if desc_elem:
        return desc_elem.get_text(strip=True)
    
    desc_elem = element.find(class_=lambda x: x and ('description' in x.lower() or 'excerpt' in x.lower()))
    if desc_elem:
        return desc_elem.get_text(strip=True)[:500]
    
    p_elem = element.find('p')
    if p_elem:
        return p_elem.get_text(strip=True)[:500]
    
    return None


def extract_image(element, base_url: str) -> str:
    img_elem = element.find('img', attrs={'itemprop': 'image'})
    if not img_elem:
        img_elem = element.find('img')
    
    if img_elem:
        src = img_elem.get('src') or img_elem.get('data-src')
        if src:
            if src.startswith('//'):
                return 'https:' + src
            elif src.startswith('/'):
                from urllib.parse import urljoin
                return urljoin(base_url, src)
            return src
    
    return None


def extract_business_name(soup: BeautifulSoup) -> str:
    title = soup.find('title')
    if title:
        return title.get_text(strip=True).split('|')[0].strip()
    
    site_name = soup.find('meta', attrs={'property': 'og:site_name'})
    if site_name and site_name.get('content'):
        return site_name['content']
    
    h1 = soup.find('h1')
    if h1:
        return h1.get_text(strip=True)
    
    return "Business"