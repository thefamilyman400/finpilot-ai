import { useAuthStore } from '../../store/authStore';
import MainLayout from '../../components/layout/MainLayout';

export default function Profile() {
  const user = useAuthStore((state) => state.user);

  return (
    <MainLayout>
      <div style={{ padding: '2rem' }}>
        <div style={{ maxWidth: '800px', margin: '0 auto' }}>
          {/* Header */}
          <div style={{ marginBottom: '2rem' }}>
            <h1 style={{ fontSize: '1.875rem', fontWeight: 'bold', color: 'rgb(17 24 39)', marginBottom: '0.5rem' }}>
              Profile & Settings
            </h1>
            <p style={{ color: 'rgb(107 114 128)' }}>
              Manage your account settings and preferences
            </p>
          </div>

          {/* Profile Information */}
          <div style={{ backgroundColor: 'white', borderRadius: '0.5rem', padding: '1.5rem', marginBottom: '1.5rem', boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.1)' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem', color: 'rgb(17 24 39)' }}>
              Profile Information
            </h2>
            <div style={{ display: 'grid', gap: '1rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '500', color: 'rgb(107 114 128)', marginBottom: '0.5rem' }}>
                  Full Name
                </label>
                <input
                  type="text"
                  value={user?.full_name || ''}
                  disabled
                  style={{
                    width: '100%',
                    padding: '0.5rem 0.75rem',
                    border: '1px solid rgb(209 213 219)',
                    borderRadius: '0.375rem',
                    fontSize: '0.875rem',
                    backgroundColor: 'rgb(249 250 251)',
                    color: 'rgb(107 114 128)',
                  }}
                />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '500', color: 'rgb(107 114 128)', marginBottom: '0.5rem' }}>
                  Email
                </label>
                <input
                  type="email"
                  value={user?.email || ''}
                  disabled
                  style={{
                    width: '100%',
                    padding: '0.5rem 0.75rem',
                    border: '1px solid rgb(209 213 219)',
                    borderRadius: '0.375rem',
                    fontSize: '0.875rem',
                    backgroundColor: 'rgb(249 250 251)',
                    color: 'rgb(107 114 128)',
                  }}
                />
              </div>
            </div>
          </div>

          {/* App Settings */}
          <div style={{ backgroundColor: 'white', borderRadius: '0.5rem', padding: '1.5rem', marginBottom: '1.5rem', boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.1)' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem', color: 'rgb(17 24 39)' }}>
              Application Settings
            </h2>
            <div style={{ display: 'grid', gap: '1rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.75rem 0', borderBottom: '1px solid rgb(229 231 235)' }}>
                <div>
                  <div style={{ fontWeight: '500', fontSize: '0.875rem', color: 'rgb(17 24 39)' }}>Email Notifications</div>
                  <div style={{ fontSize: '0.75rem', color: 'rgb(107 114 128)', marginTop: '0.25rem' }}>Receive email updates about your finances</div>
                </div>
                <label style={{ position: 'relative', display: 'inline-block', width: '44px', height: '24px' }}>
                  <input type="checkbox" defaultChecked style={{ opacity: 0, width: 0, height: 0 }} />
                  <span style={{
                    position: 'absolute',
                    cursor: 'pointer',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    backgroundColor: 'rgb(59 130 246)',
                    borderRadius: '24px',
                    transition: '0.4s',
                  }}></span>
                </label>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.75rem 0', borderBottom: '1px solid rgb(229 231 235)' }}>
                <div>
                  <div style={{ fontWeight: '500', fontSize: '0.875rem', color: 'rgb(17 24 39)' }}>Dark Mode</div>
                  <div style={{ fontSize: '0.75rem', color: 'rgb(107 114 128)', marginTop: '0.25rem' }}>Switch to dark theme</div>
                </div>
                <label style={{ position: 'relative', display: 'inline-block', width: '44px', height: '24px' }}>
                  <input type="checkbox" style={{ opacity: 0, width: 0, height: 0 }} />
                  <span style={{
                    position: 'absolute',
                    cursor: 'pointer',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    backgroundColor: 'rgb(209 213 219)',
                    borderRadius: '24px',
                    transition: '0.4s',
                  }}></span>
                </label>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.75rem 0' }}>
                <div>
                  <div style={{ fontWeight: '500', fontSize: '0.875rem', color: 'rgb(17 24 39)' }}>AI Recommendations</div>
                  <div style={{ fontSize: '0.75rem', color: 'rgb(107 114 128)', marginTop: '0.25rem' }}>Get personalized financial advice</div>
                </div>
                <label style={{ position: 'relative', display: 'inline-block', width: '44px', height: '24px' }}>
                  <input type="checkbox" defaultChecked style={{ opacity: 0, width: 0, height: 0 }} />
                  <span style={{
                    position: 'absolute',
                    cursor: 'pointer',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    backgroundColor: 'rgb(59 130 246)',
                    borderRadius: '24px',
                    transition: '0.4s',
                  }}></span>
                </label>
              </div>
            </div>
          </div>

          {/* About */}
          <div style={{ backgroundColor: 'white', borderRadius: '0.5rem', padding: '1.5rem', boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.1)' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem', color: 'rgb(17 24 39)' }}>
              About FinPilot AI
            </h2>
            <div style={{ fontSize: '0.875rem', color: 'rgb(107 114 128)', lineHeight: '1.6' }}>
              <p style={{ marginBottom: '0.75rem' }}>
                <strong>Version:</strong> 1.0.0
              </p>
              <p style={{ marginBottom: '0.75rem' }}>
                FinPilot AI is your intelligent financial companion, helping you make smarter financial decisions with AI-powered insights and recommendations.
              </p>
              <p>
                <strong>Features:</strong>
              </p>
              <ul style={{ marginTop: '0.5rem', marginLeft: '1.5rem', listStyleType: 'disc' }}>
                <li>AI-powered financial advice</li>
                <li>Portfolio-grade calculators</li>
                <li>Document analysis</li>
                <li>Transaction tracking</li>
                <li>Personalized recommendations</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}

// Made with Bob
