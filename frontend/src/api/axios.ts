import axios from 'axios';
import { url_params } from '../config';

const api = axios.create({
  baseURL: url_params.api.base,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;