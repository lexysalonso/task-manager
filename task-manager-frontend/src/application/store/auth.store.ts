import { create } from "zustand";
import { STORAGE_TOKEN_KEY, STORAGE_USER_KEY } from "@/lib/constants";
import type { User } from "@/domain/types";

interface AuthState {
  token: string | null;
  user: User | null;
  setAuth: (token: string) => void;
  setUser: (user: User) => void;
  logout: () => void;
  isAuthenticated: () => boolean;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  token: localStorage.getItem(STORAGE_TOKEN_KEY),
  user: (() => {
    try {
      const stored = localStorage.getItem(STORAGE_USER_KEY);
      return stored ? JSON.parse(stored) : null;
    } catch {
      return null;
    }
  })(),
  setAuth: (token: string) => {
    localStorage.setItem(STORAGE_TOKEN_KEY, token);
    set({ token });
  },
  setUser: (user) => {
    localStorage.setItem(STORAGE_USER_KEY, JSON.stringify(user));
    set({ user });
  },
  logout: () => {
    localStorage.removeItem(STORAGE_TOKEN_KEY);
    localStorage.removeItem(STORAGE_USER_KEY);
    set({ token: null, user: null });
  },
  isAuthenticated: () => {
    return get().token !== null;
  },
}));
