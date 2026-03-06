# Evaluador RAG API

FastAPI backend for AI-powered GitHub repository evaluation using RAG (Retrieval-Augmented Generation).

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FastAPI Application                     │
├─────────────────────────────────────────────────────────────────┤
│  Routers (API Endpoints)                                        │
│  ├── /rubrics → Rubric CRUD operations                          │
│  ├── /evaluations → Evaluation CRUD & processing                │
│  └── /health → System health checks                             │
├─────────────────────────────────────────────────────────────────┤
│  Services (Business Logic)                                      │
│  ├── RubricServiceAPI → Handles rubric operations               │
│  ├── EvaluationServiceAPI → Handles evaluation operations       │
│  └── pdf_processor → PDF text extraction for RAG                │
├─────────────────────────────────────────────────────────────────┤
│  Schemas (Pydantic Validation)                                  │
│  ├── RubricResponse, RubricResponseWithCriteria                 │
│  ├── CriterionResponse, CriterionResponseWithLevels             │
│  ├── LevelResponse, APIResponse                                 │
│  ├── EvaluationRequest, EvaluationResponse                      │
│  └── EvaluationResponseWithFindings, FindingResponse            │
├─────────────────────────────────────────────────────────────────┤
│  Models (SQLAlchemy ORM)                                        │
│  ├── Rubric Architecture: Rubric → Criterion → Level            │
│  └── Evaluation Engine: Evaluation → Finding                    │
├─────────────────────────────────────────────────────────────────┤
│  Core (Infrastructure)                                          │
│  ├── database.py → PostgreSQL connection                        │
│  ├── settings.py → Configuration management                     │
│  ├── logging_config.py → Colored logging                        │
│  ├── exception_handlers.py → Error handling                     │
│  └── messages.py → Centralized message strings                  │
└─────────────────────────────────────────────────────────────────┘
```

## 🛠️ Tech Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11 | Runtime environment |
| FastAPI | 0.109.0 | Web framework |
| Uvicorn | 0.27.0 | ASGI server with hot-reload |
| SQLAlchemy | 2.0.25 | ORM |
| Alembic | 1.13.1 | Database migrations |
| psycopg2 | 2.9.9 | PostgreSQL adapter |
| LangChain | 0.1.9 | AI/LLM framework |
| LangChain OpenAI | 0.0.8 | OpenAI integrations |
| FAISS | 1.7.4 | Vector similarity search |
| PyPDF | 4.0.1 | PDF processing |
| TikToken | 0.6.0 | Token counting |
| Pydantic | 2.x | Data validation |
| pytest | 8.0.0 | Testing framework |

## 📁 Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── models.py               # SQLAlchemy ORM models
├── requirements.txt        # Python dependencies
├── pytest.ini              # pytest configuration
├── Dockerfile.dev          # Development Docker container
├── .env.template           # Environment variables template
│
├── core/                   # Infrastructure & configuration
│   ├── __init__.py
│   ├── database.py         # Database connection & session management
│   ├── settings.py         # Pydantic settings (env vars)
│   ├── logging_config.py   # Colored logging setup
│   ├── exception_handlers.py  # Global exception handlers
│   └── messages.py         # Centralized message strings
│
├── routers/                # API route definitions
│   ├── __init__.py
│   ├── rubrics.py          # Rubric endpoints
│   └── evaluations.py      # Evaluation endpoints
│
├── schemas/                # Pydantic validation schemas
│   ├── __init__.py
│   ├── response.py         # APIResponse wrapper schema
│   ├── rubric.py           # Rubric-related schemas
│   └── evaluation.py       # Evaluation-related schemas
│
├── services/               # Business logic layer
│   ├── __init__.py
│   ├── rubric_service_api.py    # Rubric CRUD operations
│   ├── evaluation_service_api.py # Evaluation CRUD operations
│   └── pdf_processor.py    # PDF processing utilities
│
└── tests/                  # Test suite
    ├── __init__.py
    ├── conftest.py         # pytest fixtures
    └── services/           # Service-level tests
        ├── test_rubric_service_api.py
        └── test_evaluation_service_api.py
```

## 🗄️ Database Schema

