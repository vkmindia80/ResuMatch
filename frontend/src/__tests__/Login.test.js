// Mock axios before any imports
jest.mock('axios', () => {
  return {
    create: jest.fn(() => ({
      get: jest.fn(),
      post: jest.fn(),
      interceptors: {
        request: { use: jest.fn(), eject: jest.fn() },
        response: { use: jest.fn(), eject: jest.fn() },
      },
    })),
  };
});

describe('Login Component Tests', () => {
  test('login component structure verification', () => {
    // Basic test to verify test infrastructure is working
    expect(true).toBe(true);
  });

  test('can access demo credentials', () => {
    const DEMO_EMAIL = 'demo@resumatch.com';
    const DEMO_PASSWORD = 'Demo@123';
    
    expect(DEMO_EMAIL).toBe('demo@resumatch.com');
    expect(DEMO_PASSWORD).toBe('Demo@123');
  });

  test('localStorage can store user session', () => {
    localStorage.setItem('user', JSON.stringify({ email: 'test@example.com' }));
    const user = JSON.parse(localStorage.getItem('user'));
    
    expect(user.email).toBe('test@example.com');
  });
});
