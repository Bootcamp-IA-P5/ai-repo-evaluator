# Evaluador RAG API

FastAPI backend for AI-powered GitHub repository evaluation using RAG (Retrieval-Augmented Generation).

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FastAPI Application                     │
├─────────────────────────────────────────────────────────────────┤
│  Routers (API Endpoints)                                        │
│  ├── /rubrics → Rubric CRUD operations                          │
│  ├── /evaluations → Evaluation CRUD & AI processing             │
│  ├── /evaluations/briefings → File upload for briefings         │
│  └── /health → System health checks                             │
├─────────────────────────────────────────────────────────────────┤
│  Services (Business Logic)                                      │
│  ├── AIEvaluationEngine → Core AI evaluation orchestrator       │
│  ├── AIClient → Multi-provider AI client (OpenAI, Gemini, Groq) │
│  ├── ContextEngine → FAISS-based RAG vector search              │
│  ├── GitLoaderService → Repository cloning & code analysis      │
│  ├── BriefingProcessor → PDF processing for RAG context         │
│  ├── RubricServiceAPI → Handles rubric operations               │
│  ├── EvaluationServiceAPI → Handles evaluation operations       │
│  └── FileUploadService → File upload handling                   │
├─────────────────────────────────────────────────────────────────┤
│  Schemas (Pydantic Validation)                                  │
│  ├── RubricResponse, RubricResponseWithCriteria                 │
│  ├── CriterionResponse, CriterionResponseWithLevels             │
│  ├── LevelResponse, APIResponse                                 │
│  ├── EvaluationRequest, EvaluationResponse                      │
│  ├── EvaluationResponseWithFindings, FindingResponse            │
│  └── UploadResponse → File upload responses                     │
├─────────────────────────────────────────────────────────────────┤
│  Models (SQLAlchemy ORM)                                        │
│  ├── Rubric Architecture: Rubric → Criterion → Level            │
│  └── Evaluation Engine: Evaluation → Finding                    │
├─────────────────────────────────────────────────────────────────┤
│  Core (Infrastructure)                                          │
│  ├── database.py → PostgreSQL connection                        │
│  ├── settings.py → Configuration management (AI providers)      │
│  ├── logging_config.py → Colored logging                        │
│  ├── exception_handlers.py → Error handling                     │
│  └── messages.py → Centralized message strings                  │
├─────────────────────────────────────────────────────────────────┤
│  AI & RAG Components                                            │
│  ├── prompts.py → Centralized prompt templates                  │
│  ├── ai_client.py → Multi-provider AI integration               │
│  ├── context_engine.py → FAISS vector store for semantic search │
│  ├── git_loader.py → Code repository processing                 │
│  └── pdf_processor.py → PDF document processing                 │
└─────────────────────────────────────────────────────────────────┘
```

### AI Evaluation Workflow

```
1. Repository Analysis
   ├── GitLoaderService clones repository
   ├── LanguageParser processes source code
   ├── Notebook extraction for .ipynb files
   └── Configuration file processing

2. RAG Context Building
   ├── BriefingProcessor extracts PDF requirements
   ├── ContextEngine builds FAISS vector index
   └── Semantic search for relevant context

3. AI Evaluation
   ├── AIEvaluationEngine orchestrates evaluation
   ├── AIClient calls selected AI provider
   ├── Multi-criterion evaluation with WHIS methodology
   └── Score calculation and aggregation

4. Result Generation
   ├── Finding creation with evidence
   ├── Total score calculation (100-point scale)
   └── AI-generated summary report
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
| LangChain | 1.2.10 | AI/LLM framework |
| LangChain Community | 0.4.1 | LangChain ecosystem extensions |
| LangChain Core | 1.2.16 | Core LangChain functionality |
| LangChain OpenAI | 1.1.10 | OpenAI integrations |
| LangChain Google GenAI | 4.2.1 | Google Gemini integrations |
| FAISS | 1.13.2 | Vector similarity search |
| PyPDF | 6.0.0 | PDF processing |
| TikToken | 0.12.0 | Token counting |
| Pydantic | 2.x | Data validation |
| Pydantic Settings | 2.13.1 | Configuration management |
| pytest | 9.0.2 | Testing framework |
| GitPython | 3.1.43 | Git repository operations |
| Google Generative AI | 1.66.0 | Google AI models |
| OpenAI | 2.24.0 | OpenAI API client |
| Groq | 1.0.0 | Groq API client |

