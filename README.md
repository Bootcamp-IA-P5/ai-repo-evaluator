# AI Repo Evaluator

A full-stack application for evaluating repositories using AI-powered analysis. Built with a modern containerized architecture for seamless development and deployment.

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                      Docker Network (eval-network)               │
│                                                                  │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐       │
│  │  Frontend   │────> │   Backend   │────> │  Database   │       │
│  │   (React)   │      │  (FastAPI)  │      │ (PostgreSQL)│       │
│  │   :5173     │      │   :8000     │      │   :5432     │       │
│  └─────────────┘      └─────────────┘      └─────────────┘       │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

## 👥 Team Members

- **Ciprian Nica** - Development
- **Óscar Rodríguez** - Scrum Master and Development  
- **Yeder Pimentel** - Product Owner and Development

## 📋 Project Organization

| Role | Team Member | Responsibilities |
|------|-------------|------------------|
| **Scrum Master** | Óscar Rodríguez | Development coordination, sprint management |
| **Product Owner** | Yeder Pimentel | Requirements gathering, backlog management, development |
| **Development** | Ciprian Nica | Feature implementation and code development |
| **Stakeholder** | David Robert | Project oversight and guidance |

## 📚 Documentation

This project includes detailed documentation for each component:

- **[Backend Documentation](/backend/README.md)** - Comprehensive API documentation, database schema, AI evaluation workflow, and backend development guide
- **[Frontend Documentation](/frontend/README.md)** - UI component library, page flows, responsive design guidelines, and frontend development guide

## 🔗 Related Links

