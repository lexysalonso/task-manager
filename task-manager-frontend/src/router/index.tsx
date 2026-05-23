import { createBrowserRouter, Navigate } from "react-router-dom";
import { ProtectedRoute } from "@/presentation/components/common/protected-route";
import { PublicRoute } from "@/presentation/components/common/public-route";
import { ErrorBoundary } from "@/presentation/components/common/error-boundary";
import { AuthLayout } from "@/presentation/layouts/auth-layout";
import { AppLayout } from "@/presentation/layouts/app-layout";
import { LoginPage } from "@/presentation/features/auth/login-page";
import { RegisterPage } from "@/presentation/features/auth/register-page";
import { ProjectList } from "@/presentation/features/projects/project-list";
import { CreateProjectPage } from "@/presentation/features/projects/create-project-page";
import { EditProjectPage } from "@/presentation/features/projects/edit-project-page";
import { ProjectDetail } from "@/presentation/features/projects/project-detail";

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