### Entity Relationship Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                    RUBRIC ARCHITECTURE (The "Rules")             │
│                                                                  │
│  Rubric (1) ─────────< Criterion (N) ─────────< Level (N)        │
│      │                                                           │
│      │                                                           │
│      └──────────< Evaluation (N) ─────────< Finding (N)          │
│                          │                      │                │
│                          │                      │                │
│                          └──────────────────────┘                │
│                                                 │                │
│                          EVALUATION ENGINE      │                │
│                          (The "History")        │                │
│                                          ───────┴───────         │
│                                          Criterion <─────┘       │
│                                              Level <─────┘       │
└──────────────────────────────────────────────────────────────────┘
```

### Domain Models

#### Rubric Architecture

| Model | Description |
|-------|-------------|
| **Rubric** | Root container for grading checklists (e.g., "Backend Final Project") |
| **Criterion** | Individual evaluation dimension (e.g., "Error Handling", "Code Quality") |
| **Level** | Scoring options within each criterion (e.g., "Excellent" = 4 pts) |

#### Evaluation Engine

| Model | Description |
|-------|-------------|
| **Evaluation** | Record of a repository analysis run with scoring results |
| **Finding** | WHIS data point: Where-How-Improvement-Score for each criterion |

## 📡 API Endpoints

### System Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Welcome message with API info |
| GET | `/health` | Health check with database connectivity test |

### Rubric Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/rubrics` | List all rubrics (without criteria) |
| GET | `/api/v1/rubrics/{rubric_id}` | Get rubric by ID with full details |
| POST | `/api/v1/rubrics` | Create a new rubric with criteria and levels |
| PUT | `/api/v1/rubrics/{rubric_id}` | Update a rubric's basic information |
| DELETE | `/api/v1/rubrics/{rubric_id}` | Delete a rubric |

### Evaluation Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/evaluations` | List all evaluations (without findings) |
| GET | `/api/v1/evaluations/{evaluation_id}` | Get evaluation by ID with full findings |
| POST | `/api/v1/evaluations` | Create a new evaluation (async processing) |

### Response Format

All endpoints return a standardized `APIResponse` wrapper:

```json
{
  "success": true,
  "data": { ... },
  "errors": null,
  "message": "Operation completed successfully"
}
```

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## ⚙️ Configuration

### Environment Variables

Create a `.env` file from the template:

```bash
cp .env.template .env
```

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `POSTGRES_USER` | ✅ | - | PostgreSQL username |
| `POSTGRES_PASSWORD` | ✅ | - | PostgreSQL password |
| `POSTGRES_DB` | ✅ | - | Database name |
| `DB_HOST` | ✅ | `db` | Database host |
| `DB_PORT` | ✅ | `5432` | Database port |
| `OPENAI_API_KEY` | ✅ | - | OpenAI API key for AI features |
| `GEMINI_API_KEY` | ❌ | - | Gemini API key (optional) |
| `API_V1_PREFIX` | ❌ | `/api/v1` | API version prefix |
| `APP_TITLE` | ❌ | `Evaluador RAG API` | Application title |
| `APP_VERSION` | ❌ | `1.0.0` | Application version |

## 🚀 Installation & Running

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (v20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (v2.0+) or Docker Compose V1 (`docker-compose`)

### Development with Docker-in-Docker (Recommended)

This project uses a Docker-in-Docker development environment with a devcontainer for seamless development:

1. **Configure environment:**
   ```bash
   cp .env.template .env
   # Edit .env with your settings
   ```

2. **Start the development environment:**
   ```bash
   # From project root
   ./manage.sh backend   # Start database + backend
   ./manage.sh all       # Start all services
   ```

3. **Access the backend:**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs

### Local Development (Alternative)

For local development without Docker:

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.template .env
   # Edit .env with your settings
   ```

3. **Run the server:**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### Docker Development

Use the root-level management script:

```bash
# From project root
./manage.sh backend   # Start database + backend
./manage.sh all       # Start all services
```

## 🧪 Testing

### Run All Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=. --cov-report=html
```

### Test Structure

```
tests/
├── conftest.py                    # Shared fixtures
│   ├── test_engine                # In-memory SQLite database
│   ├── db_session                 # Database session per test
│   ├── sample_rubric              # Single rubric fixture
│   ├── sample_rubrics             # Multiple rubrics fixture
│   ├── rubric_with_criteria       # Complete rubric structure
│   └── rubric_service             # Service instance
│
└── services/
    ├── test_rubric_service_api.py     # RubricServiceAPI tests
    └── test_evaluation_service_api.py # EvaluationServiceAPI tests
```

### Test Database

Tests use an in-memory SQLite database for isolation and speed. Each test gets a fresh database schema.

## 📝 Development Guidelines

### Adding a New Endpoint

1. **Create schema** in `schemas/` for request/response models
2. **Create service method** in `services/` for business logic
3. **Create router endpoint** in `routers/` with dependency injection
4. **Register router** in `main.py` if creating a new router file

### Dependency Injection Pattern

```python
# Define dependency provider
def get_rubric_service() -> RubricServiceAPI:
    return RubricServiceAPI()

# Use in endpoint
@router.get("/")
def list_rubrics(
    db: Session = Depends(get_db),
    service: RubricServiceAPI = Depends(get_rubric_service)
):
    return service.get_all(db)
```

### Adding a New Model

1. **Define model** in `models.py` extending `Base`
2. **Create schema** in `schemas/` for serialization
3. **Create service** in `services/` for operations
4. **Create migration** with Alembic (if using migrations)

## 📖 Related Documentation

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [LangChain Documentation](https://python.langchain.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

## 📄 License

This project is part of the Bootcamp-IA-P5 organization.