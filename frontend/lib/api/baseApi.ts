import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

const getBaseUrl = () => {
  if (typeof window !== 'undefined') {
    return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  }
  return 'http://localhost:8000';
};

// Base API slice with common configuration
export const baseApi = createApi({
  reducerPath: 'api',
  baseQuery: fetchBaseQuery({
    baseUrl: getBaseUrl(),
    // Attach auth token if present
    prepareHeaders: (headers) => {
      if (typeof window !== 'undefined') {
        const token = localStorage.getItem('access_token');
        if (token && !headers.has('Authorization')) {
          headers.set('Authorization', `Bearer ${token}`);
        }
      }
      return headers;
    },
    // RTK Query automatically sets Content-Type: application/json for plain objects
    // and handles FormData correctly (no Content-Type, browser sets it with boundary)
  }),
  tagTypes: ['Chat', 'Document', 'Question'],
  endpoints: () => ({}), // Endpoints will be injected by other API slices
});

