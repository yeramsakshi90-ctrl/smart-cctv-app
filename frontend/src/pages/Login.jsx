import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  // Log component mount
  console.log('Login component rendered');
  console.log('Current email state:', email);
  console.log('Current password length:', password.length);

  const handleSubmit = async (e) => {
    // Log immediately - before anything else
    console.log('=== FORM SUBMIT EVENT FIRED ===');
    console.log('Event type:', e.type);
    console.log('Email value:', email);
    console.log('Password length:', password.length);
    
    e.preventDefault();
    e.stopPropagation();
    
    console.log('=== LOGIN FORM SUBMITTED ===');
    console.log('Email:', email);
    console.log('Password length:', password.length);
    console.log('Email type:', typeof email);
    console.log('Email length:', email?.length);
    
    // Validate inputs before proceeding
    if (!email || !password) {
      console.error('Validation failed - missing email or password');
      setError('Email and password are required');
      return;
    }
    
    if (email.trim() === '' || password.trim() === '') {
      console.error('Validation failed - empty email or password');
      setError('Email and password cannot be empty');
      return;
    }
    
    setError('');
    setLoading(true);
    console.log('Loading state set to true');

    try {
      console.log('Step 1: Calling login function from AuthContext...');
      const result = await login(email, password);
      console.log('Step 2: Login result received:', result);
      console.log('Step 3: Result success?', result.success);
      
      setLoading(false);

      if (result && result.success) {
        console.log('Step 4: Login successful, checking token storage...');
        // Wait a moment to ensure token is stored
        await new Promise(resolve => setTimeout(resolve, 200));
        
        // Check if token was stored
        const token = localStorage.getItem('token');
        const user = localStorage.getItem('user');
        console.log('Step 5: Token check -', token ? 'FOUND' : 'NOT FOUND');
        console.log('Step 6: User check -', user ? 'FOUND' : 'NOT FOUND');
        
        if (token) {
          console.log('Step 7: Token verified, navigating to dashboard...');
          console.log('Token preview:', token.substring(0, 30) + '...');
          // Force a small delay to ensure state updates
          setTimeout(() => {
            navigate('/dashboard', { replace: true });
          }, 100);
        } else {
          console.error('Step 7 ERROR: Token not found after successful login!');
          console.error('LocalStorage contents:', {
            token: localStorage.getItem('token'),
            user: localStorage.getItem('user'),
            allKeys: Object.keys(localStorage),
          });
          setError('Login succeeded but token not stored. Please check console for details.');
        }
      } else {
        console.error('Step 4 ERROR: Login failed');
        console.error('Result:', result);
        const errorMsg = result?.error || 'Login failed - no error message provided';
        console.error('Error message:', errorMsg);
        setError(errorMsg);
      }
    } catch (error) {
      console.error('=== LOGIN EXCEPTION CAUGHT ===');
      console.error('Error type:', error.constructor.name);
      console.error('Error message:', error.message);
      console.error('Error stack:', error.stack);
      console.error('Error response:', error.response);
      console.error('Error response data:', error.response?.data);
      console.error('Error response status:', error.response?.status);
      setLoading(false);
      
      const errorMsg = error.response?.data?.error || 
                      error.response?.data?.message || 
                      error.message || 
                      'Login failed - check console for details';
      console.error('Setting error message:', errorMsg);
      setError(errorMsg);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Sign in to Smart CCTV
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Or{' '}
            <Link to="/register" className="font-medium text-primary-600 hover:text-primary-500">
              create a new account
            </Link>
          </p>
        </div>
        <form 
          className="mt-8 space-y-6" 
          onSubmit={(e) => {
            console.log('FORM onSubmit handler called');
            handleSubmit(e);
          }}
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              console.log('Enter key pressed in form');
            }
          }}
        >
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}
          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <label htmlFor="email" className="sr-only">
                Email address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm"
                placeholder="Email address"
                value={email}
                onChange={(e) => {
                  console.log('Email input changed:', e.target.value);
                  setEmail(e.target.value);
                }}
                onBlur={(e) => {
                  console.log('Email input blurred, value:', e.target.value);
                }}
              />
            </div>
            <div>
              <label htmlFor="password" className="sr-only">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm"
                placeholder="Password"
                value={password}
                onChange={(e) => {
                  console.log('Password input changed, length:', e.target.value.length);
                  setPassword(e.target.value);
                }}
                onBlur={(e) => {
                  console.log('Password input blurred, length:', e.target.value.length);
                }}
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              onClick={(e) => {
                console.log('BUTTON CLICKED');
                console.log('Button disabled?', loading);
                console.log('Email:', email);
                console.log('Password length:', password.length);
                // Don't prevent default - let form handle it
              }}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
            >
              {loading ? 'Signing in...' : 'Sign in'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Login;

