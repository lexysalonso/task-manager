import { Link } from "react-router-dom";
import { Button } from "@/presentation/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/presentation/components/ui/card";
import { Badge } from "@/presentation/components/ui/badge";
import { Skeleton } from "@/presentation/components/ui/skeleton";
import { useProjects } from "@/application/hooks/use-projects";
import { useAuthStore } from "@/application/store/auth.store";
import { Plus, Users, Archive } from "lucide-react";

export function ProjectList() {
  const { data, isLoading, isError } = useProjects();
  const userId = useAuthStore((s) => s.user?.id);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <Skeleton className="h-8 w-48" />
          <Skeleton className="h-10 w-36" />
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <Card key={i}>
              <CardHeader>
                <Skeleton className="h-5 w-3/4" />
                <Skeleton className="h-4 w-full mt-2" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-4 w-1/2" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="text-center py-12">
        <p className="text-destructive text-lg">Error al cargar proyectos</p>
        <p className="text-muted-foreground mt-2">Intenta de nuevo más tarde</p>
      </div>
    );
  }

  const projects = data?.projects || [];

  if (projects.length === 0) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold">Mis Proyectos</h1>
          <Link to="/projects/new">
            <Button>
              <Plus className="mr-2 h-4 w-4" /> Nuevo Proyecto
            </Button>
          </Link>
        </div>
        <Card className="py-12">
          <CardContent className="flex flex-col items-center gap-4 text-center">
            <div className="rounded-full bg-muted p-4">
              <Users className="h-8 w-8 text-muted-foreground" />
            </div>
            <h3 className="text-xl font-semibold">Sin proyectos aún</h3>
            <p className="text-muted-foreground max-w-sm">
              Crea tu primer proyecto para empezar a gestionar tareas con tu equipo.
            </p>
            <Link to="/projects/new">
              <Button>
                <Plus className="mr-2 h-4 w-4" /> Crear Proyecto
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Mis Proyectos</h1>
        <Link to="/projects/new">
          <Button>
            <Plus className="mr-2 h-4 w-4" /> Nuevo Proyecto
          </Button>
        </Link>
      </div>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {projects.map((project) => (
          <Link key={project.id} to={`/projects/${project.id}`}>
            <Card className="h-full transition-colors hover:bg-accent/50 cursor-pointer">
              <CardHeader>
                <div className="flex items-start justify-between gap-2">
                  <CardTitle className="text-lg">{project.name}</CardTitle>
                  {project.is_archived && (
                    <Badge variant="outline" className="shrink-0">
                      <Archive className="mr-1 h-3 w-3" /> Archivado
                    </Badge>
                  )}
                </div>
                {project.description && (
                  <CardDescription className="line-clamp-2">
                    {project.description}
                  </CardDescription>
                )}
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-4 text-sm text-muted-foreground">
                  <span className="flex items-center gap-1">
                    <Users className="h-4 w-4" />
                    {project.member_count} {project.member_count === 1 ? "miembro" : "miembros"}
                  </span>
                  {project.owner_id === userId && (
                    <Badge variant="secondary">Propietario</Badge>
                  )}
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
