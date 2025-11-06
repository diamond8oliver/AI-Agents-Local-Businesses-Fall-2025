from typing import Dict, List
from anthropic import Anthropic
from src.database.supabase_client import get_supabase_client
import re
import os

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

SMART_SYSTEM_PROMPT = """You are an intelligent shopping assistant for a local business.

Your capabilities:
1. Product search with natural filters (price, size, color, brand, category)
2. Product recommendations based on user needs
3. Product comparisons highlighting key differences
4. Upsell/cross-sell suggestions
5. Stock awareness
6. Remember conversation context

When answering:
- Be helpful and conversational
- Reference previous questions when relevant
- Highlight key product features
- Mention prices clearly
- Note stock status
- Suggest alternatives when needed"""

def detect_intent(question: str) -> List[str]:
    intents = []
    question_lower = question.lower()
    
    compare_words = ['compare', 'difference', 'versus', 'vs', 'better than']
    recommend_words = ['recommend', 'suggest', 'best', 'what should', 'which']
    search_words = ['show', 'find', 'search', 'looking for', 'need', 'want']
    
    if any(word in question_lower for word in compare_words):
        intents.append('compare')
    if any(word in question_lower for word in recommend_words):
        intents.append('recommend')
    if any(word in question_lower for word in search_words):
        intents.append('search')
    
    return intents if intents else ['search']

def extract_filters(question: str) -> Dict:
    filters = {}
    question_lower = question.lower()
    
    price_patterns = [
        r'under\s+\$?(\d+)',
        r'below\s+\$?(\d+)',
        r'less than\s+\$?(\d+)',
        r'between\s+\$?(\d+)\s+and\s+\$?(\d+)'
    ]
    
    for pattern in price_patterns:
        match = re.search(pattern, question_lower)
        if match:
            if len(match.groups()) == 2:
                filters['min_price'] = int(match.group(1))
                filters['max_price'] = int(match.group(2))
            else:
                filters['max_price'] = int(match.group(1))
    
    colors = ['black', 'white', 'red', 'blue', 'green', 'yellow', 'orange', 'purple', 'pink', 'brown', 'gray', 'grey']
    for color in colors:
        if color in question_lower:
            filters['color'] = color
    
    size_match = re.search(r'size\s+(\d+\.?\d*|small|medium|large|xl|xxl)', question_lower)
    if size_match:
        filters['size'] = size_match.group(1)
    
    return filters

def search_products_smart(query: str, filters: Dict, business_id: str, k: int = 10) -> List[Dict]:
    supabase = get_supabase_client()
    
    query_builder = supabase.table("products").select("*").eq("business_id", business_id)
    
    if 'max_price' in filters:
        query_builder = query_builder.lte("price", filters['max_price'])
    if 'min_price' in filters:
        query_builder = query_builder.gte("price", filters['min_price'])
    
    keywords = [w for w in query.lower().split() if len(w) > 3]
    if keywords:
        search_conditions = []
        for keyword in keywords[:3]:
            search_conditions.extend([
                f"name.ilike.%{keyword}%",
                f"description.ilike.%{keyword}%",
                f"category.ilike.%{keyword}%",
                f"brand.ilike.%{keyword}%"
            ])
        if search_conditions:
            query_builder = query_builder.or_(",".join(search_conditions))
    
    response = query_builder.limit(k * 2).execute()
    products = response.data if response.data else []
    
    filtered = []
    for p in products:
        if 'color' in filters:
            colors = p.get('colors', [])
            if isinstance(colors, list):
                colors_str = ' '.join(str(c).lower() for c in colors)
                if filters['color'] not in colors_str:
                    continue
        
        if 'size' in filters:
            sizes = p.get('sizes', [])
            if isinstance(sizes, list):
                sizes_str = ' '.join(str(s).lower() for s in sizes)
                if filters['size'] not in sizes_str:
                    continue
        
        filtered.append(p)
    
    return filtered[:k]

def answer_question_smart(question: str, business_id: str, k: int, conversation_history: List[Dict] = None) -> Dict:
    intents = detect_intent(question)
    filters = extract_filters(question)
    products = search_products_smart(question, filters, business_id, k)
    
    if products:
        context_blocks = []
        for i, product in enumerate(products, 1):
            block = f"{i}. {product.get('name', 'N/A')}\n"
            block += f"   Price: ${product.get('price', 'N/A')}\n"
            if product.get('description'):
                desc = product.get('description', '')[:200]
                block += f"   Description: {desc}\n"
            if product.get('brand'):
                block += f"   Brand: {product.get('brand')}\n"
            if product.get('category'):
                block += f"   Category: {product.get('category')}\n"
            if product.get('colors'):
                block += f"   Colors: {product.get('colors')}\n"
            if product.get('sizes'):
                block += f"   Sizes: {product.get('sizes')}\n"
            block += f"   In Stock: {'Yes' if product.get('in_stock') else 'No'}\n"
            if product.get('url'):
                block += f"   URL: {product.get('url')}\n"
            context_blocks.append(block)
        context = "\n".join(context_blocks)
    else:
        context = "No products found."
    
    history_text = ""
    if conversation_history:
        history_text = "\n\nPREVIOUS CONVERSATION:\n"
        for msg in conversation_history[-3:]:
            history_text += f"User: {msg['question']}\nAssistant: {msg['answer'][:100]}...\n\n"
    
    intent_instruction = ""
    if 'compare' in intents:
        intent_instruction = "\n\nThe user wants to COMPARE products."
    elif 'recommend' in intents:
        intent_instruction = "\n\nThe user wants RECOMMENDATIONS."
    
    user_prompt = f"""PRODUCTS:
{context}
{history_text}
CURRENT QUESTION: {question}
{intent_instruction}

Remember context from previous messages and provide helpful, conversational responses."""
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=SMART_SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": user_prompt}
        ]
    )
    
    answer = message.content[0].text
    
    return {
        "answer": answer,
        "products": [{
            "name": p.get("name"),
            "price": p.get("price"),
            "url": p.get("url"),
            "in_stock": p.get("in_stock", True)
        } for p in products],
        "intents_detected": intents,
        "filters_applied": filters
    }
