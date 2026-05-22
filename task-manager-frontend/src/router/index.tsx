import { createBrowserRouter, Navigate } from "react-router-dom";
import { ProtectedRoute } from "@/presentation/components/common/ProtectedRoute";
import { PublicRoute } from "@/presentation/components/common/PublicRoute";
import { ErrorBoundary } from "@/presentation/components/common/ErrorBoundary";
import { AuthLayout } from "@/presentation/layouts/AuthLayout";
import { AppLayout } from "@/presentation/layouts/AppLayout";
import { LoginPage } from "@/presentation/features/auth/LoginPage";
import { RegisterPage } from "@/presentation/features/auth/RegisterPage";
import { ProjectList } from "@/presentation/features/projects/ProjectList";
import { CreateProjectPage } from "@/presentation/features/projects/CreateProjectPage";
import { EditProjectPage } from "@/presentation/features/projects/EditProjectPage";
import { ProjectDetail } from "@/presentation/features/projects/ProjectDetail";

export const router = createBrowserRouter([
  {
    element: <PublicRoute />,
    errorElement: <ErrorBoundary />,
    children: [
      {
        element: <AuthLayout />,
        children: [
          { path: "/login", element: <LoginPage /> },
          { path: "/register", element: <RegisterPage /> },
        ],
      },
    ],
  },
  {
    element: <ProtectedRoute />,
    errorElement: <ErrorBoundary />,
    children: [
      {
        element: <AppLayout />,
        children: [
          { index: true, element: <Navigate to="/projects" replace /> },
          { path: "/projects", element: <ProjectList /> },
          { path: "/projects/new", element: <CreateProjectPage /> },
          { path: "/projects/:id", element: <ProjectDetail /> },
          { path: "/projects/:id/edit", element: <EditProjectPage /> },
        ],
      },
    ],
  },
  {
    path: "*",
    element: <Navigate to="/projects" replace />,
  },
]);
