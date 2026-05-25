import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";
import type { ApiError } from "@/domain/types";
import { STORAGE_TOKEN_KEY } from "@/lib/constants";

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1",
  headers: { "Content-Type": "application/json" },
});

apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem(STORAGE_TOKEN_KEY);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiError>) => {
    if (error.response?.status === 401) {
      localStorage.removeItem(STORAGE_TOKEN_KEY);
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export default apiClient;
