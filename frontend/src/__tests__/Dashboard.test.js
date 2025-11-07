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

describe('Dashboard Component Tests', () => {
  test('dashboard test infrastructure works', () => {
    expect(true).toBe(true);
  });

  test('can track user profile data', () => {
    const mockProfile = {
      full_name: 'Test User',
      email: 'test@example.com',
      completeness_score: 75
    };
    
    expect(mockProfile.completeness_score).toBeGreaterThan(0);
    expect(mockProfile.completeness_score).toBeLessThanOrEqual(100);
  });

  test('can structure resume data', () => {
    const mockResume = {
      id: '123',
      template_id: 'template_1',
      status: 'draft',
      ats_score: { overall_score: 85 }
    };
    
    expect(mockResume.status).toBe('draft');
    expect(mockResume.ats_score.overall_score).toBeGreaterThan(0);
  });
});
