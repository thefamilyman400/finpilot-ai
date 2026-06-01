# FinPilot AI Frontend

Modern React-based financial management interface with AI-powered insights.

## Features

### Core Features
- 🎨 **Modern UI** - Clean, responsive design with Tailwind CSS
- 📊 **Interactive Dashboard** - Real-time financial overview with charts
- 💰 **Account Management** - Multi-account support with visual cards
- 📝 **Transaction Tracking** - Advanced filtering and categorization
- 📄 **Document Upload** - Drag-and-drop with AI analysis
- 👤 **User Profile** - Settings and preferences management

### AI Features
- 🤖 **AI Chat Assistant** - Always-visible sidebar with GPT-4 integration
- 🧮 **Integrated Calculators** - Retirement, investment, and loan calculators
- 💡 **Smart Insights** - AI-powered financial recommendations
- 📈 **Visual Analytics** - Interactive charts with Recharts

### Layout
- **Left Sidebar** - Navigation menu (240px fixed)
- **Center Content** - Page-specific content (flexible width)
- **Right AI Chat** - Always-visible assistant (360px fixed)

## Tech Stack

- **React** 19.0.0 - Latest React with modern features
- **TypeScript** 5.3 - Type-safe development
- **Vite** 5.0 - Fast build tool and dev server
- **Tailwind CSS** 4.0 - Utility-first styling
- **React Router** 7 - Client-side routing
- **TanStack Query** - Server state management
- **Zustand** - Global state management
- **Recharts** - Data visualization
- **Axios** - HTTP client
- **React Markdown** - Markdown rendering for AI responses

## Project Structure

```
frontend/
├── src/
│   ├── main.tsx                 # Application entry point
│   ├── App.tsx                  # Root component with routes
│   ├── index.css                # Global styles
│   ├── components/
│   │   ├── common/              # Reusable components
│   │   │   └── ProtectedRoute.tsx
│   │   └── layout/              # Layout components
│   │       ├── MainLayout.tsx
│   │       ├── Sidebar.tsx
│   │       └── ChatAssistantWithCalculators.tsx
│   ├── pages/                   # Page components
│   │   ├── auth/                # Authentication pages
│   │   ├── dashboard/           # Dashboard page
│   │   ├── accounts/            # Accounts management
│   │   ├── transactions/        # Transactions page
│   │   ├── documents/           # Documents page
│   │   ├── profile/             # Profile/Settings page
│   │   └── recommendations/     # Recommendations page
│   ├── services/                # API services
│   │   ├── api.ts               # Axios instance
│   │   ├── auth.service.ts
│   │   ├── account.service.ts
│   │   ├── transaction.service.ts
│   │   ├── document.service.ts
│   │   ├── copilot.service.ts
│   │   ├── simulation.service.ts
│   │   └── recommendation.service.ts
│   ├── store/                   # State management
│   │   └── authStore.ts         # Zustand auth store
│   └── types/                   # TypeScript types
│       └── index.ts
├── public/                      # Static assets
├── .env.development             # Development environment
├── .env.production              # Production environment
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

## Setup Instructions

### Prerequisites

- Node.js 18+ or higher
- npm or yarn
- Backend API running on http://localhost:8000

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

```bash
# .env.development is already configured for local development
# Backend API: http://localhost:8000/api/v1
```

### 3. Run Development Server

```bash
npm run dev
```

The application will be available at http://localhost:5173

### 4. Build for Production

```bash
npm run build
```

Build output will be in the `dist/` directory.

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Key Features Implementation

### Authentication Flow
1. User logs in → JWT tokens stored in localStorage
2. Zustand store manages auth state
3. ProtectedRoute guards authenticated pages
4. Axios interceptor adds auth header to requests

### State Management
- **Global State**: Zustand for authentication
- **Server State**: React Query for API data
- **Local State**: React useState for UI state

### API Integration
- Centralized Axios instance with interceptors
- Service layer pattern for API calls
- Automatic token refresh on 401 errors
- Type-safe request/response handling

### Layout System
```
┌─────────────────────────────────────────────────────┐
│  Sidebar (240px)  │  Content (flex)  │  Chat (360px) │
│                   │                  │               │
│  - Dashboard      │  Page-specific   │  AI Assistant │
│  - Accounts       │  content         │  + Calculators│
│  - Transactions   │                  │               │
│  - Documents      │                  │               │
│  - Settings       │                  │               │
│  - Logout         │                  │               │
└─────────────────────────────────────────────────────┘
```

## Currency

Default currency is **INR (₹)** throughout the application.

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Development Guidelines

### Code Style
- Use TypeScript for type safety
- Follow React best practices
- Use functional components with hooks
- Keep components small and focused

### Component Structure
```typescript
// Example component structure
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';

export const MyComponent = () => {
  // 1. Hooks
  const [state, setState] = useState();
  const { data, isLoading } = useQuery(...);

  // 2. Event handlers
  const handleClick = () => { ... };

  // 3. Render
  return <div>...</div>;
};
```

### API Service Pattern
```typescript
// services/example.service.ts
export const exampleService = {
  getItems: async (): Promise<Item[]> => {
    const response = await api.get<Item[]>('/items');
    return response.data;
  },
  
  createItem: async (data: ItemCreate): Promise<Item> => {
    const response = await api.post<Item>('/items', data);
    return response.data;
  },
};
```

## Troubleshooting

### Port Already in Use
```bash
# Kill process on port 5173
npx kill-port 5173

# Or use a different port
npm run dev -- --port 3000
```

### API Connection Issues
- Verify backend is running on http://localhost:8000
- Check CORS configuration in backend
- Verify .env.development has correct API URL

### Build Errors
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

## Documentation

- **Project Status**: `../docs/project-current-status.md`
- **Technical Architecture**: `../docs/technical-architecture.md`
- **Backend API**: `../backend/README.md`

## License

[Your License Here]

---

**Made with ❤️ by Bob**
