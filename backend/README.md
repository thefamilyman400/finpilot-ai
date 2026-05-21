# FinPilot AI Backend

AI-powered financial platform backend built with FastAPI, PostgreSQL, and OpenAI GPT-4.

## Features

### Core Features
- 🔐 **JWT Authentication** - Secure token-based authentication
- 👤 **User Management** - Registration, login, profile management
- 💰 **Financial Management** - Multi-account support, transaction tracking
- 📊 **Analytics** - Comprehensive financial analytics and insights

### AI-Powered Features
- 🤖 **AI Copilot** - Natural language financial conversations with GPT-4
- 💡 **Smart Recommendations** - Personalized financial advice
- 📄 **Document Intelligence** - Upload and analyze financial documents
- 🎮 **Financial Simulations** - Retirement, investment, loan scenarios
- ⚙️ **Autonomous Workflows** - Automated financial actions and alerts

### Technical Features
- 🗄️ **PostgreSQL Database** - Async SQLAlchemy ORM
- ⚡ **FastAPI** - Modern, fast Python web framework
- 📝 **Auto Documentation** - Interactive API docs with Swagger UI
- 🔒 **Security** - Password hashing, CORS, input validation
- 🎯 **Type Safety** - Full type hints with Pydantic validation

## Tech Stack

- **Framework**: FastAPI 0.109+
- **Database**: PostgreSQL 15+ with SQLAlchemy 2.0
- **AI/ML**: OpenAI GPT-4, LangChain
- **Authentication**: JWT tokens with python-jose
- **Password Hashing**: Bcrypt via passlib
- **Validation**: Pydantic v2
- **Async Support**: asyncpg, async SQLAlchemy

## Project Structure

```
backend/
├── main.py                      # Application entry point
├── config.py                    # Configuration management
├── init_database.py             # Database initialization script
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── app/
│   ├── api/v1/                  # API routes (68 endpoints)
│   │   ├── auth.py              # Authentication (7 endpoints)
│   │   ├── users.py             # User management (5 endpoints)
│   │   ├── accounts.py          # Financial accounts (7 endpoints)
│   │   ├── transactions.py      # Transactions (7 endpoints)
│   │   ├── copilot.py           # AI Copilot (7 endpoints)
│   │   ├── recommendations.py   # AI Recommendations (9 endpoints)
│   │   ├── documents.py         # Document intelligence (9 endpoints)
│   │   ├── simulations.py       # Financial simulations (9 endpoints)
│   │   └── workflows.py         # Autonomous workflows (13 endpoints)
│   ├── core/                    # Core functionality
│   │   ├── security.py          # Security utilities
│   │   └── dependencies.py      # FastAPI dependencies
│   ├── db/                      # Database
│   │   ├── base.py              # SQLAlchemy base
│   │   └── session.py           # Database session
│   ├── models/                  # SQLAlchemy models (10 tables)
│   │   ├── user.py              # User model
│   │   ├── account.py           # Financial account model
│   │   ├── transaction.py       # Transaction model
│   │   ├── conversation.py      # AI conversation models
│   │   ├── recommendation.py    # Recommendation model
│   │   ├── document.py          # Document model
│   │   ├── simulation.py        # Simulation model
│   │   └── workflow.py          # Workflow models
│   ├── schemas/                 # Pydantic schemas (40+ schemas)
│   └── services/                # Business logic (7 services)
│       ├── account_service.py
│       ├── transaction_service.py
│       ├── ai_service.py
│       ├── recommendation_service.py
│       ├── document_service.py
│       ├── simulation_service.py
│       └── workflow_service.py
```

## Setup Instructions

### Prerequisites

- Python 3.11 or higher
- PostgreSQL 15 or higher
- Redis (for caching and background tasks)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd finpilot-ai/backend
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
# Important: Change SECRET_KEY in production!
```

**Required Environment Variables:**

- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: Secret key for JWT encoding (use `openssl rand -hex 32`)
- `OPENAI_API_KEY`: OpenAI API key for AI features

### 5. Set Up Database

```bash
# Create PostgreSQL database
createdb finpilot

# Update DATABASE_URL in .env
# Example: postgresql://user:password@localhost:5432/finpilot

# Initialize database tables
python init_database.py
```

This will create all 10 tables:
- users
- financial_accounts
- transactions
- conversations & messages
- recommendations
- documents
- financial_simulations
- autonomous_workflows & workflow_executions

### 6. Run the Application

```bash
# Development mode (with auto-reload)
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints (68 Total)

### Authentication (7 endpoints)
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get tokens
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - Logout user
- `POST /api/v1/auth/password-reset-request` - Request password reset
- `POST /api/v1/auth/password-reset` - Reset password
- `POST /api/v1/auth/verify-email` - Verify email

### User Management (5 endpoints)
- `GET /api/v1/users/me` - Get current user profile
- `PUT /api/v1/users/me` - Update profile
- `DELETE /api/v1/users/me` - Delete account
- `POST /api/v1/users/me/change-password` - Change password
- `POST /api/v1/users/me/resend-verification` - Resend verification

### Financial Accounts (7 endpoints)
- `POST /api/v1/accounts` - Create account
- `GET /api/v1/accounts` - List accounts
- `GET /api/v1/accounts/summary` - Financial summary
- `GET /api/v1/accounts/{id}` - Get account
- `PUT /api/v1/accounts/{id}` - Update account
- `DELETE /api/v1/accounts/{id}` - Delete account
- `POST /api/v1/accounts/{id}/sync` - Sync account

