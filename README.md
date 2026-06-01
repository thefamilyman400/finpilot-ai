# FinPilot AI - Personal Finance Management Platform

A comprehensive AI-powered personal finance management platform built with FastAPI (backend) and React (frontend).

## 🌟 Features

### Core Features
- **Account Management**: Track multiple financial accounts (savings, current, credit cards, loans)
- **Transaction Tracking**: Automatic categorization and analysis of transactions
- **AI Copilot**: Intelligent financial assistant powered by Google Gemini AI
- **Financial Recommendations**: Personalized insights and suggestions
- **Document Management**: Upload and parse financial documents
- **Financial Simulations**: Model different financial scenarios
- **Loan Management**: Track EMIs, interest rates, and loan details

### AI Capabilities
- Natural language financial queries
- Contextual financial advice
- Spending pattern analysis
- Budget recommendations
- Automated retry logic with exponential backoff
- Graceful error handling for API rate limits

## 🏗️ Architecture

### Backend (FastAPI)
- **Framework**: FastAPI with async/await support
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT-based authentication
- **AI Integration**: Google Gemini API
- **API Documentation**: Auto-generated OpenAPI/Swagger docs

### Frontend (React + TypeScript)
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **HTTP Client**: Axios

## 📋 Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Google Gemini API Key

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd finpilot-ai
```

### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your configuration

# Initialize database
python init_database.py

# Run the server
uvicorn main:app --reload
```

Backend will be available at: http://localhost:8000
API Documentation: http://localhost:8000/docs

### 3. Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.development .env
# Edit .env if needed

# Run development server
npm run dev
```

Frontend will be available at: http://localhost:5173

## 🔧 Configuration

### Backend Environment Variables (.env)

```env
# Database
DATABASE_URL=postgresql://postgres:admin@localhost:5432/finpilot

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15

# Google Gemini AI
GOOGLE_API_KEY=your-gemini-api-key
GOOGLE_GEMINI_MODEL=gemini-2.0-flash

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Frontend Environment Variables (.env)

```env
VITE_API_BASE_URL=http://localhost:8000
```

## 📚 Documentation

- [Technical Architecture](docs/technical-architecture.md)
- [Windows Setup Guide](docs/windows-setup-guide.md)
- [Testing Guide](docs/TESTING-GUIDE.md)
- [Calculator Formulas](docs/calculator-formulas-and-logic.md)

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Run Specific Test Categories
```bash
# Fast tests only
pytest -c pytest-fast.ini

# With coverage
pytest -c pytest-coverage.ini
```

## 🛠️ Utility Scripts

### Database Management
```bash
# Initialize database tables
python init_database.py

# Clean up all accounts and transactions
python delete_all_accounts.py
```

## 📦 Project Structure

```
finpilot-ai/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Core functionality
│   │   ├── db/           # Database configuration
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   └── services/     # Business logic
│   ├── tests/            # Test suite
│   ├── migrations/       # Database migrations
│   ├── main.py          # Application entry point
│   └── config.py        # Configuration
├── frontend/
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── pages/       # Page components
│   │   ├── services/    # API services
│   │   ├── store/       # State management
│   │   └── types/       # TypeScript types
│   └── public/          # Static assets
└── docs/                # Documentation
```

## 🔐 Security Features

- JWT-based authentication
- Password hashing with bcrypt
- CORS protection
- SQL injection prevention
- Input validation with Pydantic
- Secure session management

## 🤖 AI Features

### Retry Logic
- Automatic retry with exponential backoff (3 attempts)
- Handles rate limits (429) and service unavailable (503) errors
- Intelligent delay extraction from API responses

### Error Handling
- User-friendly error messages
- Proper HTTP status codes
- Database transaction rollback on errors
- Null safety for financial data

## 📊 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token

### Accounts
- `GET /api/v1/accounts` - List accounts
- `POST /api/v1/accounts` - Create account
- `GET /api/v1/accounts/{id}` - Get account details
- `PUT /api/v1/accounts/{id}` - Update account
- `DELETE /api/v1/accounts/{id}` - Delete account

### Transactions
- `GET /api/v1/transactions` - List transactions
- `POST /api/v1/transactions` - Create transaction
- `GET /api/v1/transactions/{id}` - Get transaction
- `PUT /api/v1/transactions/{id}` - Update transaction
- `DELETE /api/v1/transactions/{id}` - Delete transaction

### AI Copilot
- `POST /api/v1/copilot/chat` - Chat with AI
- `POST /api/v1/copilot/quick-analysis` - Quick financial analysis
- `GET /api/v1/copilot/conversations` - List conversations
- `GET /api/v1/copilot/conversations/{id}` - Get conversation

### Recommendations
- `POST /api/v1/recommendations/generate` - Generate recommendations
- `GET /api/v1/recommendations` - List recommendations

## 🐛 Troubleshooting

### Gemini API Quota Exceeded
If you see "quota exceeded" errors:
1. Wait for quota reset (daily for free tier)
2. Switch to a different model in `.env`: `GOOGLE_GEMINI_MODEL=gemini-1.5-flash`
3. Get a new API key at https://aistudio.google.com/apikey
4. Upgrade to paid plan at https://ai.google.dev/pricing

### Database Connection Issues
- Ensure PostgreSQL is running
- Check DATABASE_URL in .env
- Verify database exists: `createdb finpilot`

### Port Already in Use
- Backend: Change PORT in .env
- Frontend: Use `npm run dev -- --port 3000`

## 📝 License

This project is proprietary software.

## 👥 Contributors

Built with ❤️ by the FinPilot AI team

## 🔗 Links

- [API Documentation](http://localhost:8000/docs)
- [Google Gemini API](https://ai.google.dev/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)