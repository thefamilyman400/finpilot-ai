# FinPilot AI - Technical Architecture & Logic

**Last Updated:** May 20, 2026  
**Version:** 1.0

---

## 📋 Table of Contents
1. [Overview](#overview)
2. [Technology Stack](#technology-stack)
3. [Architecture Patterns](#architecture-patterns)
4. [Application Flow](#application-flow)
5. [Component Structure](#component-structure)
6. [State Management](#state-management)
7. [API Integration](#api-integration)
8. [Authentication Flow](#authentication-flow)
9. [AI Chat System](#ai-chat-system)
10. [Data Flow Diagrams](#data-flow-diagrams)

---

## 🎯 Overview

FinPilot AI is a **full-stack personal finance management platform** with AI-powered insights. The application follows a **client-server architecture** with a React frontend and FastAPI backend.

### Core Concept
- **Frontend:** Single Page Application (SPA) with React
- **Backend:** RESTful API with FastAPI
- **Database:** PostgreSQL with SQLAlchemy ORM
- **AI:** OpenAI GPT integration for financial analysis

---

## 🛠 Technology Stack

### Frontend Stack
```
React 19.0.0          - UI library with latest features
TypeScript 5.3        - Type-safe JavaScript
Vite 5.0              - Build tool & dev server
Tailwind CSS 4.0      - Utility-first CSS framework
React Router 7        - Client-side routing
TanStack Query        - Server state management
Zustand               - Global state management
Recharts              - Data visualization
Axios                 - HTTP client
React Markdown        - Markdown rendering for AI responses
```

### Backend Stack
```
FastAPI 0.104.1       - Modern Python web framework
SQLAlchemy 2.0.23     - ORM for database operations
Pydantic 2.5.0        - Data validation
PostgreSQL 15+        - Relational database
OpenAI API            - AI/ML capabilities
JWT                   - Authentication tokens
Bcrypt                - Password hashing
```

### Development Tools
```
ESLint                - Code linting
Prettier              - Code formatting
Pytest                - Backend testing
Git                   - Version control
```

---

## 🏗 Architecture Patterns

### 1. **Component-Based Architecture (Frontend)**
```
┌─────────────────────────────────────────┐
│           React Application             │
├─────────────────────────────────────────┤
│  Pages (Route Components)               │
│  ├─ Dashboard                           │
│  ├─ Accounts                            │
│  ├─ Transactions                        │
│  └─ Documents                           │
├─────────────────────────────────────────┤
│  Layout Components                      │
│  ├─ MainLayout (wrapper)                │
│  ├─ Sidebar (navigation)                │
│  └─ ChatAssistant (AI chat)             │
├─────────────────────────────────────────┤
│  Services (API Layer)                   │
│  ├─ accountService                      │
│  ├─ transactionService                  │
│  ├─ documentService                     │
│  └─ copilotService                      │
├─────────────────────────────────────────┤
│  State Management                       │
│  ├─ Zustand (auth state)                │
│  └─ React Query (server state)          │
└─────────────────────────────────────────┘
```

### 2. **Layered Architecture (Backend)**
```
┌─────────────────────────────────────────┐
│         API Layer (FastAPI)             │
│  ├─ /api/v1/auth                        │
│  ├─ /api/v1/accounts                    │
│  ├─ /api/v1/transactions                │
│  ├─ /api/v1/documents                   │
│  ├─ /api/v1/copilot                     │
│  └─ /api/v1/simulations                 │
├─────────────────────────────────────────┤
│         Service Layer                   │
│  ├─ account_service.py                  │
│  ├─ transaction_service.py              │
│  ├─ document_service.py                 │
│  ├─ ai_service.py                       │
│  └─ simulation_service.py               │
├─────────────────────────────────────────┤
│         Data Layer (SQLAlchemy)         │
│  ├─ User Model                          │
│  ├─ Account Model                       │
│  ├─ Transaction Model                   │
│  ├─ Document Model                      │
│  ├─ Conversation Model                  │
│  └─ Message Model                       │
├─────────────────────────────────────────┤
│         Database (PostgreSQL)           │
└─────────────────────────────────────────┘
```

### 3. **RESTful API Design**
- **Resource-based URLs:** `/api/v1/accounts`, `/api/v1/transactions`
- **HTTP Methods:** GET (read), POST (create), PUT/PATCH (update), DELETE (delete)
- **Status Codes:** 200 (success), 201 (created), 400 (bad request), 401 (unauthorized), 404 (not found), 500 (server error)
- **JSON Responses:** Consistent response format with data/error structure

---

## 🔄 Application Flow

### 1. **User Journey**
```
1. User visits app → Redirected to /login
2. User logs in → JWT token stored in localStorage
3. User redirected to /dashboard
4. Dashboard loads with MainLayout:
   ├─ Left: Sidebar with navigation
   ├─ Center: Dashboard content
   └─ Right: AI Chat Assistant
5. User navigates via sidebar → Page changes, layout persists
6. User interacts with AI chat → Conversations saved to database
7. User performs actions → API calls → Database updates → UI refreshes
```

### 2. **Component Rendering Flow**
```
App.tsx (Root)
  └─ BrowserRouter
      └─ Routes
          ├─ /login → Login.tsx
          ├─ /register → Register.tsx
          └─ Protected Routes (require auth)
              ├─ /dashboard → MainLayout → Dashboard.tsx
              ├─ /accounts → MainLayout → Accounts.tsx
              ├─ /transactions → MainLayout → Transactions.tsx
              └─ /documents → MainLayout → Documents.tsx
```

### 3. **MainLayout Structure**
```jsx
<MainLayout>
  <div style={{ display: 'flex' }}>
    {/* Left Sidebar - 240px fixed */}
    <Sidebar>
      - Logo
      - Navigation Menu
      - Settings/Logout
    </Sidebar>

    {/* Center Content - flexible width */}
    <main style={{ flex: 1, marginLeft: '240px', marginRight: '360px' }}>
      {children} // Page-specific content
    </main>

    {/* Right AI Chat - 360px fixed */}
    <ChatAssistant>
      - Chat messages
      - Calculator forms
      - Minimize button
    </ChatAssistant>
  </div>
</MainLayout>
```

---

## 🧩 Component Structure

### Core Components

#### 1. **Sidebar Component**
```typescript
// Location: frontend/src/components/layout/Sidebar.tsx
// Purpose: Fixed left navigation menu

Features:
- Navigation links (Dashboard, Accounts, Transactions, Documents)
- Active state highlighting
- Settings and Logout buttons
- Gradient logo
- Hover effects

State: None (stateless, uses React Router for navigation)
```

#### 2. **ChatAssistant Component**
```typescript
// Location: frontend/src/components/layout/ChatAssistantWithCalculators.tsx
// Purpose: AI chat interface with calculator integration

Features:
- Real-time AI conversations
- Calculator detection (retirement, investment, loan)
- Inline calculator forms
- Message history
- Minimize/maximize functionality
- Conversation persistence

State:
- messages: ChatMessage[]
- input: string
- isLoading: boolean
- isMinimized: boolean
- conversationId: string | null
- showCalculator: 'retirement' | 'investment' | 'loan' | null
```

#### 3. **MainLayout Component**
```typescript
// Location: frontend/src/components/layout/MainLayout.tsx
// Purpose: Wrapper component for consistent layout

Features:
- Combines Sidebar + Content + ChatAssistant
- Provides consistent spacing
- Handles responsive layout

Props:
- children: ReactNode (page content)
```

### Page Components

#### 1. **Dashboard**
```typescript
// Location: frontend/src/pages/dashboard/Dashboard.tsx

Features:
- Welcome message
- 4 stat cards (Balance, Accounts, Transactions, AI Copilot)
- Spending by Category pie chart
- Account Balances bar chart
- Loading skeletons
- Error handling

Data Sources:
- accounts (from accountService)
- transactions (from transactionService)

State Management:
- React Query for server state
- Local state for UI interactions
```

#### 2. **Accounts**
```typescript
// Location: frontend/src/pages/accounts/Accounts.tsx

Features:
- Account list with cards
- Add/Edit account modal
- Multi-currency support
- Account type selection
- Delete confirmation

Data Sources:
- accounts (from accountService)

Mutations:
- createAccount
- updateAccount
- deleteAccount
```

#### 3. **Transactions**
```typescript
// Location: frontend/src/pages/transactions/Transactions.tsx

Features:
- Transaction list with filters
- Add transaction form
- 30+ categories
- Date range filtering
- Account filtering

Data Sources:
- transactions (from transactionService)
- accounts (for dropdown)

Mutations:
- createTransaction
- deleteTransaction
```

#### 4. **Documents**
```typescript
// Location: frontend/src/pages/documents/Documents.tsx

Features:
- Drag-and-drop file upload
- Document list
- AI analysis display
- File preview
- Delete functionality

Data Sources:
- documents (from documentService)

Mutations:
- uploadDocument
- deleteDocument
```

---

## 📊 State Management

### 1. **Global State (Zustand)**
```typescript
// Location: frontend/src/store/authStore.ts
// Purpose: Authentication state management

interface AuthState {
  user: User | null;
  access_token: string | null;
  refresh_token: string | null;
  isAuthenticated: boolean;
  
  login: (tokens, user) => void;
  logout: () => void;
  setUser: (user) => void;
}

// Persisted to localStorage
// Accessible from any component
```

### 2. **Server State (React Query)**
```typescript
// Purpose: Caching and synchronizing server data

Features:
- Automatic caching
- Background refetching
- Optimistic updates
- Loading/error states
- Query invalidation

Example:
const { data, isLoading, error } = useQuery({
  queryKey: ['accounts'],
  queryFn: accountService.getAccounts,
});

const mutation = useMutation({
  mutationFn: accountService.createAccount,
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['accounts'] });
  },
});
```

### 3. **Local Component State**
```typescript
// Purpose: UI-specific state (forms, modals, etc.)

Examples:
- Form inputs: useState()
- Modal visibility: useState()
- Loading indicators: useState()
- Selected items: useState()
```

---

## 🔌 API Integration

### Service Layer Pattern
```typescript
// Location: frontend/src/services/

// Example: account.service.ts
export const accountService = {
  getAccounts: async (): Promise<Account[]> => {
    const response = await api.get<Account[]>('/accounts');
    return response.data;
  },
  
  createAccount: async (data: AccountCreate): Promise<Account> => {
    const response = await api.post<Account>('/accounts', data);
    return response.data;
  },
  
  // ... more methods
};

// Centralized API client (api.ts)
const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: { 'Content-Type': 'application/json' },
});

// Request interceptor (adds auth token)
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor (handles errors)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Redirect to login
    }
    return Promise.reject(error);
  }
);
```

### Backend API Endpoints
```python
# Location: backend/app/api/v1/

# Authentication
POST   /auth/register          # Create new user
POST   /auth/login             # Login and get tokens
POST   /auth/refresh           # Refresh access token
GET    /auth/me                # Get current user

# Accounts
GET    /accounts               # List all accounts
POST   /accounts               # Create account
GET    /accounts/{id}          # Get account details
PUT    /accounts/{id}          # Update account
DELETE /accounts/{id}          # Delete account

# Transactions
GET    /transactions           # List transactions (with filters)
POST   /transactions           # Create transaction
GET    /transactions/{id}      # Get transaction details
PUT    /transactions/{id}      # Update transaction
DELETE /transactions/{id}      # Delete transaction
GET    /transactions/stats     # Get statistics

# Documents
GET    /documents              # List documents
POST   /documents/upload       # Upload document
GET    /documents/{id}         # Get document details
DELETE /documents/{id}         # Delete document
POST   /documents/{id}/analyze # Analyze with AI

# AI Copilot
POST   /copilot/chat           # Send message (creates conversation if needed)
GET    /copilot/conversations  # List conversations
POST   /copilot/conversations  # Create conversation
GET    /copilot/conversations/{id}  # Get conversation with messages
DELETE /copilot/conversations/{id}  # Delete conversation

# Simulations
POST   /simulations            # Run simulation
GET    /simulations            # List simulations
GET    /simulations/{id}       # Get simulation details
```

---

## 🔐 Authentication Flow

### 1. **Registration Flow**
```
User fills registration form
  ↓
POST /api/v1/auth/register
  ↓
Backend validates data
  ↓
Backend hashes password (bcrypt)
  ↓
Backend creates user in database
  ↓
Backend returns user data
  ↓
Frontend redirects to login
```

### 2. **Login Flow**
```
User enters credentials
  ↓
POST /api/v1/auth/login
  ↓
Backend validates credentials
  ↓
Backend generates JWT tokens
  ├─ access_token (15 min expiry)
  └─ refresh_token (7 days expiry)
  ↓
Frontend stores tokens in localStorage
  ↓
Frontend stores user in Zustand
  ↓
Frontend redirects to /dashboard
```

### 3. **Protected Route Access**
```
User navigates to protected route
  ↓
ProtectedRoute component checks auth
  ↓
If not authenticated → Redirect to /login
  ↓
If authenticated → Render page
  ↓
API requests include Authorization header
  ↓
Backend validates JWT token
  ↓
If valid → Process request
If invalid → Return 401 Unauthorized
```

### 4. **Token Refresh Flow**
```
Access token expires (15 min)
  ↓
API request returns 401
  ↓
Frontend intercepts 401 response
  ↓
POST /api/v1/auth/refresh (with refresh_token)
  ↓
Backend validates refresh token
  ↓
Backend generates new access_token
  ↓
Frontend stores new token
  ↓
Frontend retries original request
```

---

## 🤖 AI Chat System

### Architecture
```
┌─────────────────────────────────────────────────────┐
│              ChatAssistant Component                │
├─────────────────────────────────────────────────────┤
│  1. User types message                              │
│  2. Check if calculator request                     │
│     ├─ Yes → Show calculator form                   │
│     └─ No → Send to AI                              │
│  3. POST /api/v1/copilot/chat                       │
│  4. Backend processes with OpenAI                   │
│  5. Response displayed in chat                      │
│  6. Conversation saved to database                  │
└─────────────────────────────────────────────────────┘
```

### Calculator Integration
```typescript
// Detection Logic
const detectCalculatorRequest = (text: string) => {
  const lower = text.toLowerCase();
  if (lower.includes('retirement')) return 'retirement';
  if (lower.includes('investment')) return 'investment';
  if (lower.includes('loan')) return 'loan';
  return null;
};

// Flow
User types "retirement calculator"
  ↓
detectCalculatorRequest() returns 'retirement'
  ↓
setShowCalculator('retirement')
  ↓
RetirementCalculatorForm renders
  ↓
User fills form and clicks Calculate
  ↓
POST /api/v1/simulations (with parameters)
  ↓
Backend runs calculation
  ↓
Results formatted and displayed in chat
```

### AI Chat Backend Flow
```python
# POST /api/v1/copilot/chat

1. Receive message and optional conversation_id
2. If no conversation_id:
   - Create new conversation
   - Generate title from first message
3. Save user message to database
4. Gather financial context:
   - User's accounts
   - Recent transactions
   - Document summaries
5. Build prompt with context
6. Call OpenAI API (GPT-4)
7. Save assistant response to database
8. Return conversation_id + messages
```

### Conversation Persistence
```
Database Schema:

conversations
├─ id (UUID)
├─ user_id (FK)
├─ title (string)
├─ created_at (timestamp)
├─ updated_at (timestamp)
└─ last_message_at (timestamp)

messages
├─ id (UUID)
├─ conversation_id (FK)
├─ role ('user' | 'assistant')
├─ content (text)
├─ tokens_used (int)
├─ model (string)
└─ created_at (timestamp)
```

---

## 📈 Data Flow Diagrams

### 1. **Account Creation Flow**
```
User clicks "Add Account"
  ↓
Modal opens with form
  ↓
User fills form (name, type, balance, currency)
  ↓
User clicks "Create"
  ↓
Frontend validates input
  ↓
POST /api/v1/accounts
  {
    "account_name": "Savings",
    "account_type": "savings",
    "balance": 5000,
    "currency": "USD"
  }
  ↓
Backend validates with Pydantic
  ↓
Backend creates Account model
  ↓
Backend saves to database
  ↓
Backend returns Account object
  ↓
Frontend invalidates 'accounts' query
  ↓
React Query refetches accounts
  ↓
UI updates with new account
  ↓
Modal closes
```

### 2. **Transaction Filtering Flow**
```
User selects filters:
├─ Account: "Checking"
├─ Category: "groceries"
├─ Date range: "2024-01-01" to "2024-01-31"
└─ Type: "debit"
  ↓
Frontend updates filter state
  ↓
React Query detects dependency change
  ↓
GET /api/v1/transactions?account_id=xxx&category=groceries&start_date=2024-01-01&end_date=2024-01-31&transaction_type=debit
  ↓
Backend builds SQL query with filters
  ↓
Backend executes query
  ↓
Backend returns filtered transactions
  ↓
Frontend displays results
```

### 3. **Document Upload & Analysis Flow**
```
User drags file to upload area
  ↓
File dropped
  ↓
Frontend detects file type
  ↓
POST /api/v1/documents/upload (multipart/form-data)
  ↓
Backend receives file
  ↓
Backend saves to uploads/ directory
  ↓
Backend creates Document record
  ↓
Backend extracts text (OCR for images, PyPDF2 for PDFs)
  ↓
Backend calls OpenAI for analysis
  ↓
Backend saves analysis to document
  ↓
Backend returns document with analysis
  ↓
Frontend displays document in list
  ↓
User clicks document
  ↓
Frontend shows analysis results
```

---

## 🎨 UI/UX Patterns

### 1. **Loading States**
```typescript
// Pattern: Skeleton screens
if (isLoading) {
  return (
    <div className="card" style={{ animation: 'pulse 2s infinite' }}>
      <div style={{ height: '1rem', backgroundColor: 'rgb(229 231 235)' }} />
      <div style={{ height: '2rem', backgroundColor: 'rgb(229 231 235)' }} />
    </div>
  );
}
```

### 2. **Error Handling**
```typescript
// Pattern: User-friendly error messages
if (error) {
  return (
    <div style={{ backgroundColor: 'rgb(254 242 242)', padding: '1rem' }}>
      <p style={{ color: 'rgb(153 27 27)' }}>
        ⚠️ Error loading data. Please try again.
      </p>
    </div>
  );
}
```

### 3. **Optimistic Updates**
```typescript
// Pattern: Update UI before server confirms
const mutation = useMutation({
  mutationFn: deleteAccount,
  onMutate: async (accountId) => {
    // Cancel outgoing refetches
    await queryClient.cancelQueries({ queryKey: ['accounts'] });
    
    // Snapshot previous value
    const previous = queryClient.getQueryData(['accounts']);
    
    // Optimistically update
    queryClient.setQueryData(['accounts'], (old) =>
      old.filter((acc) => acc.id !== accountId)
    );
    
    return { previous };
  },
  onError: (err, variables, context) => {
    // Rollback on error
    queryClient.setQueryData(['accounts'], context.previous);
  },
});
```

---

## 🔒 Security Measures

### Frontend Security
1. **JWT Storage:** Tokens in localStorage (consider httpOnly cookies for production)
2. **XSS Prevention:** React automatically escapes content
3. **CSRF Protection:** Not needed for JWT-based auth
4. **Input Validation:** Client-side validation before API calls
5. **Protected Routes:** ProtectedRoute component checks authentication

### Backend Security
1. **Password Hashing:** Bcrypt with salt
2. **JWT Tokens:** Signed with secret key, short expiry
3. **SQL Injection Prevention:** SQLAlchemy ORM parameterized queries
4. **CORS:** Configured for specific origins
5. **Rate Limiting:** Can be added with slowapi
6. **Input Validation:** Pydantic schemas validate all inputs

---

## 🚀 Performance Optimizations

### Frontend
1. **Code Splitting:** React.lazy() for route-based splitting
2. **Memoization:** useMemo() and useCallback() for expensive computations
3. **Virtual Scrolling:** For large lists (can be added)
4. **Image Optimization:** Lazy loading, proper sizing
5. **Bundle Size:** Tree shaking, minification

### Backend
1. **Database Indexing:** Indexes on frequently queried columns
2. **Query Optimization:** Eager loading to avoid N+1 queries
3. **Caching:** Can add Redis for frequently accessed data
4. **Connection Pooling:** SQLAlchemy connection pool
5. **Async Operations:** FastAPI async endpoints

---

## 📦 Deployment Architecture

### Development
```
Frontend: http://localhost:5173 (Vite dev server)
Backend: http://localhost:8000 (Uvicorn)
Database: localhost:5432 (PostgreSQL)
```

### Production (Recommended)
```
Frontend: Static files on CDN (Vercel, Netlify, Cloudflare)
Backend: Docker container on cloud (AWS, GCP, Azure)
Database: Managed PostgreSQL (AWS RDS, Supabase)
AI: OpenAI API (external service)
```

---

## 🧪 Testing Strategy

### Frontend Testing
```typescript
// Unit Tests: Component logic
// Integration Tests: Component + API
// E2E Tests: Full user flows

Example:
describe('Dashboard', () => {
  it('displays account balance', async () => {
    render(<Dashboard />);
    await waitFor(() => {
      expect(screen.getByText(/Total Balance/i)).toBeInTheDocument();
    });
  });
});
```

### Backend Testing
```python
# Unit Tests: Service functions
# Integration Tests: API endpoints
# Database Tests: Model operations

Example:
def test_create_account(client, auth_headers):
    response = client.post(
        "/api/v1/accounts",
        json={"account_name": "Test", "account_type": "checking"},
        headers=auth_headers
    )
    assert response.status_code == 201
    assert response.json()["account_name"] == "Test"
```

---

## 📚 Key Takeaways

### Architecture Principles
1. **Separation of Concerns:** Clear boundaries between layers
2. **Single Responsibility:** Each component/service has one job
3. **DRY (Don't Repeat Yourself):** Reusable components and services
4. **Composition over Inheritance:** React components compose together
5. **API-First Design:** Backend exposes RESTful API

### Design Patterns Used
1. **Container/Presentational:** Smart vs. dumb components
2. **Service Layer:** Centralized API communication
3. **Repository Pattern:** Data access abstraction (SQLAlchemy)
4. **Observer Pattern:** React Query for state synchronization
5. **Factory Pattern:** Service creation and dependency injection

### Best Practices
1. **Type Safety:** TypeScript on frontend, Pydantic on backend
2. **Error Handling:** Graceful degradation, user-friendly messages
3. **Loading States:** Skeleton screens, progress indicators
4. **Accessibility:** Semantic HTML, ARIA labels
5. **Code Organization:** Feature-based folder structure

---

## 🎓 Learning Resources

### Frontend
- React Docs: https://react.dev
- TypeScript Handbook: https://www.typescriptlang.org/docs/
- TanStack Query: https://tanstack.com/query
- Tailwind CSS: https://tailwindcss.com

### Backend
- FastAPI Docs: https://fastapi.tiangolo.com
- SQLAlchemy: https://docs.sqlalchemy.org
- Pydantic: https://docs.pydantic.dev
- OpenAI API: https://platform.openai.com/docs

---

**Made with Bob - Your AI Development Assistant**