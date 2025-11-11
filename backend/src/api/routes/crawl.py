"""
Crawl endpoint for scraping business websites and storing products
Place this in: backend/src/api/routes/crawl.py
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
import uuid
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from src.database.supabase_client import get_supabase_client

router = APIRouter()

class CrawlRequest(BaseModel):
    url: HttpUrl  # Validates URL format
    business_name: str = None  # Optional business name

class CrawlResponse(BaseModel):
    business_id: str
    products_found: int
    message: str

@router.post("/crawl", response_model=CrawlResponse)
async def crawl_website(request: CrawlRequest):
    """
    Crawl a business website, extract products, store in Supabase
    Returns business_id for chatbot initialization
    """
    try:
        # Generate unique business_id
        business_id = str(uuid.uuid4())
        
        # Fetch the webpage
        response = requests.get(str(request.url), timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract products (customize this based on common e-commerce patterns)
        products = extract_products(soup, str(request.url))
        
        if not products:
            raise HTTPException(status_code=400, detail="No products found on this website")
        
        # Store in Supabase
        supabase = get_supabase_client()
        
        # Store business info
        business_data = {
            'id': business_id,
            'name': request.business_name or extract_business_name(soup),
            'url': str(request.url),
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Insert business (create this table if it doesn't exist)
        supabase.table('businesses').insert(business_data).execute()
        
        # Store products with business_id
        for product in products:
            product['business_id'] = business_id
            product['created_at'] = datetime.utcnow().isoformat()
        
        supabase.table('products').insert(products).execute()
        
        return CrawlResponse(
            business_id=business_id,
            products_found=len(products),
            message=f"Successfully crawled {len(products)} products"
        )
        
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch website: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Crawl failed: {str(e)}")


def extract_products(soup: BeautifulSoup, base_url: str) -> list:
    """
    Extract product information from HTML
    This is a basic implementation - customize based on common patterns
    """
    products = []
    
    # Common product selectors (try multiple patterns)
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
    
    # If no products found with selectors, try finding h2/h3 with prices nearby
    if not product_elements:
        product_elements = find_products_by_pattern(soup)
    
    for element in product_elements[:50]:  # Limit to 50 products
        try:
            # Extract product details
            name = extract_product_name(element)
            price = extract_price(element)
            description = extract_description(element)
            image_url = extract_image(element, base_url)
            
            if name:  # Only add if we found a name
                products.append({
                    'name': name,
                    'price': price,
                    'description': description or f"Product: {name}",
                    'image_url': image_url,
                    'url': base_url
                })
        except Exception as e:
            continue  # Skip problematic products
    
    return products


def find_products_by_pattern(soup: BeautifulSoup) -> list:
    """Fallback: Find products by looking for price + heading patterns"""
    products = []
    
    # Find all price elements
    price_elements = soup.find_all(string=lambda text: text and ('$' in text or '€' in text or '£' in text))
    
    for price_elem in price_elements[:50]:
        parent = price_elem.parent
        # Look for nearby heading
        heading = parent.find_previous(['h1', 'h2', 'h3', 'h4'])
        if heading and len(heading.get_text(strip=True)) > 0:
            products.append(parent)
    
    return products


def extract_product_name(element) -> str:
    """Extract product name from element"""
    # Try common heading tags
    name_elem = element.find(['h1', 'h2', 'h3', 'h4', 'a'])
    if name_elem:
        return name_elem.get_text(strip=True)
    
    # Try itemprop
    name_elem = element.find(attrs={'itemprop': 'name'})
    if name_elem:
        return name_elem.get_text(strip=True)
    
    # Try class patterns
    name_elem = element.find(class_=lambda x: x and ('name' in x.lower() or 'title' in x.lower()))
    if name_elem:
        return name_elem.get_text(strip=True)
    
    return "Product"


def extract_price(element) -> float:
    """Extract price from element"""
    # Try itemprop
    price_elem = element.find(attrs={'itemprop': 'price'})
    if price_elem and price_elem.get('content'):
        try:
            return float(price_elem['content'])
        except:
            pass
    
    # Try common class patterns
    price_elem = element.find(class_=lambda x: x and 'price' in x.lower())
    if price_elem:
        price_text = price_elem.get_text(strip=True)
        # Extract numeric value
        import re
        match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
        if match:
            try:
                return float(match.group())
            except:
                pass
    
    # Look for $ signs
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
    """Extract product description"""
    # Try itemprop
    desc_elem = element.find(attrs={'itemprop': 'description'})
    if desc_elem:
        return desc_elem.get_text(strip=True)
    
    # Try common class patterns
    desc_elem = element.find(class_=lambda x: x and ('description' in x.lower() or 'excerpt' in x.lower()))
    if desc_elem:
        return desc_elem.get_text(strip=True)[:500]  # Limit length
    
    # Try paragraph tags
    p_elem = element.find('p')
    if p_elem:
        return p_elem.get_text(strip=True)[:500]
    
    return None


def extract_image(element, base_url: str) -> str:
    """Extract product image URL"""
    # Try itemprop
    img_elem = element.find('img', attrs={'itemprop': 'image'})
    if not img_elem:
        img_elem = element.find('img')
    
    if img_elem:
        src = img_elem.get('src') or img_elem.get('data-src')
        if src:
            # Handle relative URLs
            if src.startswith('//'):
                return 'https:' + src
            elif src.startswith('/'):
                from urllib.parse import urljoin
                return urljoin(base_url, src)
            return src
    
    return None


def extract_business_name(soup: BeautifulSoup) -> str:
    """Extract business name from page"""
    # Try common patterns
    title = soup.find('title')
    if title:
        return title.get_text(strip=True).split('|')[0].strip()
    
    # Try site name meta tags
    site_name = soup.find('meta', attrs={'property': 'og:site_name'})
    if site_name and site_name.get('content'):
        return site_name['content']
    
    # Try h1
    h1 = soup.find('h1')
    if h1:
        return h1.get_text(strip=True)
    
    return "Business"