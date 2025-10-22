# AI Shopping Assistant Platform for Local Businesses

A complete SaaS platform that provides local businesses with AI-powered shopping assistants. Built by Syracuse University students for the Syracuse business community.

## What It Does

Helps customers find products instantly through natural language chat - like having your best salesperson available 24/7 on your website.

**Example:**
- Customer: "Show me black boots under $150"
- AI: Returns exact matches with prices, links, and recommendations

## Key Features

### Smart Product Search
- Natural language understanding ("shoes under $100")
- Price range filtering
- Size, color, and availability filtering
- Product comparisons
- Personalized recommendations
- Upsell/cross-sell suggestions

### Automatic Product Management
- Auto-crawls business websites on signup
- Daily automatic updates (2am)
- Supports Shopify and generic websites
- Extracts: name, price, description, images, variants, stock status

### Embeddable Widget
- Customizable colors, position, and icon
- Mobile responsive
- Real-time chat interface
- Clickable product links
- Conversation memory

### Analytics & Limits
- Conversation tracking
- Usage statistics (30-day views)
- Pricing tier enforcement (Free/Starter/Pro)
- Products per query metrics

### Business Dashboard
- Widget code generator
- Product inventory viewer
- Analytics dashboard
- Business profile management

## Tech Stack

**Backend:** FastAPI, Python 3.11, OpenAI GPT-4o-mini
**Database:** Supabase (PostgreSQL)
**Deployment:** Railway
**Frontend:** Next.js, React, Tailwind CSS
**Auth:** Clerk

## Quick Start

### Prerequisites
- Python 3.11
- OpenAI API key
- Supabase account
- Clerk account (for dashboard)

### Installation

1. **Clone and setup**
```bash
   cd backend
   python3.11 -m venv .venv311
   source .venv311/bin/activate
   pip install -r requirements.txt
```

2. **Environment variables**
```bash
   export OPENAI_API_KEY="your-key"
   export SUPABASE_URL="your-url"
   export SUPABASE_KEY="your-key"
   export DATABASE_URL="your-postgres-url"
   export REDIS_URL="your-redis-url"
```

3. **Run locally**
```bash
   uvicorn src.api.main:app --host 0.0.0.0 --port 8012 --reload
```

4. **API Documentation**
   Visit: http://localhost:8012/docs

## API Endpoints

### Core Features
- `POST /product-crawl/` - Crawl website and extract products
- `POST /smart-agent/ask` - AI product search
- `GET /widget/settings/{business_id}` - Widget customization
- `POST /webhooks/business-created` - Auto-crawl on signup

### Analytics
- `GET /analytics/stats/{business_id}` - Usage statistics
- `POST /analytics/log-conversation` - Log conversations

### Management
- `GET /tiers/list` - Available pricing tiers
- `GET /tiers/check-limits/{business_id}` - Usage limits
- `POST /scheduled/crawl-all-businesses` - Daily cron job

## Deployment

**Backend (Railway):**
- Connected to: `Cuse-AI/AI-Agents-Local-Businesses-Fall-2025/backend`
- Auto-deploys on push to main
- Cron job runs daily at 2am

**Dashboard:**
- Deploy to Vercel
- Connect to backend API

## Project Structure
```
AI-Agents-Local-Businesses-Fall-2025/
├── backend/                    # Python FastAPI backend
│   ├── src/
│   │   ├── agents/            # Smart agent logic
│   │   ├── api/routes/        # API endpoints
│   │   ├── scrapers/          # Website crawlers
│   │   ├── services/          # Business logic
│   │   ├── middleware/        # Error handling
│   │   └── config/            # Settings
│   ├── widget/                # Embeddable JavaScript widget
│   └── requirements.txt
├── dashboard/                  # Next.js business dashboard
└── docs/                      # Documentation
```

## Widget Installation

Add to any website:
```html
<script src="https://web-production-902d.up.railway.app/widget/widget.js" 
        data-api-key="YOUR_BUSINESS_ID"></script>
```

## Pricing Tiers

- **Free**: 50 products, 100 conversations/month
- **Starter ($49/mo)**: 500 products, 1000 conversations/month
- **Pro ($99/mo)**: 5000 products, 10000 conversations/month

## Development
```bash
# Format code
black src/

# Run tests
pytest

# Update requirements
pip freeze > requirements.txt
```

## Team

Built by Syracuse University students for local Syracuse businesses.

**Contributors:** 
Oliver Diamond
Ryan Walsh
Logan Brown
Ignacio Marro
Jake Machemer

## License

MIT License

## Support

For Syracuse businesses: Contact us for free setup assistance!
