# FinPilot AI - Testing Guide

## Overview

This guide covers the testing strategy, setup, and execution for the FinPilot AI backend.

**Test Coverage Goal**: >70% (configured in pytest.ini)

---

## Testing Framework

### Tools Used
- **pytest** - Testing framework
- **pytest-asyncio** - Async test support
- **pytest-cov** - Code coverage reporting
- **httpx** - HTTP client for API testing
- **faker** - Test data generation

---

## Setup

### 1. Install Test Dependencies

```bash
cd backend
pip install -r requirements-test.txt
```

### 2. Create Test Database

```bash
# Create separate test database
createdb finpilot_test

# Update .env if needed (test database URL is auto-configured)
```

### 3. Run Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run specific test class
pytest tests/test_auth.py::TestUserRegistration

# Run specific test
pytest tests/test_auth.py::TestUserRegistration::test_register_new_user

# Run tests by marker
pytest -m auth          # Authentication tests
pytest -m financial     # Financial feature tests
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
```

---

## Test Structure

### Directory Layout

```
backend/tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── test_auth.py             # Authentication tests
├── test_accounts.py         # Account management tests
├── test_transactions.py     # Transaction tests
├── test_copilot.py          # AI copilot tests
├── test_recommendations.py  # Recommendation tests
├── test_documents.py        # Document processing tests
├── test_simulations.py      # Simulation tests
└── test_workflows.py        # Workflow tests
```

---

## Test Categories

### Test Markers

Tests are organized using pytest markers:

```python
@pytest.mark.unit          # Fast, isolated unit tests
@pytest.mark.integration   # Tests with database/external services
@pytest.mark.e2e           # End-to-end API flow tests
@pytest.mark.auth          # Authentication tests
@pytest.mark.financial     # Financial feature tests
@pytest.mark.ai            # AI/ML tests
@pytest.mark.slow          # Slow-running tests
```

### Running by Category

```bash
# Run only unit tests (fast)
pytest -m unit

# Run only integration tests
pytest -m integration

# Run all except slow tests
pytest -m "not slow"

# Run auth and financial tests
pytest -m "auth or financial"
```

---

## Available Fixtures

### Database Fixtures

```python
@pytest.fixture
async def db_session():
    """Provides clean database session for each test"""

@pytest.fixture
async def test_engine():
    """Test database engine"""
```

### User Fixtures

```python
@pytest.fixture
async def test_user():
    """Creates a test user"""

@pytest.fixture
async def test_user_token():
    """JWT token for test user"""

@pytest.fixture
async def auth_headers():
    """Authorization headers with valid token"""
```

### Financial Fixtures

```python
@pytest.fixture
async def test_account():
    """Creates a test financial account"""

@pytest.fixture
async def test_transaction():
    """Creates a test transaction"""
```

### HTTP Client Fixture

```python
@pytest.fixture
async def client():
    """Async HTTP client for API testing"""
```

### Sample Data Fixtures

```python
@pytest.fixture
def sample_user_data():
    """Sample user registration data"""

@pytest.fixture
def sample_account_data():
    """Sample account creation data"""

@pytest.fixture
def sample_transaction_data():
    """Sample transaction data"""
```

---

## Writing Tests

### Test Class Structure

```python
import pytest
from httpx import AsyncClient

