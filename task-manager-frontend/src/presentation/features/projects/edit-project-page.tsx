import { useParams, useNavigate, Link, Navigate } from "react-router-dom";
import { Button } from "@/presentation/components/ui/button";
import { Skeleton } from "@/presentation/components/ui/skeleton";
import { useProject, useUpdateProject } from "@/application/hooks/use-projects";
import { useAuthStore } from "@/application/store/auth.store";
import { ProjectForm } from "./project-form";
import { ArrowLeft } from "lucide-react";

export function EditProjectPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const projectId = Number(id);
  const userId = useAuthStore((s) => s.user?.id);
  const { data: project, isLoading } = useProject(projectId);
  const updateMutation = useUpdateProject(projectId);

  if (isLoading) {
    return (
      <div className="max-w-2xl mx-auto space-y-6">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-96" />
      </div>
    );
  }

  if (!project) {
    return <Navigate to="/projects" replace />;
  }

  if (project.owner_id !== userId) {
    return <Navigate to={`/projects/${projectId}`} replace />;
  }

  const handleSubmit = (data: { name: string; description?: string; is_archived?: boolean }) => {
    updateMutation.mutate(data, {
      onSuccess: () => navigate(`/projects/${projectId}`),
    });
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="flex items-center gap-3">
        <Link to={`/projects/${projectId}`}>
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-4 w-4" />
          </Button>
        </Link>
        <h1 className="text-3xl font-bold">Editar Proyecto</h1>
      </div>
      <ProjectForm
        defaultValues={{ name: project.name, description: project.description, is_archived: project.is_archived }}
        onSubmit={handleSubmit}
        isPending={updateMutation.isPending}
        mode="edit"
      />
    </div>
  );
}
