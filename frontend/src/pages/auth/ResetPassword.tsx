import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { authService } from '../../services/auth.service';

export default function ResetPassword() {
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const [validating, setValidating] = useState(true);
  
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');

  useEffect(() => {
    // Validate token exists
    if (!token) {
      setError('Invalid or missing reset token. Please request a new password reset.');
      setValidating(false);
    } else {
      setValidating(false);
    }
  }, [token]);

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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    // Validate password
    const passwordError = validatePassword(password);
    if (passwordError) {
      setError(passwordError);
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setLoading(true);

    try {
      await authService.resetPassword(token!, password);
      setSuccess('Password has been reset successfully. Redirecting to login...');
      
      // Redirect to login after 2 seconds
      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } catch (err: any) {
      setError(
        err.response?.data?.detail || 
        'Failed to reset password. The link may have expired. Please request a new one.'
      );
    } finally {
      setLoading(false);
    }
  };

  if (validating) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: 'rgb(249 250 251)' }}>
        <div className="card" style={{ maxWidth: '28rem', width: '100%' }}>
          <p style={{ textAlign: 'center', color: 'rgb(107 114 128)' }}>Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: 'rgb(249 250 251)', padding: '1rem' }}>
      <div className="card" style={{ maxWidth: '28rem', width: '100%' }}>
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <h1 style={{ fontSize: '2rem', fontWeight: 'bold', color: 'rgb(17 24 39)', marginBottom: '0.5rem' }}>
            FinPilot AI
          </h1>
          <p style={{ color: 'rgb(107 114 128)' }}>
            Create a new password
          </p>
        </div>

        {error && !token && (
          <div style={{ backgroundColor: 'rgb(254 242 242)', border: '1px solid rgb(252 165 165)', borderRadius: '0.5rem', padding: '0.75rem', marginBottom: '1rem' }}>
            <p style={{ color: 'rgb(153 27 27)', fontSize: '0.875rem' }}>{error}</p>
            <Link 
              to="/forgot-password" 
              style={{ color: 'rgb(2 132 199)', fontWeight: '500', textDecoration: 'none', fontSize: '0.875rem', display: 'inline-block', marginTop: '0.5rem' }}
            >
              Request a new reset link
            </Link>
          </div>
        )}

        {error && token && (
          <div style={{ backgroundColor: 'rgb(254 242 242)', border: '1px solid rgb(252 165 165)', borderRadius: '0.5rem', padding: '0.75rem', marginBottom: '1rem' }}>
            <p style={{ color: 'rgb(153 27 27)', fontSize: '0.875rem' }}>{error}</p>
          </div>
        )}

        {success && (
          <div style={{ backgroundColor: 'rgb(240 253 244)', border: '1px solid rgb(134 239 172)', borderRadius: '0.5rem', padding: '0.75rem', marginBottom: '1rem' }}>
            <p style={{ color: 'rgb(20 83 45)', fontSize: '0.875rem' }}>{success}</p>
          </div>
        )}

        {token && !success && (
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div>
              <label className="label" htmlFor="password">
                New Password
              </label>
              <input
                id="password"
                type="password"
                className="input-field"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                disabled={loading}
                placeholder="••••••••"
              />
              <p style={{ color: 'rgb(107 114 128)', fontSize: '0.75rem', marginTop: '0.25rem' }}>
                At least 8 characters with uppercase, lowercase, and number
              </p>
            </div>

            <div>
              <label className="label" htmlFor="confirmPassword">
                Confirm Password
              </label>
              <input
                id="confirmPassword"
                type="password"
                className="input-field"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                disabled={loading}
                placeholder="••••••••"
              />
            </div>

            <button
              type="submit"
              className="btn-primary"
              disabled={loading || !password || !confirmPassword}
              style={{ width: '100%', marginTop: '0.5rem' }}
            >
              {loading ? 'Resetting Password...' : 'Reset Password'}
            </button>
          </form>
        )}

        <div style={{ marginTop: '1.5rem', textAlign: 'center' }}>
          <p style={{ color: 'rgb(107 114 128)', fontSize: '0.875rem' }}>
            <Link 
              to="/login" 
              style={{ color: 'rgb(2 132 199)', fontWeight: '500', textDecoration: 'none' }}
            >
              Back to sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
