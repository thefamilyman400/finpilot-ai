# FinPilot AI Backend

AI-powered financial platform backend built with FastAPI, PostgreSQL, and OpenAI GPT-4.

## Features

### Core Features
- 🔐 **JWT Authentication** - Secure token-based authentication
- 👤 **User Management** - Registration, login, profile management
- 💰 **Financial Management** - Multi-account support (checking, savings, credit, investment, loan)
- 📊 **Transaction Tracking** - 30+ categories with advanced filtering
- 📈 **Analytics** - Comprehensive financial analytics and insights

### AI-Powered Features
- 🤖 **AI Copilot** - Natural language financial conversations with GPT-4
- 💡 **Smart Recommendations** - Personalized financial advice
- 📄 **Document Intelligence** - Upload and analyze financial documents (PDF, images, DOCX)
- 🎮 **Financial Calculators** - Retirement planning, investment growth, loan amortization, budget forecasting
- ⚙️ **Autonomous Workflows** - Automated financial actions and alerts

### Technical Features
- 🗄️ **PostgreSQL Database** - SQLAlchemy ORM with 11 models
- ⚡ **FastAPI** - Modern, fast Python web framework
- 📝 **Auto Documentation** - Interactive API docs with Swagger UI
- 🔒 **Security** - Password hashing, CORS, input validation
- 🎯 **Type Safety** - Full type hints with Pydantic validation
- 🧮 **Monte Carlo Simulations** - Risk analysis with NumPy

## Tech Stack

- **Framework**: FastAPI 0.104.1
- **Database**: PostgreSQL 15+ with SQLAlchemy 2.0.23
- **AI/ML**: OpenAI GPT-4
- **Authentication**: JWT tokens with python-jose
- **Password Hashing**: Bcrypt via passlib
- **Validation**: Pydantic 2.5.0
- **Calculations**: NumPy (Monte Carlo simulations)

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
- OpenAI API key (for AI features)

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

## API Endpoints (51 Total)

### Authentication (5 endpoints)
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get tokens
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/logout` - Logout user

### Accounts (6 endpoints)
- `POST /api/v1/accounts` - Create account
- `GET /api/v1/accounts` - List accounts
- `GET /api/v1/accounts/{id}` - Get account details
- `PUT /api/v1/accounts/{id}` - Update account
- `DELETE /api/v1/accounts/{id}` - Delete account
- `GET /api/v1/accounts/summary` - Get financial summary

### Transactions (7 endpoints)
- `POST /api/v1/transactions` - Create transaction
- `GET /api/v1/transactions` - List transactions (with filters)
- `GET /api/v1/transactions/{id}` - Get transaction details
- `PUT /api/v1/transactions/{id}` - Update transaction
- `DELETE /api/v1/transactions/{id}` - Delete transaction
- `GET /api/v1/transactions/stats` - Get transaction statistics
- `GET /api/v1/transactions/categories` - Get available categories

### Documents (5 endpoints)
- `POST /api/v1/documents/upload` - Upload document
- `GET /api/v1/documents` - List documents
- `GET /api/v1/documents/{id}` - Get document details
- `DELETE /api/v1/documents/{id}` - Delete document
- `POST /api/v1/documents/{id}/analyze` - AI analysis

### AI Copilot (8 endpoints)
- `POST /api/v1/copilot/chat` - Chat with AI
- `GET /api/v1/copilot/conversations` - List conversations
- `POST /api/v1/copilot/conversations` - Create conversation
- `GET /api/v1/copilot/conversations/{id}` - Get conversation with messages
- `PUT /api/v1/copilot/conversations/{id}` - Update conversation
- `DELETE /api/v1/copilot/conversations/{id}` - Delete conversation
- `GET /api/v1/copilot/conversations/{id}/messages` - Get messages
- `POST /api/v1/copilot/analyze` - Quick financial analysis

### Financial Simulations (6 endpoints)
- `POST /api/v1/simulations` - Create simulation
- `GET /api/v1/simulations` - List simulations
- `GET /api/v1/simulations/{id}` - Get simulation details
- `POST /api/v1/simulations/retirement/quick` - Retirement planning calculator
- `POST /api/v1/simulations/investment/quick` - Investment growth calculator
- `POST /api/v1/simulations/loan-payoff/quick` - Loan amortization calculator

### Recommendations (7 endpoints)
- `POST /api/v1/recommendations/generate` - Generate AI recommendations
- `GET /api/v1/recommendations` - List recommendations
- `GET /api/v1/recommendations/{id}` - Get recommendation details
- `PUT /api/v1/recommendations/{id}` - Update recommendation
- `POST /api/v1/recommendations/{id}/accept` - Accept recommendation
- `POST /api/v1/recommendations/{id}/reject` - Reject recommendation
- `DELETE /api/v1/recommendations/{id}` - Delete recommendation

### Workflows (7 endpoints)
- `POST /api/v1/workflows` - Create workflow
- `GET /api/v1/workflows` - List workflows
- `GET /api/v1/workflows/{id}` - Get workflow details
- `PUT /api/v1/workflows/{id}` - Update workflow
- `DELETE /api/v1/workflows/{id}` - Delete workflow
- `POST /api/v1/workflows/{id}/execute` - Execute workflow
- `GET /api/v1/workflows/{id}/executions` - Get execution history

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

**Current Status**: Production-Ready ✅

✅ **Completed Features**:
- Authentication & User Management
- Multi-account Financial Management (5 account types)
- Transaction Tracking (30+ categories)
- AI Copilot with GPT-4 Integration
- Document Intelligence (PDF, images, DOCX)
- Financial Calculators (Retirement, Investment, Loan, Budget)
- Monte Carlo Simulations
- Recommendations Engine
- Autonomous Workflows
- Comprehensive Test Suite (30/30 tests passing)

## Test Coverage

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html

# Current Status: 100% (30/30 tests passing)
```

## Documentation

- **Project Status**: `../docs/project-current-status.md`
- **Technical Architecture**: `../docs/technical-architecture.md`
- **Setup Guide**: `../docs/windows-setup-guide.md`
- **Testing Guide**: `../docs/TESTING-GUIDE.md`
- **Calculator Formulas**: `../docs/calculator-formulas-and-logic.md`

## License

[Your License Here]

## Support

For issues and questions, please open an issue on GitHub.

---

**Made with ❤️ by Bob**