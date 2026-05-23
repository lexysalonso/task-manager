import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { authApi } from "@/infrastructure/api/auth.api";
import { useAuthStore } from "@/application/store/auth.store";
import { AxiosError } from "axios";
import type { ApiError } from "@/domain/types";

export function useRegister() {
  const navigate = useNavigate();
  const { setAuth, setUser } = useAuthStore();

  return useMutation({
    mutationFn: authApi.register,
    onSuccess: (data) => {
      setAuth(data.access_token);
      setUser(data.user);
      toast.success("Cuenta creada exitosamente");
      navigate("/projects");
    },
    onError: (error: AxiosError<ApiError>) => {
      toast.error(error.response?.data?.detail || "Error al registrarse");
    },
  });
}

export function useLogin() {
  const navigate = useNavigate();
  const { setAuth, setUser } = useAuthStore();

  return useMutation({
    mutationFn: authApi.login,
    onSuccess: (data) => {
      setAuth(data.access_token);
      setUser(data.user);
      toast.success("Sesión iniciada exitosamente");
      navigate("/projects");
    },
    onError: (error: AxiosError<ApiError>) => {
      toast.error(error.response?.data?.detail || "Error al iniciar sesión");
    },
  });
}

export function useLogout() {
  const { logout } = useAuthStore();
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  return () => {
    logout();
    queryClient.clear();
    navigate("/login");
    toast.success("Sesión cerrada");
  };
}
