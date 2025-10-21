# Local Business AI Agent Platform

An AI agent system that enables local businesses to automate customer interactions 24/7 while maintaining human oversight and control.

## Features

- **Website Crawling & Knowledge Base**: Automatically crawls business websites and creates searchable knowledge bases
- **RAG-Powered Agent**: Uses Retrieval Augmented Generation for accurate, context-aware responses
- **Tool Integration**: Connects to Google Calendar, CRM systems, and other business tools
- **Multi-Channel Support**: Website chat, voice calls, and SMS
- **Monitoring Dashboard**: Real-time conversation monitoring with human takeover capabilities

## Quick Start

1. **Create & Activate Virtualenv (Python 3.11 recommended)**
   ```bash
   python3.11 -m venv .venv311
   source .venv311/bin/activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Environment Variables**
   ```bash
   # Required
   export OPENAI_API_KEY="<your-key>"
   # Ensure local imports resolve
   export PYTHONPATH=src
   ```

4. **Run the API Server**
   ```bash
   uvicorn api.main:app --host 127.0.0.1 --port 8012
   # Docs: http://127.0.0.1:8012/docs
   # Health: http://127.0.0.1:8012/health
   ```

5. **Example Requests**
   ```bash
   # Crawl a site into the knowledge base
   curl -X POST http://127.0.0.1:8012/crawl \
     -H 'Content-Type: application/json' \
     -d '{"start_url":"https://example.com","max_pages":5}'

   # Ask a question (requires that you have crawled some pages)
   curl -X POST http://127.0.0.1:8012/agent/ask \
     -H 'Content-Type: application/json' \
     -d '{"question":"What products does this store sell?"}'

   # Health check
   curl http://127.0.0.1:8012/health
   ```

## Project Structure

```
local_business_ai_agent/
├── src/
│   ├── agents/          # AI agent core logic
│   ├── crawlers/        # Website crawling functionality
│   ├── database/        # Database models and connections
│   ├── integrations/    # External API integrations
│   ├── dashboard/       # Streamlit dashboard
│   └── api/             # FastAPI backend
├── tests/              # Test files
├── config/             # Configuration files
├── docs/               # Documentation
└── static/             # Static assets
```

## Configuration

See `.env.example` for all required environment variables.

## Development

- Run tests: `pytest`
- Format code: `black src/`
- Type checking: `mypy src/`

## License

MIT License
