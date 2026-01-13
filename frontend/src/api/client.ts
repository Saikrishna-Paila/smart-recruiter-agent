import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Jobs API
export const jobsApi = {
  list: (status?: string) => api.get('/jobs', { params: { status } }),
  get: (id: string) => api.get(`/jobs/${id}`),
  create: (data: any) => api.post('/jobs', data),
  update: (id: string, data: any) => api.put(`/jobs/${id}`, data),
  updateStatus: (id: string, status: string) => api.patch(`/jobs/${id}/status`, { status }),
  delete: (id: string) => api.delete(`/jobs/${id}`),
  publish: (id: string) => api.post(`/jobs/${id}/publish`),
  stats: (id: string) => api.get(`/jobs/${id}/stats`),
};

// Candidates API
export const candidatesApi = {
  listForJob: (jobId: string, params?: { status?: string; min_score?: number }) =>
    api.get(`/candidates/job/${jobId}`, { params }),
  get: (id: string) => api.get(`/candidates/${id}`),
  update: (id: string, data: any) => api.put(`/candidates/${id}`, data),
  updateStatus: (id: string, status: string) => api.patch(`/candidates/${id}/status`, { status }),
  shortlist: (id: string) => api.post(`/candidates/${id}/shortlist`),
  reject: (id: string) => api.post(`/candidates/${id}/reject`),
  sendAssessment: (id: string) => api.post(`/candidates/${id}/send-assessment`),
  sendInterviewInvite: (id: string, data?: { interview_date?: string; interview_link?: string }) =>
    api.post(`/candidates/${id}/send-interview-invite`, null, { params: data }),
  rescreen: (id: string) => api.post(`/screening/candidate/${id}/rescreen`),
};

// Application API (Public)
export const applyApi = {
  getJob: (jobId: string) => api.get(`/apply/${jobId}`),
  submit: (jobId: string, formData: FormData) =>
    api.post(`/apply/${jobId}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  checkStatus: (jobId: string, email: string) =>
    api.get(`/apply/${jobId}/check/${email}`),
};

// Screening API
export const screeningApi = {
  screen: (jobId: string) => api.post(`/screening/job/${jobId}/screen`),
  screenJob: (jobId: string) => api.post(`/screening/job/${jobId}/screen`),
  optimizeJD: (jobId: string) => api.post(`/screening/job/${jobId}/optimize-jd`),
  generateQuestions: (candidateId: string) =>
    api.post(`/screening/candidate/${candidateId}/generate-questions`),
  results: (jobId: string) => api.get(`/screening/job/${jobId}/results`),
};
