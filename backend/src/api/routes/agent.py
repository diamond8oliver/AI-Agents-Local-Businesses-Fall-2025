from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List
import anthropic
import os
from src.database.supabase_client import get_supabase_client
import re

router = APIRouter(prefix="/agent", tags=["agent"])

class AskRequest(BaseModel):
    question: str
    business_id: str
    k: Optional[int] = 10

def extract_filters(query: str):
    """Extract price, color, and category filters from query"""
    query_lower = query.lower()
    
    # Price filters
    min_price, max_price = 0, float('inf')
    
    under_match = re.search(r'(?:under|below|less than|cheaper than|max)\s*\$?(\d+(?:\.\d+)?)', query_lower)
    if under_match:
        max_price = float(under_match.group(1))
    
    over_match = re.search(r'(?:over|above|more than|at least)\s*\$?(\d+(?:\.\d+)?)', query_lower)
    if over_match:
        min_price = float(over_match.group(1))
    
    between_match = re.search(r'between\s*\$?(\d+(?:\.\d+)?)\s*(?:and|to|-)\s*\$?(\d+(?:\.\d+)?)', query_lower)
    if between_match:
        min_price, max_price = float(between_match.group(1)), float(between_match.group(2))
    
    # Category keywords (must match)
    category_keywords = []
    
    category_map = {
        # Clothing
        'shirts': ['shirt', 'tshirt', 't-shirt', 'tee', 'top'],
        'pants': ['pants', 'pant', 'jeans', 'jean', 'denim', 'trouser'],
        'shorts': ['shorts', 'short'],
        'hoodies': ['hoodie', 'sweatshirt', 'sweater', 'pullover', 'crewneck', 'zip up', 'zip-up'],
        'jackets': ['jacket', 'coat', 'puffer', 'windbreaker'],
        'shoes': ['shoe', 'shoes', 'sneaker', 'sneakers', 'boot', 'boots', 'footwear', 'kicks'],
        'accessories': ['accessory', 'accessories', 'hat', 'cap', 'bag', 'wallet', 'belt', 'backpack'],
        
        # Skate
        'skateboards': ['skateboard', 'deck', 'board', 'longboard'],
        
        # Coffee subcategories
        'coffee_pods': ['pod', 'pods', 'k-cup', 'kcup', 'capsule', 'capsules'],
        'coffee_beans': ['bean', 'beans', 'whole bean', 'ground coffee', 'roasted coffee', 'ground'],
        'tea': ['tea', 'loose leaf', 'rooibos', 'botanical', 'herbal'],
        'coffee_general': ['coffee', 'espresso', 'roast', 'blend'],
    }
    
    for category, terms in category_map.items():
        for term in terms:
            if term in query_lower:
                category_keywords = terms
                break
        if category_keywords:
            break
    
    # Color keywords (optional additional filter)
    color_keywords = []
    colors = ['black', 'white', 'red', 'blue', 'green', 'yellow', 'orange', 'purple', 'pink', 'gray', 'grey', 'brown', 'vintage']
    for color in colors:
        if color in query_lower:
            color_keywords.append(color)
    
    return min_price, max_price, category_keywords, color_keywords

def filter_products(products: List[dict], query: str) -> List[dict]:
    """Filter products by price, category, and color"""
    min_price, max_price, category_keywords, color_keywords = extract_filters(query)
    
    filtered = []
    for product in products:
        price = float(product.get('price', 0))
        
        # Price filter
        if not (min_price <= price <= max_price):
            continue
        
        name_lower = product.get('name', '').lower()
        category_lower = product.get('category', '').lower()
        
        # Category filter (if specified, MUST match)
        if category_keywords:
            if not any(kw in name_lower or kw in category_lower for kw in category_keywords):
                continue
        
        # Color filter (if specified, MUST match)
        if color_keywords:
            if not any(color in name_lower for color in color_keywords):
                continue
        
        filtered.append(product)
    
    return filtered

@router.post("/ask")
async def ask_agent(req: AskRequest, request: Request):
    """AI agent for product questions"""
    print(f"Agent question: {req.question} for business: {req.business_id}", flush=True)
    
    try:
        supabase = get_supabase_client()
        
        response = supabase.table('products') \
            .select('*') \
            .eq('business_id', req.business_id) \
            .eq('in_stock', True) \
            .limit(100) \
            .execute()
        
        all_products = response.data if response.data else []
        
        if not all_products:
            return {
                "answer": "I don't have any product information yet.",
                "products": []
            }
        
        print(f"Retrieved {len(all_products)} total products", flush=True)
        
        # Filter products
        filtered_products = filter_products(all_products, req.question)
        
        print(f"After filtering: {len(filtered_products)} products", flush=True)
        
        if not filtered_products:
            return {
                "answer": "I couldn't find any products matching that. Try adjusting your search.",
                "products": []
            }
        
        # Take top matches
        products_for_display = filtered_products[:req.k]
        
        # Format for AI (just basic info, no full descriptions)
        products_summary = "\n".join([
            f"- {p['name']}: ${p['price']:.2f}"
            for p in products_for_display[:5]  # Only show AI first 5
        ])
        
        # Call Claude with SHORT response requirement
        client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        
        prompt = f"""Customer asked: "{req.question}"

Matching products:
{products_summary}

Write a 1-2 sentence response. DO NOT list product names or prices (they're shown separately). Just give a brief helpful comment about what you found.

Examples:
- "I found some great options in your price range!"
- "Here are our black shirts currently in stock."
- "These are our most popular hoodies."

Keep it under 20 words."""

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=100,
            messages=[{"role": "user", "content": prompt}]
        )
        
        answer = message.content[0].text.strip()
        
        return {
            "answer": answer,
            "products": products_for_display
        }
    
    except Exception as e:
        print(f"Error: {e}", flush=True)
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))