@pytest.mark.financial
@pytest.mark.asyncio
class TestAccountCreation:
    """Test account creation endpoint"""
    
    async def test_create_account_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        sample_account_data: dict
    ):
        """Test successful account creation"""
        response = await client.post(
            "/api/v1/accounts",
            json=sample_account_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["account_name"] == sample_account_data["account_name"]
```

### Best Practices

1. **Use Descriptive Names**
   ```python
   # Good
   async def test_create_account_with_invalid_type_returns_422()
   
   # Bad
   async def test_account()
   ```

2. **One Assertion Per Test** (when possible)
   ```python
   # Good - focused test
   async def test_account_creation_returns_201():
       response = await client.post("/api/v1/accounts", ...)
       assert response.status_code == 201
   
   # Also good - related assertions
   async def test_account_creation_returns_correct_data():
       response = await client.post("/api/v1/accounts", ...)
       data = response.json()
       assert data["account_name"] == expected_name
       assert data["balance"] == expected_balance
   ```

3. **Use Fixtures for Setup**
   ```python
   # Good - uses fixture
   async def test_update_account(test_account, client, auth_headers):
       response = await client.put(f"/api/v1/accounts/{test_account.id}", ...)
   
   # Bad - manual setup in test
   async def test_update_account(client, auth_headers):
       # Creating account manually...
       account = Account(...)
       # ...
   ```

4. **Test Both Success and Failure Cases**
   ```python
   async def test_login_success(...)
   async def test_login_wrong_password(...)
   async def test_login_nonexistent_user(...)
   async def test_login_inactive_user(...)
   ```

---

## Coverage Reports

### Generate Coverage Report

```bash
# HTML report (opens in browser)
pytest --cov=app --cov-report=html
open htmlcov/index.html  # macOS
start htmlcov/index.html # Windows

# Terminal report
pytest --cov=app --cov-report=term-missing

# XML report (for CI/CD)
pytest --cov=app --cov-report=xml
```

### Coverage Configuration

Configured in `pytest.ini`:
```ini
[pytest]
addopts = 
    --cov=app
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=70
```

---

## Continuous Integration

### GitHub Actions Workflow

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      
      - name: Run tests
        run: pytest --cov=app --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## Test Data Management

### Using Faker for Test Data

```python
from faker import Faker

fake = Faker()

def generate_test_user():
    return {
        "email": fake.email(),
        "password": fake.password(),
        "full_name": fake.name()
    }
```

### Database Cleanup

Tests automatically clean up after themselves:
- Each test gets a fresh database session
- Session is rolled back after each test
- Test database is dropped after test suite completes

---

## Mocking External Services

### Mocking OpenAI API

```python
@pytest.fixture
def mock_openai(mocker):
    """Mock OpenAI API calls"""
    mock_response = {
        "choices": [{
            "message": {"content": "Test response"}
        }]
    }
    return mocker.patch(
        "openai.ChatCompletion.create",
        return_value=mock_response
    )

async def test_ai_chat(client, auth_headers, mock_openai):
    response = await client.post(
        "/api/v1/copilot/chat",
        json={"message": "Test"},
        headers=auth_headers
    )
    assert response.status_code == 200
```

---

## Performance Testing

### Benchmark Tests

```python
@pytest.mark.benchmark
def test_account_list_performance(benchmark, client, auth_headers):
    """Benchmark account listing endpoint"""
    result = benchmark(
        lambda: client.get("/api/v1/accounts", headers=auth_headers)
    )
    assert result.status_code == 200
```

### Load Testing

For load testing, use tools like:
- **Locust** - Python-based load testing
- **k6** - Modern load testing tool
- **Apache JMeter** - Traditional load testing

---

## Debugging Tests

### Run Tests in Verbose Mode

```bash
pytest -v
pytest -vv  # Extra verbose
```

### Show Print Statements

```bash
pytest -s
```

### Stop on First Failure

```bash
pytest -x
```

### Run Last Failed Tests

```bash
pytest --lf
```

### Drop into Debugger on Failure

```bash
pytest --pdb
```

---

## Common Issues & Solutions

### Issue: Database Connection Errors

**Solution**: Ensure test database exists
```bash
createdb finpilot_test
```

### Issue: Async Tests Not Running

**Solution**: Add `@pytest.mark.asyncio` decorator
```python
@pytest.mark.asyncio
async def test_something():
    ...
```

### Issue: Fixtures Not Found

**Solution**: Check `conftest.py` is in correct location and fixtures are defined

### Issue: Import Errors

**Solution**: Ensure you're running pytest from backend directory
```bash
cd backend
pytest
```

---

## Test Checklist

When adding new features, ensure you test:

- [ ] **Happy Path** - Feature works as expected
- [ ] **Authentication** - Requires proper auth
- [ ] **Authorization** - Users can only access their own data
- [ ] **Validation** - Invalid input is rejected
- [ ] **Edge Cases** - Boundary conditions
- [ ] **Error Handling** - Proper error responses
- [ ] **Database** - Data is persisted correctly
- [ ] **Cleanup** - Resources are cleaned up

---

## Current Test Coverage

### Implemented Tests

✅ **Authentication** (`test_auth.py`)
- User registration
- Login/logout
- Token refresh
- Password reset
- Email verification
- Protected endpoints

✅ **Financial Accounts** (`test_accounts.py`)
- Account creation
- Account retrieval
- Account updates
- Account deletion
- Filtering and pagination

### Tests To Be Added

⏳ **Transactions** (`test_transactions.py`)
⏳ **AI Copilot** (`test_copilot.py`)
⏳ **Recommendations** (`test_recommendations.py`)
⏳ **Documents** (`test_documents.py`)
⏳ **Simulations** (`test_simulations.py`)
⏳ **Workflows** (`test_workflows.py`)

---

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/20/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites)

---

**Made with ❤️ by Bob**