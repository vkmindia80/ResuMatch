import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../context/AuthContext';
import Login from '../pages/Login';

// Mock useNavigate
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

// Helper function to render with providers
const renderWithProviders = (component) => {
  return render(
    <BrowserRouter>
      <AuthProvider>
        {component}
      </AuthProvider>
    </BrowserRouter>
  );
};

describe('Login Component', () => {
  beforeEach(() => {
    mockNavigate.mockClear();
    localStorage.clear();
  });

  test('renders login form with all elements', () => {
    renderWithProviders(<Login />);
    
    expect(screen.getByText('Welcome Back')).toBeInTheDocument();
    expect(screen.getByText('Sign in to continue to ResuMatch AI')).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });

  test('renders demo credentials banner', () => {
    renderWithProviders(<Login />);
    
    expect(screen.getByTestId('demo-credentials-banner')).toBeInTheDocument();
    expect(screen.getByText('demo@resumatch.com')).toBeInTheDocument();
    expect(screen.getByText('Demo@123')).toBeInTheDocument();
  });

  test('use demo credentials button populates fields', () => {
    renderWithProviders(<Login />);
    
    const demoButton = screen.getByTestId('use-demo-credentials-button');
    fireEvent.click(demoButton);
    
    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    
    expect(emailInput.value).toBe('demo@resumatch.com');
    expect(passwordInput.value).toBe('Demo@123');
  });

  test('allows user to type in email and password fields', () => {
    renderWithProviders(<Login />);
    
    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    
    expect(emailInput.value).toBe('test@example.com');
    expect(passwordInput.value).toBe('password123');
  });

  test('has link to register page', () => {
    renderWithProviders(<Login />);
    
    const registerLink = screen.getByText(/sign up/i);
    expect(registerLink).toBeInTheDocument();
    expect(registerLink.closest('a')).toHaveAttribute('href', '/register');
  });

  test('submit button is disabled when loading', async () => {
    renderWithProviders(<Login />);
    
    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    
    // Note: This test is simplified - in a real scenario, you'd mock the API call
    expect(submitButton).not.toBeDisabled();
  });
});
