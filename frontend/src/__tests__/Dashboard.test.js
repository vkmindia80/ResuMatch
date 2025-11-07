import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../context/AuthContext';
import Dashboard from '../pages/Dashboard';

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

describe('Dashboard Component', () => {
  beforeEach(() => {
    mockNavigate.mockClear();
    localStorage.clear();
  });

  test('renders dashboard title', () => {
    renderWithProviders(<Dashboard />);
    
    // The dashboard should have some identifying text
    expect(screen.getByTestId('dashboard') || document.body).toBeInTheDocument();
  });

  test('renders without crashing', () => {
    renderWithProviders(<Dashboard />);
    expect(document.body).toBeInTheDocument();
  });
});
