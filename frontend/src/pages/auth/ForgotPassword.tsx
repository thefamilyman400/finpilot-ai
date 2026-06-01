import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authService } from '../../services/auth.service';

export default function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      await authService.requestPasswordReset(email);
      setSuccess('Password reset email has been sent. Please check your inbox.');
      setEmail('');
      
      // Redirect to login after 3 seconds
      setTimeout(() => {
        navigate('/login');
      }, 3000);
    } catch (err: any) {
      setError(
        err.response?.data?.detail || 
        'Failed to send reset email. Please check your email and try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: 'rgb(249 250 251)', padding: '1rem' }}>
      <div className="card" style={{ maxWidth: '28rem', width: '100%' }}>
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <h1 style={{ fontSize: '2rem', fontWeight: 'bold', color: 'rgb(17 24 39)', marginBottom: '0.5rem' }}>
            FinPilot AI
          </h1>
          <p style={{ color: 'rgb(107 114 128)' }}>
            Reset your password
          </p>
        </div>

        {error && (
          <div style={{ backgroundColor: 'rgb(254 242 242)', border: '1px solid rgb(252 165 165)', borderRadius: '0.5rem', padding: '0.75rem', marginBottom: '1rem' }}>
            <p style={{ color: 'rgb(153 27 27)', fontSize: '0.875rem' }}>{error}</p>
          </div>
        )}

        {success && (
          <div style={{ backgroundColor: 'rgb(240 253 244)', border: '1px solid rgb(134 239 172)', borderRadius: '0.5rem', padding: '0.75rem', marginBottom: '1rem' }}>
            <p style={{ color: 'rgb(20 83 45)', fontSize: '0.875rem' }}>{success}</p>
          </div>
        )}

        {!success ? (
          <>
            <p style={{ color: 'rgb(107 114 128)', fontSize: '0.875rem', marginBottom: '1rem' }}>
              Enter your email address and we'll send you a link to reset your password.
            </p>

            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label className="label" htmlFor="email">
                  Email Address
                </label>
                <input
                  id="email"
                  type="email"
                  className="input-field"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  disabled={loading}
                  placeholder="you@example.com"
                />
              </div>

              <button
                type="submit"
                className="btn-primary"
                disabled={loading}
                style={{ width: '100%', marginTop: '0.5rem' }}
              >
                {loading ? 'Sending...' : 'Send Reset Link'}
              </button>
            </form>
          </>
        ) : null}

        <div style={{ marginTop: '1.5rem', textAlign: 'center' }}>
          <p style={{ color: 'rgb(107 114 128)', fontSize: '0.875rem' }}>
            Remember your password?{' '}
            <Link 
              to="/login" 
              style={{ color: 'rgb(2 132 199)', fontWeight: '500', textDecoration: 'none' }}
            >
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
