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
  suggestAchievements: (data) => api.post('/api/profiles/suggest-achievements', null, { params: data }),
  suggestSkills: (data) => api.post('/api/profiles/suggest-skills', null, { params: data }),
  categorizeSkills: (skills) => api.post('/api/profiles/categorize-skills', null, { params: { skills } }),
  uploadCertificate: (formData) => {
    return api.post('/api/profiles/upload-certificate', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  deleteCertificate: (educationId) => api.delete(`/api/profiles/delete-certificate/${educationId}`),
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

// Cover Letter API
export const coverLetterAPI = {
  generate: (data) => api.post('/api/cover-letters/generate', data),
  getAll: (params) => api.get('/api/cover-letters/', { params }),
  getOne: (id) => api.get(`/api/cover-letters/${id}`),
  update: (id, data) => api.put(`/api/cover-letters/${id}`, data),
  delete: (id) => api.delete(`/api/cover-letters/${id}`),
  getTemplates: () => api.get('/api/cover-letters/templates/list'),
};

// Practice Session API
export const practiceSessionAPI = {
  create: (data) => api.post('/api/practice-sessions/', data),
  getAll: (params) => api.get('/api/practice-sessions/', { params }),
  getOne: (id) => api.get(`/api/practice-sessions/${id}`),
  update: (id, data) => api.put(`/api/practice-sessions/${id}`, data),
  delete: (id) => api.delete(`/api/practice-sessions/${id}`),
  getAnalytics: (days = 30) => api.get('/api/practice-sessions/analytics/summary', { params: { days } }),
};

// Job Match Score API
export const matchScoreAPI = {
  getScore: (jobId) => api.get(`/api/jobs/${jobId}/match-score`),
};

// Admin API
export const adminAPI = {
  getStorageSettings: () => api.get('/api/admin/storage-settings'),
  updateStorageSettings: (data) => api.put('/api/admin/storage-settings', data),
  getStorageConfig: () => api.get('/api/admin/storage-config'),
};

export default api;
