const API_BASE_URL = import.meta.env.VITE_BACKEND_HOST || 'http://localhost:8000';
const API_VERSION = '/api/v1';

export const url_params = {
  api: {
    base: `${API_BASE_URL}${API_VERSION}`,
    endpoints: {
      transcribe: `${API_BASE_URL}${API_VERSION}/transcribe`,
      transcriptions: `${API_BASE_URL}${API_VERSION}/transcriptions`,
      search: `${API_BASE_URL}${API_VERSION}/search`,
    },
  },
} as const;