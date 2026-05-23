import { useNavigate, Link } from "react-router-dom";
import { Button } from "@/presentation/components/ui/button";
import { useCreateProject } from "@/application/hooks/use-projects";
import { ProjectForm } from "./project-form";
import { ArrowLeft } from "lucide-react";

export function CreateProjectPage() {
  const navigate = useNavigate();
  const createMutation = useCreateProject();

  const handleSubmit = (data: { name: string; description?: string; is_archived?: boolean }) => {
    createMutation.mutate(data, {
      onSuccess: (project) => navigate(`/projects/${project.id}`),
    });
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="flex items-center gap-3">
        <Link to="/projects">
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-4 w-4" />
          </Button>
        </Link>
        <h1 className="text-3xl font-bold">Crear Proyecto</h1>
      </div>
      <ProjectForm onSubmit={handleSubmit} isPending={createMutation.isPending} mode="create" />
    </div>
  );
}
