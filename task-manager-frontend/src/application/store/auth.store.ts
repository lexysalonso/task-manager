import { create } from "zustand";

interface AuthState {
  token: string | null;
  user: { id: number; email: string; full_name: string } | null;
  setAuth: (token: string) => void;
  setUser: (user: { id: number; email: string; full_name: string }) => void;
  logout: () => void;
  isAuthenticated: () => boolean;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  token: localStorage.getItem("auth-token"),
  user: (() => {
    try {
      const stored = localStorage.getItem("auth-user");
      return stored ? JSON.parse(stored) : null;
    } catch {
      return null;
    }
  })(),
  setAuth: (token: string) => {
    localStorage.setItem("auth-token", token);
    set({ token });
  },
  setUser: (user) => {
    localStorage.setItem("auth-user", JSON.stringify(user));
    set({ user });
  },
  logout: () => {
    localStorage.removeItem("auth-token");
    localStorage.removeItem("auth-user");
    set({ token: null, user: null });
  },
  isAuthenticated: () => {
    return get().token !== null;
  },
}));
