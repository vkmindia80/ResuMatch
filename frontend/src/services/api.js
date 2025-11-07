import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/api/auth/refresh`, {
            refresh_token: refreshToken,
          });
          
          const { access_token, refresh_token: newRefreshToken } = response.data;
          localStorage.setItem('access_token', access_token);
          localStorage.setItem('refresh_token', newRefreshToken);
          
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        } catch (refreshError) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
      }
    }
    
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: (data) => api.post('/api/auth/register', data),
  login: (data) => api.post('/api/auth/login', data),
  getCurrentUser: () => api.get('/api/auth/me'),
};

// Profile API
export const profileAPI = {
  getProfile: () => api.get('/api/profiles/me'),
  createProfile: (data) => api.post('/api/profiles/me', data),
  updateProfile: (data) => api.put('/api/profiles/me', data),
  getCompleteness: () => api.get('/api/profiles/completeness'),
  parseResume: (formData) => {
    return api.post('/api/profiles/parse-resume', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
};

// Job Description API
export const jobAPI = {
  createJob: (data) => api.post('/api/jobs/', data),
  getJobs: () => api.get('/api/jobs/'),
  getJob: (id) => api.get(`/api/jobs/${id}`),
  deleteJob: (id) => api.delete(`/api/jobs/${id}`),
};

// Resume API
export const resumeAPI = {
  generateResume: (data) => api.post('/api/resumes/generate', data),
  getResumes: () => api.get('/api/resumes/'),
  getResume: (id) => api.get(`/api/resumes/${id}`),
  deleteResume: (id) => api.delete(`/api/resumes/${id}`),
  getTemplates: () => api.get('/api/resumes/templates/list'),
};

// Interview API
export const interviewAPI = {
  generateQuestions: (data) => api.post('/api/interviews/generate-questions', data),
  getQuestions: (params) => api.get('/api/interviews/questions', { params }),
  getCategories: () => api.get('/api/interviews/categories'),
};

export default api;
