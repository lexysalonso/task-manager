import { Outlet } from "react-router-dom";

export function AuthLayout() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-muted/30 px-4">
      <div className="w-full max-w-md">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold">Gestor de Tareas</h1>
          <p className="text-muted-foreground mt-2">Gestiona tus proyectos y tareas</p>
        </div>
        <Outlet />
      </div>
    </div>
  );
}