### Transactions (7 endpoints)
- `POST /api/v1/transactions` - Create transaction
- `GET /api/v1/transactions` - List transactions
- `GET /api/v1/transactions/analytics` - Get analytics
- `GET /api/v1/transactions/{id}` - Get transaction
- `PUT /api/v1/transactions/{id}` - Update transaction
- `DELETE /api/v1/transactions/{id}` - Delete transaction
- `POST /api/v1/transactions/categorize` - Bulk categorize

### AI Copilot (7 endpoints)
- `POST /api/v1/copilot/chat` - Chat with AI
- `POST /api/v1/copilot/quick-analysis` - Quick analysis
- `GET /api/v1/copilot/conversations` - List conversations
- `POST /api/v1/copilot/conversations` - Create conversation
- `GET /api/v1/copilot/conversations/{id}` - Get conversation
- `PUT /api/v1/copilot/conversations/{id}` - Update conversation
- `DELETE /api/v1/copilot/conversations/{id}` - Delete conversation

### Recommendations (9 endpoints)
- `POST /api/v1/recommendations/generate` - Generate recommendations
- `GET /api/v1/recommendations` - List recommendations
- `GET /api/v1/recommendations/summary` - Get summary
- `GET /api/v1/recommendations/{id}` - Get recommendation
- `PUT /api/v1/recommendations/{id}` - Update recommendation
- `POST /api/v1/recommendations/{id}/accept` - Accept
- `POST /api/v1/recommendations/{id}/reject` - Reject
- `POST /api/v1/recommendations/{id}/complete` - Complete
- `DELETE /api/v1/recommendations/{id}` - Delete

### Documents (9 endpoints)
- `POST /api/v1/documents/upload` - Upload document
- `GET /api/v1/documents/{id}` - Get document
- `GET /api/v1/documents/` - List documents
- `PUT /api/v1/documents/{id}` - Update metadata
- `DELETE /api/v1/documents/{id}` - Delete document
- `POST /api/v1/documents/{id}/extract-text` - Extract text
- `POST /api/v1/documents/{id}/analyze` - AI analysis
- `POST /api/v1/documents/search` - Search documents
- `POST /api/v1/documents/{id}/tags` - Manage tags

### Simulations (9 endpoints)
- `POST /api/v1/simulations/` - Create simulation
- `GET /api/v1/simulations/{id}` - Get simulation
- `GET /api/v1/simulations/` - List simulations
- `PUT /api/v1/simulations/{id}` - Update simulation
- `DELETE /api/v1/simulations/{id}` - Delete simulation
- `POST /api/v1/simulations/{id}/run` - Execute simulation
- `POST /api/v1/simulations/retirement/quick` - Quick retirement plan
- `POST /api/v1/simulations/investment/quick` - Quick investment scenario
- `POST /api/v1/simulations/loan-payoff/quick` - Quick loan analysis

### Workflows (13 endpoints)
- `POST /api/v1/workflows/` - Create workflow
- `GET /api/v1/workflows/{id}` - Get workflow
- `GET /api/v1/workflows/` - List workflows
- `PUT /api/v1/workflows/{id}` - Update workflow
- `DELETE /api/v1/workflows/{id}` - Delete workflow
- `POST /api/v1/workflows/{id}/activate` - Activate
- `POST /api/v1/workflows/{id}/pause` - Pause
- `POST /api/v1/workflows/{id}/deactivate` - Deactivate
- `POST /api/v1/workflows/{id}/execute` - Execute
- `GET /api/v1/workflows/{id}/executions` - Execution history
- `GET /api/v1/workflows/summary/stats` - Statistics
- `POST /api/v1/workflows/quick/bill-payment` - Quick bill payment
- `POST /api/v1/workflows/quick/savings-transfer` - Quick savings

For complete API documentation, visit http://localhost:8000/docs after starting the server.

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov httpx

# Run tests
pytest

# Run tests with coverage
pytest --cov=app --cov-report=html
```

### Code Quality

```bash
# Format code with Black
black .

# Lint with Flake8
flake8 .

# Type checking with MyPy
mypy .
```

### Database Migrations

```bash
# Initialize Alembic (first time only)
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Security Considerations

- ✅ JWT tokens with short expiration (15 minutes for access, 7 days for refresh)
- ✅ Password hashing with bcrypt
- ✅ CORS configuration
- ✅ Input validation with Pydantic
- ✅ SQL injection prevention via SQLAlchemy
- ✅ Rate limiting (to be implemented)
- ✅ HTTPS only in production

## Environment Variables Reference

See `.env.example` for all available configuration options.

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
pg_isready

# Test connection
psql -U user -d finpilot
```

### Import Errors

```bash
# Ensure virtual environment is activated
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## Project Status

**Current Progress**: 80% Complete (4 of 5 phases)

✅ **Completed**:
- Phase 1: Foundation (Auth & Users)
- Phase 2: Core Financial Features
- Phase 3: AI Integration
- Phase 4: Advanced Features

⏳ **Remaining**:
- Phase 5: Testing, Optimization & Deployment

## Next Steps (Phase 5)

- [ ] Comprehensive test suite (unit, integration, e2e)
- [ ] Redis caching implementation
- [ ] Celery for background tasks
- [ ] Docker containerization
- [ ] CI/CD pipeline setup
- [ ] Production deployment configuration
- [ ] Monitoring and logging (Sentry, CloudWatch)
- [ ] Performance optimization
- [ ] Security audit

## Documentation

- **Complete Implementation Summary**: `../docs/complete-implementation-summary.md`
- **Architecture Plan**: `../docs/backend-architecture-plan.md`
- **Implementation Roadmap**: `../docs/implementation-roadmap.md`
- **Setup Guides**: `../docs/phase1-setup-guide.md`, `../docs/windows-setup-guide.md`

## License

[Your License Here]

## Support

For issues and questions, please open an issue on GitHub.

---

**Made with ❤️ by Bob**