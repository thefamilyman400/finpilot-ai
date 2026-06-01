import { useState } from 'react';
import { useAuthStore } from '../../store/authStore';
import { authService } from '../../services/auth.service';
import MainLayout from '../../components/layout/MainLayout';

export default function Profile() {
  const user = useAuthStore((state) => state.user);
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [passwordSuccess, setPasswordSuccess] = useState('');
  const [passwordLoading, setPasswordLoading] = useState(false);

  const validatePassword = (pwd: string): string | null => {
    if (pwd.length < 8) {
      return 'Password must be at least 8 characters long';
    }
    if (!/[A-Z]/.test(pwd)) {
      return 'Password must contain at least one uppercase letter';
    }
    if (!/[a-z]/.test(pwd)) {
      return 'Password must contain at least one lowercase letter';
    }
    if (!/\d/.test(pwd)) {
      return 'Password must contain at least one number';
    }
    return null;
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setPasswordError('');
    setPasswordSuccess('');

    // Validate inputs
    if (!currentPassword) {
      setPasswordError('Please enter your current password');
      return;
    }

    const passwordErr = validatePassword(newPassword);
    if (passwordErr) {
      setPasswordError(passwordErr);
      return;
    }

    if (newPassword !== confirmPassword) {
      setPasswordError('New passwords do not match');
      return;
    }

    if (currentPassword === newPassword) {
      setPasswordError('New password must be different from current password');
      return;
    }

    setPasswordLoading(true);

    try {
      await authService.changePassword(currentPassword, newPassword);
      setPasswordSuccess('Password changed successfully!');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
      
      // Clear success message after 3 seconds
      setTimeout(() => {
        setPasswordSuccess('');
      }, 3000);
    } catch (err: any) {
      setPasswordError(
        err.response?.data?.detail || 
        'Failed to change password. Please check your current password and try again.'
      );
    } finally {
      setPasswordLoading(false);
    }
  };

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

          {/* Change Password */}
          <div style={{ backgroundColor: 'white', borderRadius: '0.5rem', padding: '1.5rem', marginBottom: '1.5rem', boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.1)' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem', color: 'rgb(17 24 39)' }}>
              Change Password
            </h2>
            
            {passwordError && (
              <div style={{ backgroundColor: 'rgb(254 242 242)', border: '1px solid rgb(252 165 165)', borderRadius: '0.5rem', padding: '0.75rem', marginBottom: '1rem' }}>
                <p style={{ color: 'rgb(153 27 27)', fontSize: '0.875rem' }}>{passwordError}</p>
              </div>
            )}

            {passwordSuccess && (
              <div style={{ backgroundColor: 'rgb(240 253 244)', border: '1px solid rgb(134 239 172)', borderRadius: '0.5rem', padding: '0.75rem', marginBottom: '1rem' }}>
                <p style={{ color: 'rgb(20 83 45)', fontSize: '0.875rem' }}>{passwordSuccess}</p>
              </div>
            )}

            <form onSubmit={handleChangePassword} style={{ display: 'grid', gap: '1rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '500', color: 'rgb(107 114 128)', marginBottom: '0.5rem' }}>
                  Current Password
                </label>
                <input
                  type="password"
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                  required
                  disabled={passwordLoading}
                  placeholder="••••••••"
                  style={{
                    width: '100%',
                    padding: '0.5rem 0.75rem',
                    border: '1px solid rgb(209 213 219)',
                    borderRadius: '0.375rem',
                    fontSize: '0.875rem',
                  }}
                />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '500', color: 'rgb(107 114 128)', marginBottom: '0.5rem' }}>
                  New Password
                </label>
                <input
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  required
                  disabled={passwordLoading}
                  placeholder="••••••••"
                  style={{
                    width: '100%',
                    padding: '0.5rem 0.75rem',
                    border: '1px solid rgb(209 213 219)',
                    borderRadius: '0.375rem',
                    fontSize: '0.875rem',
                  }}
                />
                <p style={{ color: 'rgb(107 114 128)', fontSize: '0.75rem', marginTop: '0.25rem' }}>
                  At least 8 characters with uppercase, lowercase, and number
                </p>
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '500', color: 'rgb(107 114 128)', marginBottom: '0.5rem' }}>
                  Confirm New Password
                </label>
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  disabled={passwordLoading}
                  placeholder="••••••••"
                  style={{
                    width: '100%',
                    padding: '0.5rem 0.75rem',
                    border: '1px solid rgb(209 213 219)',
                    borderRadius: '0.375rem',
                    fontSize: '0.875rem',
                  }}
                />
              </div>
              <button
                type="submit"
                disabled={passwordLoading || !currentPassword || !newPassword || !confirmPassword}
                style={{
                  padding: '0.5rem 1rem',
                  backgroundColor: passwordLoading || !currentPassword || !newPassword || !confirmPassword ? 'rgb(209 213 219)' : 'rgb(59 130 246)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '0.375rem',
                  fontSize: '0.875rem',
                  fontWeight: '500',
                  cursor: passwordLoading || !currentPassword || !newPassword || !confirmPassword ? 'not-allowed' : 'pointer',
                  transition: 'background-color 0.2s',
                }}
              >
                {passwordLoading ? 'Changing Password...' : 'Change Password'}
              </button>
            </form>
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