## 📁 Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── models.py               # SQLAlchemy ORM models
├── requirements.txt        # Python dependencies (production)
├── requirements.dev.txt    # Development dependencies
├── requirements.prod.txt   # Production-specific dependencies
├── pytest.ini              # pytest configuration
├── Dockerfile.dev          # Development Docker container
├── Dockerfile.prod         # Production Docker container
├── .env.template           # Environment variables template
├── AI_CONFIGURATION.md     # AI provider configuration documentation
│
├── core/                   # Infrastructure & configuration
│   ├── __init__.py
│   ├── database.py         # Database connection & session management
│   ├── settings.py         # Pydantic settings (env vars, AI providers)
│   ├── logging_config.py   # Colored logging setup
│   ├── exception_handlers.py  # Global exception handlers
│   └── messages.py         # Centralized message strings
│
├── routers/                # API route definitions
│   ├── __init__.py
│   ├── rubrics.py          # Rubric endpoints
│   ├── evaluations.py      # Evaluation endpoints (with AI evaluation)
│   └── file_upload.py      # File upload endpoints for briefings
│
├── schemas/                # Pydantic validation schemas
│   ├── __init__.py
│   ├── response.py         # APIResponse wrapper schema
│   ├── rubric.py           # Rubric-related schemas
│   └── evaluation.py       # Evaluation-related schemas (with AI config)
│
├── services/               # Business logic layer
│   ├── __init__.py
│   ├── ai_client.py        # Multi-provider AI client (OpenAI, Gemini, Groq)
│   ├── ai_evaluation_engine.py  # Core AI evaluation orchestrator
│   ├── context_engine.py   # FAISS-based RAG vector search
│   ├── git_loader.py       # Repository cloning & code analysis
│   ├── prompts.py          # Centralized prompt templates
│   ├── rubric_service_api.py    # Rubric CRUD operations
│   ├── evaluation_service_api.py # Evaluation CRUD operations
│   ├── file_upload_service.py   # File upload handling
│   └── pdf_processor.py    # PDF processing for RAG context
│
└── tests/                  # Test suite
    ├── __init__.py
    ├── conftest.py         # pytest fixtures
    └── services/           # Service-level tests
        ├── __init__.py
        ├── test_ai_evaluation_engine.py  # AI evaluation engine tests
        ├── test_context_engine.py        # RAG context engine tests
        ├── test_evaluation_service_api.py # Evaluation service tests
        ├── test_pdf_processor.py         # PDF processing tests
        └── test_rubric_service_api.py    # Rubric service tests
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
| POST | `/api/v1/evaluations/briefings` | Upload briefing PDF file for RAG context |

### File Upload Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/evaluations/briefings` | Upload PDF briefing file (max 5MB) |

### AI Configuration

The evaluation endpoint supports custom AI provider configuration:

```json
{
  "repo_url": "https://github.com/user/repo",
  "rubric_id": 1,
  "briefing_path": "/path/to/briefing.pdf",
  "ai_provider": "openai",     // Optional: openai, gemini, groq
  "ai_model": "gpt-4",         // Optional: model for selected provider
  "ai_api_key": "sk-..."       // Optional: API key (or use X-API-Key header)
}
```

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

### Evaluation Response Format

Evaluations return detailed findings with WHIS methodology:

