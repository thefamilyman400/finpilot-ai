# Windows Setup Guide for FinPilot AI Backend

## Step-by-Step Setup for Windows

### 1. Install PostgreSQL on Windows

#### Option A: Using Official Installer (Recommended)

1. **Download PostgreSQL:**
   - Visit: https://www.postgresql.org/download/windows/
   - Download the installer (PostgreSQL 15 or 16)
   - Run the installer

2. **During Installation:**
   - Set a password for the `postgres` user (remember this!)
   - Default port: 5432 (keep it)
   - Install pgAdmin 4 (GUI tool - recommended)

3. **Add PostgreSQL to PATH (Optional):**
   - Right-click "This PC" → Properties → Advanced System Settings
   - Environment Variables → System Variables → Path → Edit
   - Add: `C:\Program Files\PostgreSQL\15\bin`
   - Click OK and restart PowerShell

#### Option B: Using pgAdmin 4 (GUI - Easiest)

If you installed pgAdmin 4 with PostgreSQL:

1. **Open pgAdmin 4** (search in Start menu)
2. **Connect to PostgreSQL:**
   - Expand "Servers" → "PostgreSQL 15"
   - Enter your postgres password
3. **Create Database:**
   - Right-click "Databases" → Create → Database
   - Name: `finpilot`
   - Owner: `postgres`
   - Click "Save"

✅ **Done! Skip to Step 2 below**

#### Option C: Using PowerShell/CMD

If PostgreSQL is installed but not in PATH:

```powershell
# Navigate to PostgreSQL bin directory
cd "C:\Program Files\PostgreSQL\15\bin"

# Create database using psql
.\psql.exe -U postgres -c "CREATE DATABASE finpilot;"

# Or open psql interactive shell
.\psql.exe -U postgres
# Then type: CREATE DATABASE finpilot;
# Then type: \q to exit
```

### 2. Install Python Dependencies

```powershell
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install lightweight dependencies (Phase 1 & 2 only)
pip install -r requirements-phase2.txt

# This will take 2-5 minutes and download ~200 MB
```

### 3. Configure Environment Variables

```powershell
# Copy example file
copy .env.example .env

# Edit .env file (use notepad or VS Code)
notepad .env
```

**Update these values in .env:**

```env
# Database - Update with your PostgreSQL password
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/finpilot

# Security - Generate a secure key
SECRET_KEY=your-secret-key-here

# Other settings (can keep defaults)
DEBUG=True
ENVIRONMENT=development
HOST=0.0.0.0
PORT=8000
```

**To generate a secure SECRET_KEY:**

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output and paste it as your SECRET_KEY in .env

### 4. Verify Database Connection

Test if you can connect to PostgreSQL:

```powershell
# Option 1: Using psql (if in PATH)
psql -U postgres -d finpilot -c "SELECT version();"

# Option 2: Using Python
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "C:\Users\0025BL744\finpilot-ai\backend\venv\Lib\site-packages\psycopg2\__init__.py", line 122, in connect
    conn = _connect(dsn, connection_factory=connection_factory, **kwasync)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
psycopg2.OperationalError: connection to server at "localhost" (::1), port 5432 failed: FATAL:  password authentication failed for user "postgres"
```

### 5. Run the Application

```powershell
# Make sure virtual environment is activated
# You should see (venv) in your prompt

# Run the FastAPI application
python main.py
```

**Expected output:**
```
🚀 Starting FinPilot AI Backend...
📝 Environment: development
🔧 Debug Mode: True
✅ Database initialized
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 6. Test the API

Open your browser and visit:
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health
- **Root:** http://localhost:8000

## Common Windows Issues & Solutions

### Issue 1: "psql is not recognized"

**Solution:** PostgreSQL bin folder not in PATH. Use one of these:

1. **Use pgAdmin 4 GUI** (easiest - see Option B above)
2. **Use full path:**
   ```powershell
   cd "C:\Program Files\PostgreSQL\15\bin"
   .\psql.exe -U postgres
   ```
3. **Add to PATH** (see Option A above)

### Issue 2: "python is not recognized"

**Solution:** Python not installed or not in PATH.

1. Download Python 3.11+ from https://www.python.org/downloads/
2. During installation, check "Add Python to PATH"
3. Restart PowerShell

### Issue 3: "pip install fails with SSL error"

**Solution:**
```powershell
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements-phase2.txt
```

### Issue 4: "Port 8000 already in use"

**Solution:** Find and kill the process:
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual number)
taskkill /PID <PID> /F

# Or use a different port
python main.py --port 8001
```

### Issue 5: "Cannot connect to database"

**Solutions:**

1. **Check PostgreSQL is running:**
   - Open Services (Win + R → services.msc)
   - Find "postgresql-x64-15" service
   - Ensure it's "Running"
   - If not, right-click → Start

2. **Verify credentials in .env:**
   - Check DATABASE_URL has correct password
   - Check database name is `finpilot`
   - Check port is 5432

3. **Test connection:**
   ```powershell
   # Using pgAdmin 4 - try to connect
   # Or using psql:
   "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -d finpilot
   ```

### Issue 6: "Module not found" errors

**Solution:** Ensure virtual environment is activated:
```powershell
# You should see (venv) in your prompt
# If not, activate it:
.\venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements-phase2.txt
```

## Quick Start Checklist

- [ ] PostgreSQL installed and running
- [ ] Database `finpilot` created (using pgAdmin or psql)
- [ ] Python 3.11+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements-phase2.txt`)
- [ ] `.env` file configured with correct DATABASE_URL and SECRET_KEY
- [ ] Application runs successfully (`python main.py`)
- [ ] Can access http://localhost:8000/docs

## Next Steps After Setup

Once everything is running:

1. **Test the API** at http://localhost:8000/docs
2. **Register a user** using the `/api/v1/auth/register` endpoint
3. **Login** to get JWT tokens
4. **Test authenticated endpoints** using the "Authorize" button in Swagger UI

## Need Help?

If you encounter issues not covered here:

1. Check the error message carefully
2. Verify PostgreSQL service is running
3. Check .env file configuration
4. Ensure virtual environment is activated
5. Try restarting PowerShell/terminal

---

**Ready for Phase 2!** Once setup is complete, you can start implementing financial features.