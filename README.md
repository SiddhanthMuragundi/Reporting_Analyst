# Research Portal

AI-powered financial analysis tool that extracts structured data from financial statements and summarizes earnings call transcripts.

## Features

**Financial Statement Extraction**
- Upload financial statement PDFs
- Extracts income statement line items into structured format
- Generates downloadable Excel output with metadata
- Handles multiple periods/quarters
- Auto-detects currency and scale

**Earnings Call Summarization**
- Upload earnings call transcript PDFs
- Analyzes management tone and confidence
- Extracts key positives, concerns, and forward guidance
- Identifies growth initiatives

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, Claude Sonnet 4, pandas, openpyxl |
| Frontend | Vue.js 3, Axios |
| AI | Anthropic API |

## Architecture

```
research-portal/
├── README.md                    # This file
├── backend/                     # FastAPI backend
│   ├── main.py
│   ├── requirements.txt
│   ├── test_api.py
│   ├── outputs/                # Generated Excel files (auto-created)
│   └── Dockerfile
└── frontend/                    # Vue.js frontend
    ├── src/
    │   ├── App.vue
    │   └── main.js
    ├── public/
    │   └── index.html
    ├── package.json
    └── vue.config.js
```

## API Reference

| Endpoint | Method | Description | Avg. Time |
|---|---|---|---|
| `/api/extract-financials` | POST | Upload financial statement PDF, returns Excel file | 15 to 30s |
| `/api/summarize-earnings-call` | POST | Upload earnings call PDF, returns structured JSON summary | 10 to 20s |
| `/api/download/{filename}` | GET | Download generated Excel file | n/a |

Interactive API docs available at `/docs` on the running backend.

## Local Setup

**Requirements:** Python 3.9+, Node.js 16+, Anthropic API key

```bash
# Backend
cd backend
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your-key-here
uvicorn main:app --host 0.0.0.0 --port 8000
```

```bash
# Frontend (new terminal)
cd frontend
npm install
npm run serve
```

App runs at `http://localhost:8080`, backend at `http://localhost:8000`.

## Cost

- ~$0.03 per financial extraction, ~$0.02 per earnings summary (Anthropic API)

## License

MIT
