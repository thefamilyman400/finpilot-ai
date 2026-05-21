import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authService } from '../../services/auth.service';

export default function Register() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    full_name: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }

    setLoading(true);

    try {
      await authService.register({
        email: formData.email,
        password: formData.password,
        full_name: formData.full_name,
      });
      
      // Redirect to login after successful registration
      navigate('/login', { 
        state: { message: 'Registration successful! Please log in.' } 
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed. Please try again.');
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
            Create your account
          </p>
        </div>

        {error && (
          <div style={{ backgroundColor: 'rgb(254 242 242)', border: '1px solid rgb(252 165 165)', borderRadius: '0.5rem', padding: '0.75rem', marginBottom: '1rem' }}>
            <p style={{ color: 'rgb(153 27 27)', fontSize: '0.875rem' }}>{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div>
            <label className="label" htmlFor="full_name">
              Full Name
            </label>
            <input
              id="full_name"
              name="full_name"
              type="text"
              className="input-field"
              value={formData.full_name}
              onChange={handleChange}
              required
              disabled={loading}
              placeholder="John Doe"
            />
          </div>

          <div>
            <label className="label" htmlFor="email">
              Email
            </label>
            <input
              id="email"
              name="email"
              type="email"
              className="input-field"
              value={formData.email}
              onChange={handleChange}
              required
              disabled={loading}
              placeholder="you@example.com"
            />
          </div>

          <div>
            <label className="label" htmlFor="password">
              Password
            </label>
            <input
              id="password"
              name="password"
              type="password"
              className="input-field"
              value={formData.password}
              onChange={handleChange}
              required
              disabled={loading}
              placeholder="••••••••"
              minLength={8}
            />
            <p style={{ marginTop: '0.25rem', fontSize: '0.75rem', color: 'rgb(107 114 128)' }}>
              Must be at least 8 characters
            </p>
          </div>

          <div>
            <label className="label" htmlFor="confirmPassword">
              Confirm Password
            </label>
            <input
              id="confirmPassword"
              name="confirmPassword"
              type="password"
              className="input-field"
              value={formData.confirmPassword}
              onChange={handleChange}
              required
              disabled={loading}
              placeholder="••••••••"
            />
          </div>

          <button
            type="submit"
            className="btn-primary"
            disabled={loading}
            style={{ width: '100%', marginTop: '0.5rem' }}
          >
            {loading ? 'Creating account...' : 'Create account'}
          </button>
        </form>

        <div style={{ marginTop: '1.5rem', textAlign: 'center' }}>
          <p style={{ color: 'rgb(107 114 128)', fontSize: '0.875rem' }}>
            Already have an account?{' '}
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

// Made with Bob