```json
{
  "success": true,
  "data": {
    "id": 1,
    "repo_url": "https://github.com/user/repo",
    "total_score": 85.5,
    "status": "completed",
    "findings": [
      {
        "criterion_id": 1,
        "selected_level_id": 2,
        "file_path": "src/main.py",
        "evidence_snippet": "def main(): pass",
        "improvement_suggestion": "Add error handling",
        "score_points": 3.0
      }
    ],
    "ai_summary": "Comprehensive evaluation summary..."
  },
  "errors": null,
  "message": "Evaluation completed successfully"
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

#### Database Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `POSTGRES_USER` | ✅ | - | PostgreSQL username |
| `POSTGRES_PASSWORD` | ✅ | - | PostgreSQL password |
| `POSTGRES_DB` | ✅ | - | Database name |
| `DB_HOST` | ✅ | `db` | Database host |
| `DB_PORT` | ✅ | `5432` | Database port |

#### AI Provider Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | ✅ | - | OpenAI API key for AI features |
| `OPENAI_MODEL` | ✅ | - | OpenAI model (e.g., "gpt-4", "gpt-3.5-turbo") |
| `GEMINI_API_KEY` | ✅ | - | Gemini API key (optional) |
| `GEMINI_MODEL` | ✅ | - | Gemini model (e.g., "gemini-1.5-pro") |
| `GROQ_API_KEY` | ✅ | - | Groq API key (optional) |
| `GROQ_MODEL` | ✅ | - | Groq model (e.g., "llama3-8b-8192") |
| `GEMINI_EMBEDDING_MODEL` | ✅ | "models/gemini-embedding-001" | Gemini embedding model |
| `OPENAI_EMBEDDING_MODEL` | ✅ | "text-embedding-3-small" | OpenAI embedding model |

#### Application Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `API_V1_PREFIX` | ✅ | `/api/v1` | API version prefix |
| `APP_TITLE` | ✅ | `Evaluador RAG API` | Application title |
| `APP_VERSION` | ✅ | `1.0.0` | Application version |
| `FILE_UPLOAD_PATH` | ✅ | "/tmp/briefings" | Server path for uploaded briefing files |

#### RAG Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `RAG_MAX_CHUNKS` | ✅ | 8 | Maximum number of chunks for RAG context |
| `RAG_MAX_CHUNK_CHARS` | ✅ | 1200 | Maximum characters per RAG chunk |
| `MAX_FILE_SIZE` | ✅ | 50000 | Maximum file size for processing (50KB) |

#### Evaluation Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `EVALUATION_STATUS_PENDING` | ✅ | "pending" | Pending evaluation status |
| `EVALUATION_STATUS_PROCESSING` | ✅ | "processing" | Processing evaluation status |
| `EVALUATION_STATUS_COMPLETED` | ✅ | "completed" | Completed evaluation status |
| `EVALUATION_STATUS_FAILED` | ✅ | "failed" | Failed evaluation status |

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
└── services/                      # Service-level tests
    ├── test_ai_evaluation_engine.py  # AI evaluation engine tests
    ├── test_context_engine.py        # RAG context engine tests
    ├── test_evaluation_service_api.py # Evaluation service tests
    ├── test_pdf_processor.py         # PDF processing tests
    └── test_rubric_service_api.py    # Rubric service tests
```

### Test Categories

#### AI Evaluation Tests
- **test_ai_evaluation_engine.py**: Tests for the core AI evaluation orchestrator
  - Repository cloning and code analysis
  - Multi-criterion evaluation with WHIS methodology
  - Score calculation and aggregation
  - AI summary generation
  - Error handling for failed evaluations

#### RAG Context Tests
- **test_context_engine.py**: Tests for FAISS-based vector search
  - Document indexing and retrieval
  - Semantic similarity search
  - Context chunking and metadata handling

#### PDF Processing Tests
- **test_pdf_processor.py**: Tests for PDF document processing
  - Text extraction from PDF files
  - Document chunking for RAG context
  - Text cleaning and formatting

#### Service Integration Tests
- **test_evaluation_service_api.py**: Tests for evaluation service operations
- **test_rubric_service_api.py**: Tests for rubric CRUD operations

### Test Database

Tests use an in-memory SQLite database for isolation and speed. Each test gets a fresh database schema.

### AI Provider Testing

The test suite includes comprehensive testing for:
- Multi-provider AI client (OpenAI, Gemini, Groq)
- AI configuration validation
- Error handling for API failures
- Response parsing and validation

### Mocking Strategy

Tests use extensive mocking to:
- Avoid actual API calls during testing
- Simulate different AI provider responses
- Test error scenarios and edge cases
- Ensure consistent test execution

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

### AI Component Development

#### Adding a New AI Provider

1. **Update AIProvider enum** in `services/ai_client.py`
2. **Add provider initialization** in `AIClient._get_client()`
3. **Update settings** in `core/settings.py` for provider-specific configuration
4. **Add tests** in `tests/services/test_ai_client.py`

#### Adding a New RAG Document Type

1. **Update file type detection** in `services/git_loader.py`
2. **Add parsing logic** for the new document type
3. **Update ContextEngine** to handle the new metadata
4. **Add tests** for document processing

#### Adding a New Evaluation Criterion

1. **Update rubric schema** in `schemas/rubric.py`
2. **Add criterion processing** in `services/ai_evaluation_engine.py`
3. **Update prompt templates** in `services/prompts.py`
4. **Add tests** for criterion evaluation

### RAG Best Practices

- **Document Chunking**: Keep chunks under 1200 characters for optimal context
- **Metadata**: Include file paths and document types for better traceability
- **Semantic Search**: Use ContextEngine for relevant context retrieval
- **Error Handling**: Always handle AI API failures gracefully

### AI Evaluation Best Practices

- **WHIS Methodology**: Always provide Where, How, Improvement, and Score
- **Evidence-Based**: Cite specific code snippets and file paths
- **Constructive Feedback**: Focus on actionable improvements
- **Scoring Consistency**: Use consistent criteria across evaluations

## 📖 Related Documentation

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [LangChain Documentation](https://python.langchain.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

## 📄 License

This project is part of the Bootcamp-IA-P5 organization.