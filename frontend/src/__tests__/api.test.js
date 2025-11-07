describe('API Service', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  test('localStorage is accessible', () => {
    localStorage.setItem('test_key', 'test_value');
    expect(localStorage.getItem('test_key')).toBe('test_value');
    
    localStorage.removeItem('test_key');
    expect(localStorage.getItem('test_key')).toBeNull();
  });

  test('can store and retrieve access token', () => {
    const mockToken = 'test-access-token';
    localStorage.setItem('access_token', mockToken);
    
    const token = localStorage.getItem('access_token');
    expect(token).toBe(mockToken);
  });

  test('can store and retrieve refresh token', () => {
    const mockRefreshToken = 'test-refresh-token';
    localStorage.setItem('refresh_token', mockRefreshToken);
    
    const token = localStorage.getItem('refresh_token');
    expect(token).toBe(mockRefreshToken);
  });

  test('can clear all localStorage items', () => {
    localStorage.setItem('key1', 'value1');
    localStorage.setItem('key2', 'value2');
    
    localStorage.clear();
    
    expect(localStorage.getItem('key1')).toBeNull();
    expect(localStorage.getItem('key2')).toBeNull();
  });

  test('can remove specific items', () => {
    localStorage.setItem('access_token', 'token1');
    localStorage.setItem('refresh_token', 'token2');
    
    localStorage.removeItem('access_token');
    
    expect(localStorage.getItem('access_token')).toBeNull();
    expect(localStorage.getItem('refresh_token')).toBe('token2');
  });
});
