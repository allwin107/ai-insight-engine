# AI Data Insight Engine

> Transform raw business data into actionable insights automatically — Replace your junior data analyst with AI.

## What It Does

Upload messy CSV/Excel files → Get cleaned data + smart visualizations + AI-generated business insights in minutes.

**Perfect for:**
- SMEs without data teams
- Product/marketing managers needing instant insights
- E-commerce stores seeking profit optimization
- Anyone who wants answers, not just charts

## Features (MVP)

✅ **Automated Data Cleaning** - Handles missing values, outliers, formatting issues  
✅ **Intelligent Visualizations** - 5-8 charts automatically selected  
✅ **AI Business Insights** - Narrative explanations of trends and profit impact  
✅ **PDF Reports** - Professional reports ready to share  
✅ **Zero Setup** - Just upload and go

## Tech Stack

- **Backend:** Python, FastAPI
- **Frontend:** Streamlit (MVP) → React (v2)
- **AI/ML:** Llama 3.1-8B, scikit-learn, AutoViz
- **Infrastructure:** Google Colab (LLM), Railway.app (API)
- **Cost:** $0 for MVP

## Quick Start

### Prerequisites

- Python 3.10+
- pip
- Git

### Installation

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/ai-insight-engine.git
cd ai-insight-engine

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Copy environment template
cp .env.example .env
# Edit .env with your settings

# Run backend
uvicorn app.main:app --reload

# In another terminal, run frontend
streamlit run frontend/app.py
```

### Running with Docker

```bash
docker-compose up --build
```

## Project Structure

```
ai-insight-engine/
├── app/                    # Backend API
│   ├── main.py            # FastAPI entry point
│   ├── config.py          # Configuration
│   ├── api/               # API endpoints
│   ├── auth/              # Authentication
│   ├── services/          # Business logic
│   ├── models/            # Database models
│   └── utils/             # Utilities
├── frontend/              # Streamlit frontend
│   ├── app.py            # Main app
│   ├── pages/            # Multi-page app
│   └── components/       # Reusable components
├── tests/                # Test suite
├── docs/                 # Documentation
├── scripts/              # Utility scripts
└── colab/               # Google Colab notebooks
```

## Development

### Running Tests

```bash
pytest tests/ -v --cov
```

### Code Quality

```bash
# Linting
ruff check .

# Formatting
black .

# Type checking
mypy app/
```

## Deployment

### Backend (Railway.app)

```bash
railway login
railway up
```

### Frontend (Streamlit Cloud)

Connect GitHub repo at https://streamlit.io/cloud

## Contributing

This is an MVP project. Contributions welcome after initial launch!

## License

MIT License - See LICENSE file

## Roadmap

- [x] Week 1-2: Foundation
- [ ] Week 3-4: Data cleaning pipeline
- [ ] Week 5-6: Visualization & AI insights
- [ ] Week 7-8: Dashboard UI
- [ ] Week 9-10: Export & testing
- [ ] Week 11-12: Launch

## Contact

Questions? Open an issue or email [your-email@example.com]

---

**Status:** 🚧 Under active development (Week 1/12)