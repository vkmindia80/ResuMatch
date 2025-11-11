import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Mail, Lock, AlertCircle, Play, Database, CheckCircle } from 'lucide-react';
import axios from 'axios';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [generatingData, setGeneratingData] = useState(false);
  const [dataGenerated, setDataGenerated] = useState(false);
  const [generationResult, setGenerationResult] = useState(null);
  const { login } = useAuth();
  const navigate = useNavigate();

  // Demo credentials
  const DEMO_EMAIL = 'demo@resumatch.com';
  const DEMO_PASSWORD = 'Demo@123';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const result = await login(email, password);
    
    if (result.success) {
      navigate('/dashboard');
    } else {
      setError(result.error);
    }
    
    setLoading(false);
  };

  const useDemoCredentials = () => {
    setEmail(DEMO_EMAIL);
    setPassword(DEMO_PASSWORD);
    setError('');
  };

  const generateSampleData = async () => {
    setGeneratingData(true);
    setError('');
    setDataGenerated(false);
    
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
      const response = await axios.post(`${backendUrl}/api/admin/generate-sample-data`, {
        target_user_email: DEMO_EMAIL
      });
      
      if (response.data.success) {
        setDataGenerated(true);
        setGenerationResult(response.data.created);
        // Auto-fill demo credentials
        setEmail(DEMO_EMAIL);
        setPassword(DEMO_PASSWORD);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate sample data. Please try again.');
    } finally {
      setGeneratingData(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-secondary-50 px-4">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-secondary-900 mb-2">Welcome Back</h1>
          <p className="text-secondary-600">Sign in to continue to ResuMatch AI</p>
        </div>

        {/* Demo Credentials Banner */}
        <div className="mb-6 bg-gradient-to-r from-blue-50 to-indigo-50 border-2 border-blue-200 rounded-lg p-4 shadow-sm" data-testid="demo-credentials-banner">
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0">
              <Play className="h-6 w-6 text-blue-600 mt-0.5" />
            </div>
            <div className="flex-1">
              <h3 className="text-sm font-semibold text-blue-900 mb-2">🎯 Quick Demo Access</h3>
              <div className="text-sm text-blue-800 space-y-1">
                <p><span className="font-medium">Email:</span> <code className="bg-blue-100 px-2 py-0.5 rounded text-xs">{DEMO_EMAIL}</code></p>
                <p><span className="font-medium">Password:</span> <code className="bg-blue-100 px-2 py-0.5 rounded text-xs">{DEMO_PASSWORD}</code></p>
              </div>
              <button
                type="button"
                onClick={useDemoCredentials}
                data-testid="use-demo-credentials-button"
                className="mt-3 w-full bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium py-2 px-4 rounded-lg transition-colors duration-200 flex items-center justify-center space-x-2"
              >
                <Play size={16} />
                <span>Use Demo Credentials</span>
              </button>
            </div>
          </div>
        </div>

        {/* Generate Sample Data Section */}
        <div className="mb-6 bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-200 rounded-lg p-4 shadow-sm" data-testid="sample-data-section">
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0">
              <Database className="h-6 w-6 text-green-600 mt-0.5" />
            </div>
            <div className="flex-1">
              <h3 className="text-sm font-semibold text-green-900 mb-2">🚀 Generate Sample Data</h3>
              <p className="text-sm text-green-800 mb-3">
                Populate the demo account with sample profiles, resumes, job descriptions, interview prep data, and live interview sessions across diverse roles.
              </p>
              
              {dataGenerated && generationResult && (
                <div className="mb-3 bg-green-100 border border-green-300 rounded-lg p-3 text-xs text-green-900" data-testid="generation-success">
                  <div className="flex items-center space-x-2 mb-2">
                    <CheckCircle size={16} className="text-green-600" />
                    <span className="font-semibold">Sample Data Generated Successfully!</span>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div>✓ Profiles: {generationResult.profiles}</div>
                    <div>✓ Jobs: {generationResult.job_descriptions}</div>
                    <div>✓ Resumes: {generationResult.resumes}</div>
                    <div>✓ Questions: {generationResult.interview_questions}</div>
                    <div>✓ Cover Letters: {generationResult.cover_letters}</div>
                    <div>✓ Practice: {generationResult.practice_sessions}</div>
                    <div className="col-span-2">✓ Live Sessions: {generationResult.live_interview_sessions}</div>
                  </div>
                </div>
              )}
              
              <button
                type="button"
                onClick={generateSampleData}
                disabled={generatingData}
                data-testid="generate-sample-data-button"
                className="w-full bg-green-600 hover:bg-green-700 disabled:bg-green-400 disabled:cursor-not-allowed text-white text-sm font-medium py-2 px-4 rounded-lg transition-colors duration-200 flex items-center justify-center space-x-2"
              >
                <Database size={16} />
                <span>{generatingData ? 'Generating Sample Data...' : 'Generate Sample Data'}</span>
              </button>
            </div>
          </div>
        </div>

        <div className="card">
          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center space-x-2">
                <AlertCircle size={20} />
                <span>{error}</span>
              </div>
            )}

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-secondary-700 mb-2">
                Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-secondary-400" size={20} />
                <input
                  type="email"
                  id="email"
                  data-testid="email-input"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="input-field pl-10"
                  placeholder="you@example.com"
                  required
                />
              </div>
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-secondary-700 mb-2">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-secondary-400" size={20} />
                <input
                  type="password"
                  id="password"
                  data-testid="password-input"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="input-field pl-10"
                  placeholder="••••••••"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              data-testid="login-submit-button"
              disabled={loading}
              className="w-full btn-primary py-3 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-secondary-600">
              Don't have an account?{' '}
              <Link to="/register" className="text-primary-600 hover:text-primary-700 font-medium">
                Sign up
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
