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
    k: Optional[int] = 5

def extract_price_constraint(query: str):
    """
    Extract price constraints from natural language query
    Returns: (min_price, max_price) tuple
    """
    query_lower = query.lower()
    
    # Under/below/less than X
    under_match = re.search(r'(?:under|below|less than|cheaper than|max)\s*\$?(\d+(?:\.\d+)?)', query_lower)
    if under_match:
        return (0, float(under_match.group(1)))
    
    # Over/above/more than X
    over_match = re.search(r'(?:over|above|more than|at least)\s*\$?(\d+(?:\.\d+)?)', query_lower)
    if over_match:
        return (float(over_match.group(1)), float('inf'))
    
    # Between X and Y
    between_match = re.search(r'between\s*\$?(\d+(?:\.\d+)?)\s*(?:and|to|-)\s*\$?(\d+(?:\.\d+)?)', query_lower)
    if between_match:
        return (float(between_match.group(1)), float(between_match.group(2)))
    
    # Exactly X
    exact_match = re.search(r'(?:exactly|for|at)\s*\$?(\d+(?:\.\d+)?)', query_lower)
    if exact_match:
        price = float(exact_match.group(1))
        return (price - 5, price + 5)  # Allow $5 buffer
    
    return (0, float('inf'))

def extract_category_keywords(query: str):
    """
    Extract product categories/types from query
    Returns: list of keywords to match against product names
    """
    query_lower = query.lower()
    
    # Common product categories (expand this list as needed)
    categories = {
        'clothing': ['shirt', 'tshirt', 't-shirt', 'tee', 'top', 'blouse'],
        'outerwear': ['jacket', 'coat', 'hoodie', 'sweatshirt', 'sweater', 'cardigan'],
        'bottoms': ['pants', 'jeans', 'shorts', 'skirt', 'trouser'],
        'footwear': ['shoe', 'boot', 'sneaker', 'sandal', 'slipper', 'loafer'],
        'accessories': ['hat', 'cap', 'beanie', 'bag', 'belt', 'scarf', 'glove'],
        'sports': ['skateboard', 'deck', 'wheel', 'truck', 'grip tape', 'board'],
    }
    
    found_keywords = []
    
    # Check each category
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in query_lower:
                found_keywords.append(keyword)
    
    # Also look for color modifiers
    colors = ['black', 'white', 'red', 'blue', 'green', 'yellow', 'orange', 'purple', 'pink', 'gray', 'grey', 'brown']
    for color in colors:
        if color in query_lower:
            found_keywords.append(color)
    
    # Look for brand names (if mentioned)
    brand_match = re.search(r'\b(nike|adidas|champion|vans|atlas|etc)\b', query_lower)
    if brand_match:
        found_keywords.append(brand_match.group(1))
    
    return found_keywords

def filter_products(products: List[dict], query: str) -> List[dict]:
    """
    Filter products based on price and category constraints in query
    """
    # Extract constraints
    min_price, max_price = extract_price_constraint(query)
    category_keywords = extract_category_keywords(query)
    
    filtered = []
    
    for product in products:
        # Price filter
        price = float(product.get('price', 0))
        if not (min_price <= price <= max_price):
            continue
        
        # Category filter (if keywords found)
        if category_keywords:
            product_name = product.get('name', '').lower()
            product_desc = product.get('description', '').lower()
            
            # Check if ANY keyword matches
            matches = any(
                keyword in product_name or keyword in product_desc 
                for keyword in category_keywords
            )
            
            if not matches:
                continue
        
        filtered.append(product)
    
    return filtered

@router.post("/ask")
async def ask_agent(req: AskRequest, request: Request):
    """
    Ask the AI agent a question about products for a specific business
    """
    print(f"Agent question: {req.question} for business: {req.business_id}", flush=True)
    
    try:
        # Get Supabase client
        supabase = get_supabase_client()
        
        # Retrieve products for this business (vector search would go here)
        # For now, simple retrieval by business_id
        response = supabase.table('products') \
            .select('*') \
            .eq('business_id', req.business_id) \
            .eq('in_stock', True) \
            .limit(50) \
            .execute()
        
        all_products = response.data if response.data else []
        
        if not all_products:
            return {
                "answer": "I don't have any product information for this business yet. Please check back later!",
                "products": []
            }
        
        print(f"Retrieved {len(all_products)} total products", flush=True)
        
        # Apply filters based on query
        filtered_products = filter_products(all_products, req.question)
        
        print(f"After filtering: {len(filtered_products)} products", flush=True)
        
        if not filtered_products:
            # No products match filters - provide helpful message
            return {
                "answer": "I couldn't find any products matching those specific criteria. Would you like to see what else is available, or adjust your requirements?",
                "products": []
            }
        
        # Limit to top matches for LLM context
        products_for_llm = filtered_products[:req.k]
        
        # Format products for LLM
        products_text = "\n\n".join([
            f"Product: {p['name']}\nPrice: ${p['price']}\nDescription: {p.get('description', 'N/A')}"
            for p in products_for_llm
        ])
        
        # Call Claude to generate natural response
        client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        
        prompt = f"""You are a helpful shopping assistant for a retail business. A customer asked: "{req.question}"

Here are the relevant products that match their criteria:

{products_text}

Provide a friendly, concise response that:
1. Directly answers their question
2. Highlights the most relevant products (maximum 3-4)
3. Mentions key features like price, style, or benefits
4. Keeps the tone conversational and helpful

Keep your response under 150 words."""

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        answer = message.content[0].text
        
        return {
            "answer": answer,
            "products": products_for_llm  # Return filtered products for display
        }
    
    except Exception as e:
        print(f"Error in agent: {e}", flush=True)
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))