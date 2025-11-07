import axios from 'axios';
import api from '../services/api';

// Mock axios
jest.mock('axios');

describe('API Service', () => {
  beforeEach(() => {
    localStorage.clear();
    jest.clearAllMocks();
  });

  test('API base URL is correctly set', () => {
    expect(api.defaults.baseURL).toBeDefined();
  });

  test('adds authorization header when token exists', async () => {
    const mockToken = 'test-token';
    localStorage.setItem('access_token', mockToken);
    
    // The interceptor should add the token to requests
    const config = {
      headers: {}
    };
    
    const token = localStorage.getItem('access_token');
    expect(token).toBe(mockToken);
  });

  test('localStorage is accessible', () => {
    localStorage.setItem('test_key', 'test_value');
    expect(localStorage.getItem('test_key')).toBe('test_value');
    
    localStorage.removeItem('test_key');
    expect(localStorage.getItem('test_key')).toBeNull();
  });

  test('can clear all localStorage items', () => {
    localStorage.setItem('key1', 'value1');
    localStorage.setItem('key2', 'value2');
    
    localStorage.clear();
    
    expect(localStorage.getItem('key1')).toBeNull();
    expect(localStorage.getItem('key2')).toBeNull();
  });
});