- **[GitHub Project Board](https://github.com/orgs/Bootcamp-IA-P5/projects/40)** - Project management and task tracking

## 🛠️ Tech Stack

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11 | Runtime environment |
| FastAPI | 0.109.0 | Web framework |
| Uvicorn | 0.27.0 | ASGI server with hot-reload |
| SQLAlchemy | 2.0.25 | ORM |
| Alembic | 1.13.1 | Database migrations |
| psycopg2-binary | 2.9.9 | PostgreSQL adapter |
| LangChain | 1.2.10 | AI/LLM framework |
| LangChain Community | 0.4.1 | LangChain ecosystem extensions |
| LangChain Core | 1.2.16 | Core LangChain functionality |
| LangChain OpenAI | 1.1.10 | OpenAI integrations |
| LangChain Google GenAI | 4.2.1 | Google Gemini integrations |
| FAISS | 1.13.2 | Vector similarity search |
| PyPDF | 6.0.0 | PDF processing |
| TikToken | 0.12.0 | Token counting |
| OpenAI | 2.24.0 | OpenAI API client |
| Google Generative AI | 1.66.0 | Google AI models |
| Groq | 1.0.0 | Groq API client |
| GitPython | 3.1.43 | Git repository operations |
| Pydantic Settings | 2.13.1 | Configuration management |

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| React | 19.2.3 | UI library |
| Next.js | 16.1.6 | React framework & build tool |
| TailwindCSS | 4.x | Styling framework |
| Axios | 1.13.5 | HTTP client |
| Lucide React | 0.575.0 | Icon library |
| React Markdown | 10.1.0 | Markdown rendering |
| Recharts | 3.7.0 | Data visualization |
| Remark GFM | 4.0.1 | GitHub-flavored markdown |

### Infrastructure
| Technology | Version | Purpose |
|------------|---------|---------|
| PostgreSQL | 15 Alpine | Relational database |
| Docker | - | Containerization |
| Docker Compose | - | Multi-container orchestration |
| LangGraph | - | AI workflow monitoring and orchestration |

## 📋 Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (v20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (v2.0+) or Docker Compose V1 (`docker-compose`)

> **Note:** This project uses Docker-in-Docker development. The management scripts are designed for Linux/macOS systems.

### Platform-Specific Scripts

| Platform | Script | Description |
|----------|--------|-------------|
| Linux/macOS | `manage.sh` | Bash script with Docker-in-Docker support |
| Windows | Manual Docker commands | Use `docker compose` commands directly (see [Windows Setup](#windows-support)) |

### Windows Support

For Windows users, the project supports Docker Desktop with WSL2 backend. Use these commands instead of the management script:

```bash
# Start all services
docker compose -f docker-compose.dev.yml up -d

# View logs
docker compose -f docker-compose.dev.yml logs -f

# Stop services
docker compose -f docker-compose.dev.yml down
```

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone git@github.com:Bootcamp-IA-P5/ai-repo-evaluator.git
cd ai-repo-evaluator
```

### 2. Configure Environment Variables

```bash
# Backend configuration
cp backend/.env.template backend/.env
# Edit backend/.env with your settings

# Frontend configuration
cp frontend/.env.template frontend/.env
# Edit frontend/.env with your settings
```

### 3. Start All Services

**Linux/macOS:**
```bash
./manage.sh all
```

### 4. Access the Application

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Documentation | http://localhost:8000/docs |

## 📁 Project Structure

```
ai-repo-evaluator/
├── backend/
│   ├── Dockerfile.dev        # Development container for FastAPI
│   ├── requirements.txt      # Python dependencies
│   ├── .env.template         # Environment variables template
│   └── ...                   # Application code
├── frontend/
│   ├── Dockerfile.dev        # Development container for React
│   ├── package.json          # Node.js dependencies
│   ├── .env.template         # Environment variables template
│   └── ...                   # Application code
├── backups/                  # Database backup storage
├── docker-compose.dev.yml    # Docker Compose configuration
├── manage.sh                 # Development management script (Linux/macOS)
├── requirements.txt          # Root requirements (references backend)
└── README.md                 # This file
```

## 🔧 Development Guide

### Using `manage.sh`

The `manage.sh` script provides convenient commands for managing the development environment:

| Command | Description |
|---------|-------------|
| `./manage.sh db` | Start only the database service |
| `./manage.sh backend` | Start database and backend services |
| `./manage.sh all` | Start all services (db, backend, frontend) |
| `./manage.sh rebuild` | Rebuild all Docker images from scratch (no-cache) |
| `./manage.sh stop` | Stop all running services |
| `./manage.sh backup` | Create a database backup |
| `./manage.sh restore` | Restore database from a backup |
| `./manage.sh logs` | Follow logs from all containers |

### Development Workflow

1. **Start development environment:**
   ```bash
   ./manage.sh all
   ```

2. **View logs (optional):**
   ```bash
   ./manage.sh logs
   ```

3. **Make changes** - Both backend and frontend have hot-reloading enabled:
   - Backend: Uvicorn reloads on Python file changes
   - Frontend: Vite reloads on React/CSS changes

4. **Stop when done:**
   ```bash
   ./manage.sh stop
   ```

### Running Individual Services

For targeted development, you can start specific services:

```bash
# Database only (useful for local backend development)
./manage.sh db

# Database + Backend (useful for API development)
./manage.sh backend

# Everything (full stack)
./manage.sh all
```

## 💾 Database Management

### Creating a Backup

```bash
./manage.sh backup
```

You'll be prompted to enter a filename. The backup will be stored as an SQL file in the `./backups/` directory.

### Restoring from Backup

```bash
./manage.sh restore
```

This will:
1. List available backups in `./backups/`
2. Prompt you to select a backup file
3. Restore the database from that backup

### Manual Database Access

```bash
# Connect to PostgreSQL container
docker exec -it evaluator_db psql -U <username> -d <database>

# Or use your local psql client
psql -h localhost -p 5432 -U <username> -d <database>
```

## 🔄 Rebuilding Containers

If you need to rebuild containers (e.g., after dependency changes):

```bash
# Rebuild all images from scratch
./manage.sh rebuild
```

This is equivalent to:
```bash
docker compose -f docker-compose.dev.yml build --no-cache
docker compose -f docker-compose.dev.yml up -d
```

## 🐛 Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Check what's using the port
lsof -i :8000  # Backend
lsof -i :5173  # Frontend
lsof -i :5432  # Database

# Stop conflicting services or modify ports in docker-compose.dev.yml
```

**Docker volume issues:**
```bash
# Remove all volumes and start fresh
docker compose -f docker-compose.dev.yml down -v
./manage.sh all
```

**Container won't start:**
```bash
# Check logs
./manage.sh logs

# Rebuild from scratch
./manage.sh rebuild
```

### Viewing Logs

```bash
# All services
./manage.sh logs

# Specific service
docker logs evaluator_backend -f
docker logs evaluator_frontend -f
docker logs evaluator_db -f
```

## 📝 Environment Variables

### Backend (`backend/.env`)

Configure these variables based on your `.env.template`:

| Variable | Description |
|----------|-------------|
| `POSTGRES_USER` | Database username |
| `POSTGRES_PASSWORD` | Database password |
| `POSTGRES_DB` | Database name |
| `OPENAI_API_KEY` | OpenAI API key for AI features |

### Frontend (`frontend/.env`)

Configure these variables based on your `.env.template`:

| Variable | Description |
|----------|-------------|
| `VITE_API_URL` | Backend API URL (default: http://localhost:8000) |

## 📖 API Documentation

Once the backend is running, access the auto-generated API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🤝 Contributing

1. Create a feature branch from `main`
2. Make your changes
3. Ensure tests pass
4. Submit a pull request

## 📄 License

This project is part of the Bootcamp-IA-P5 organization.