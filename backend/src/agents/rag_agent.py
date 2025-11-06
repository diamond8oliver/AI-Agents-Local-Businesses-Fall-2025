from typing import Dict, List
from openai import OpenAI
from src.database.supabase_client import get_supabase_client

SYSTEM_PROMPT = (
    "You are a helpful AI assistant for a local business. "
    "Answer questions about products, inventory, pricing, and comparisons. "
    "Use only the provided product data to answer. If the answer is not found, say you don't know."
)

def search_products(query: str, business_id: str = "4644670e-936f-4688-87ed-b38d0f9a8f47", k: int = 5) -> List[Dict]:
    """Search products by name or description"""
    supabase = get_supabase_client()
    
    # Search in name and description fields
    response = supabase.table("products")\
        .select("*")\
        .eq("business_id", business_id)\
        .or_(f"name.ilike.%{query}%,description.ilike.%{query}%")\
        .limit(k)\
        .execute()
    
    return response.data if response.data else []

def answer_question(question: str, k: int = 5, model: str = "gpt-4o-mini") -> Dict:
    """Answer questions about products using Supabase data"""
    client = OpenAI()
    
    # Extract keywords from question for better search
    keywords = question.lower().split()
    products = []
    
    # Try searching with different keywords
    for keyword in keywords:
        if len(keyword) > 3:  # Skip short words
            results = search_products(keyword, k=k)
            products.extend(results)
    
    # Remove duplicates
    unique_products = {p['id']: p for p in products}.values()
    
    # Build context from products
    if unique_products:
        context_blocks = []
        for product in list(unique_products)[:k]:
            block = f"Product: {product.get('name', 'N/A')}\n"
            block += f"Price: ${product.get('price', 'N/A')}\n"
            if product.get('description'):
                block += f"Description: {product.get('description')}\n"
            if product.get('category'):
                block += f"Category: {product.get('category')}\n"
            if product.get('brand'):
                block += f"Brand: {product.get('brand')}\n"
            if product.get('url'):
                block += f"URL: {product.get('url')}\n"
            context_blocks.append(block)
        context = "\n\n".join(context_blocks)
    else:
        context = "No products found matching the query."
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"PRODUCTS:\n{context}\n\nQUESTION: {question}"},
    ]
    
    chat = client.chat.completions.create(model=model, messages=messages, temperature=0.2)
    answer = chat.choices[0].message.content
    
    return {
        "answer": answer,
        "products": [{"name": p.get("name"), "price": p.get("price"), "url": p.get("url")} for p in list(unique_products)[:k]]
    }
