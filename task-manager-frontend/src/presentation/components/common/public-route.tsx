import { Navigate, Outlet } from "react-router-dom";
import { useAuthStore } from "@/application/store/auth.store";

export function PublicRoute() {
  const token = useAuthStore((s) => s.token);
  if (token) {
    return <Navigate to="/projects" replace />;
  }
  return <Outlet />;
}
