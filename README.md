# AI Data Insight Engine

> Transform raw business data into actionable insights automatically — Replace your junior data analyst with AI.

## 🚀 **Week 1 Complete! Foundation Built.**

**Current Status:** MVP Development - Week 1/12 ✅  
**Features Completed:** Authentication, File Upload, Job Tracking, Testing Framework, Docker

## What It Does

Upload messy CSV/Excel files → Get cleaned data + smart visualizations + AI-generated business insights in minutes.

**Perfect for:**
- SMEs without data teams
- Product/marketing managers needing instant insights
- E-commerce stores seeking profit optimization
- Anyone who wants answers, not just charts

## ✨ Features (Implemented)

✅ **User Authentication** - Secure JWT-based auth with bcrypt password hashing  
✅ **File Upload System** - CSV/Excel support with validation (size, type, magic bytes)  
✅ **Job Tracking** - Real-time status tracking and job management  
✅ **Database** - SQLite with SQLAlchemy ORM  
✅ **Testing Framework** - Pytest with 70%+ code coverage  
✅ **Docker Support** - Full containerization with docker-compose  
✅ **API Documentation** - Auto-generated with FastAPI  
✅ **Structured Logging** - Production-ready logging with structlog

## 🏗️ Tech Stack

**Backend:**
- Python 3.11
- FastAPI (async web framework)
- SQLAlchemy (ORM)
- JWT Authentication
- Structured Logging

**Frontend:**
- Streamlit (rapid prototyping)
- React (planned for v2)

**AI/ML (Coming Week 3-6):**
- Llama 3.1-8B (self-hosted LLM)
- scikit-learn (data cleaning)
- AutoViz (chart generation)

**Infrastructure:**
- Docker & Docker Compose
- Google Colab (free LLM hosting)
- Railway.app (API deployment)

**Cost:** $0 for MVP ✨

## 🚀 Quick Start

### Prerequisites

- Python 3.11+ (3.10 also works)
- pip
- Git
- Docker (optional)

### Installation

#### Option 1: Local Development

```bash
# Clone repository
git clone https://github.com/allwin107/ai-insight-engine.git
cd ai-insight-engine

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Mac/Linux
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Copy environment template
cp .env.example .env
# Edit .env with your settings (SECRET_KEY, etc.)

# Initialize database (automatic on first run)
# Run backend
uvicorn app.main:app --reload

# In another terminal, run frontend
streamlit run frontend/app.py
```

**Access the app:**
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:8501

#### Option 2: Docker (Recommended for Testing)

```bash
# Clone repository
git clone https://github.com/allwin107/ai-insight-engine.git
cd ai-insight-engine

# Build and run with docker-compose
docker-compose up --build

# Access the app
# Backend: http://localhost:8000
# Frontend: http://localhost:8501

# Stop containers
docker-compose down
```

## 🧪 Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov --cov-report=html

# Run specific test file
pytest tests/test_auth.py -v

# Run tests with markers
pytest -m unit  # Only unit tests
pytest -m auth  # Only auth tests

# Use test script (generates HTML coverage report)
# Linux/Mac:
bash scripts/run_tests.sh

# Windows:
scripts\run_tests.bat
```

**View coverage report:** Open `htmlcov/index.html` in browser

## 📝 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user
- `GET /api/v1/auth/me` - Get current user info
- `POST /api/v1/auth/logout` - Logout user

### File Upload & Jobs
- `POST /api/v1/upload` - Upload CSV/Excel file
- `GET /api/v1/jobs/{job_id}` - Get job status
- `GET /api/v1/jobs` - List user's jobs
- `DELETE /api/v1/jobs/{job_id}` - Delete job

### Health & Info
- `GET /` - API information
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation

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

### Code Quality

```bash
# Linting
ruff check .

# Formatting
black .

# Type checking
mypy app/
```

### Project Structure

```
ai-insight-engine/
├── app/                    # Backend API
│   ├── main.py            # FastAPI entry point
│   ├── config.py          # Configuration
│   ├── database.py        # Database setup
│   ├── api/               # API endpoints
│   │   └── upload.py      # Upload endpoints
│   ├── auth/              # Authentication
│   │   ├── routes.py      # Auth endpoints
│   │   ├── schemas.py     # Pydantic models
│   │   └── security.py    # JWT & password hashing
│   ├── models/            # Database models
│   │   ├── user.py        # User model
│   │   └── job.py         # Job model
│   ├── services/          # Business logic (Week 3+)
│   └── utils/             # Utilities
│       ├── validation.py  # File validation
│       ├── helpers.py     # Helper functions
│       └── logging.py     # Structured logging
├── frontend/              # Streamlit frontend
│   ├── app.py            # Main app
│   ├── pages/            # Multi-page app (future)
│   └── components/       # Reusable components (future)
├── tests/                # Test suite
│   ├── conftest.py       # Pytest config
│   ├── test_auth.py      # Auth tests
│   ├── test_upload.py    # Upload tests
│   └── test_main.py      # Main API tests
├── scripts/              # Utility scripts
│   ├── test_auth.py      # Manual auth testing
│   ├── test_upload.py    # Manual upload testing
│   └── run_tests.sh      # Run test suite
├── docs/                 # Documentation
├── docker/               # Docker configs
├── Dockerfile            # Backend container
├── docker-compose.yml    # Multi-container setup
└── pytest.ini            # Test configuration
```

## 🎯 Development Roadmap

### ✅ Week 1-2: Foundation (COMPLETE)
- ✅ Project setup & CI/CD
- ✅ FastAPI backend with authentication
- ✅ Database setup (SQLite + SQLAlchemy)
- ✅ File upload with validation
- ✅ Job tracking system
- ✅ Streamlit frontend with auth
- ✅ Testing framework (pytest)
- ✅ Docker containerization
- ✅ Structured logging

### 📋 Week 3-4: Data Cleaning (NEXT)
- Data cleaning pipeline
- ML-based imputation
- Outlier detection
- Format standardization
- Quality scoring
- Cleaning logs

### 📊 Week 5-6: Visualizations & AI
- AutoViz integration
- Chart selection & ranking
- LLM integration (Google Colab)
- Business insight generation
- Confidence scoring

### 🎨 Week 7-8: Dashboard UI
- Results display
- Chart gallery
- Insight cards
- Real-time status updates
- UI/UX polish

### 📄 Week 9-10: Export & Testing
- PDF generation
- Cleaned data export
- End-to-end testing
- Load testing
- Security audit
- Bug fixes

### 🚀 Week 11-12: Launch
- Beta testing (10 users)
- Documentation
- User onboarding
- Public launch (Product Hunt)
- Feedback collection
- Go/No-Go decision

## 📊 Current Metrics

**Code Coverage:** 70%+ (target: 80%)  
**API Endpoints:** 10 implemented  
**Database Models:** 2 (User, Job)  
**Tests:** 25+ test cases  
**Documentation:** API docs auto-generated

## Contributing

This is an MVP project under active development. Contributions welcome after initial launch!

## License

MIT License - See LICENSE file

## Contact

Questions? Open an issue or email [allwin10raja@gmail.com]

---

**Status:** 🚧 Week 1/12 Complete - Starting Data Cleaning Pipeline  
**Last Updated:** December 2024  
**Next Milestone:** Data cleaning module (Week 3)