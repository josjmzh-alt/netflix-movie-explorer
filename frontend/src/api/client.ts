// Typed API client — wraps all backend endpoints

import { ApiError } from './errors';
import type { FilterParams, MovieCreate, MovieRead, Stats, Status } from './types';

const BASE = '/api';

function errorMessage(detail: unknown, fallback: string) {
  if (typeof detail === 'string') return detail;
  if (detail && typeof detail === 'object' && 'message' in detail) {
    return String((detail as { message: unknown }).message);
  }
  return fallback;
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new ApiError(errorMessage(err.detail, res.statusText || 'Request failed'), res.status, err.detail);
  }
  return res.json();
}

export const api = {
  getStatus: () => request<Status>('/status'),
  getStats: () => request<Stats>('/stats'),
  searchMovies: (title: string) =>
    request<MovieRead[]>(`/movies/search?title=${encodeURIComponent(title)}`),
  getTopRated: (limit = 10) =>
    request<MovieRead[]>(`/movies/top-rated?limit=${limit}`),
  filterMovies: (params: FilterParams) => {
    const qs = new URLSearchParams();
    if (params.genre) qs.set('genre', params.genre);
    if (params.min_rating !== undefined) qs.set('min_rating', String(params.min_rating));
    if (params.year !== undefined) qs.set('year', String(params.year));
    return request<MovieRead[]>(`/movies?${qs.toString()}`);
  },
  getAuthUrl: () => request<{ url: string }>('/auth/login-url'),
  addMovie: (payload: MovieCreate) =>
    request<MovieRead>('/movies', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
};
