import { useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';

export default function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();
  const { logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const menuItems = [
    { icon: '🏠', label: 'Dashboard', path: '/dashboard' },
    { icon: '💳', label: 'Accounts', path: '/accounts' },
    { icon: '📊', label: 'Transactions', path: '/transactions' },
    { icon: '📄', label: 'Documents', path: '/documents' },
  ];

  const isActive = (path: string) => location.pathname === path;

  return (
    <aside
      style={{
        width: '240px',
        backgroundColor: 'white',
        borderRight: '1px solid rgb(229 231 235)',
        height: '100vh',
        position: 'fixed',
        left: 0,
        top: 0,
        display: 'flex',
        flexDirection: 'column',
        padding: '1.5rem 0',
      }}
    >
      {/* Logo */}
      <div style={{ padding: '0 1.5rem', marginBottom: '2rem' }}>
        <h1
          style={{
            fontSize: '1.5rem',
            fontWeight: 'bold',
            background: 'linear-gradient(135deg, rgb(59 130 246) 0%, rgb(147 51 234) 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
          }}
        >
          FinPilot AI
        </h1>
      </div>

      {/* Navigation */}
      <nav style={{ flex: 1, padding: '0 0.75rem' }}>
        {menuItems.map((item) => (
          <button
            key={item.path}
            onClick={() => navigate(item.path)}
            style={{
              width: '100%',
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem',
              padding: '0.75rem 1rem',
              marginBottom: '0.25rem',
              borderRadius: '0.5rem',
              border: 'none',
              backgroundColor: isActive(item.path) ? 'rgb(239 246 255)' : 'transparent',
              color: isActive(item.path) ? 'rgb(59 130 246)' : 'rgb(107 114 128)',
              fontSize: '0.875rem',
              fontWeight: isActive(item.path) ? '600' : '500',
              cursor: 'pointer',
              transition: 'all 0.2s',
              textAlign: 'left',
            }}
            onMouseEnter={(e) => {
              if (!isActive(item.path)) {
                e.currentTarget.style.backgroundColor = 'rgb(249 250 251)';
              }
            }}
            onMouseLeave={(e) => {
              if (!isActive(item.path)) {
                e.currentTarget.style.backgroundColor = 'transparent';
              }
            }}
          >
            <span style={{ fontSize: '1.25rem' }}>{item.icon}</span>
            <span>{item.label}</span>
          </button>
        ))}
      </nav>

      {/* Bottom Actions */}
      <div style={{ padding: '0 0.75rem', borderTop: '1px solid rgb(229 231 235)', paddingTop: '1rem' }}>
        <button
          onClick={() => navigate('/profile')}
          style={{
            width: '100%',
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
            padding: '0.75rem 1rem',
            marginBottom: '0.25rem',
            borderRadius: '0.5rem',
            border: 'none',
            backgroundColor: 'transparent',
            color: 'rgb(107 114 128)',
            fontSize: '0.875rem',
            fontWeight: '500',
            cursor: 'pointer',
            transition: 'all 0.2s',
            textAlign: 'left',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = 'rgb(249 250 251)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = 'transparent';
          }}
        >
          <span style={{ fontSize: '1.25rem' }}>⚙️</span>
          <span>Settings</span>
        </button>

        <button
          onClick={handleLogout}
          style={{
            width: '100%',
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
            padding: '0.75rem 1rem',
            borderRadius: '0.5rem',
            border: 'none',
            backgroundColor: 'transparent',
            color: 'rgb(239 68 68)',
            fontSize: '0.875rem',
            fontWeight: '500',
            cursor: 'pointer',
            transition: 'all 0.2s',
            textAlign: 'left',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = 'rgb(254 242 242)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = 'transparent';
          }}
        >
          <span style={{ fontSize: '1.25rem' }}>🚪</span>
          <span>Logout</span>
        </button>
      </div>
    </aside>
  );
}

// Made with Bob
