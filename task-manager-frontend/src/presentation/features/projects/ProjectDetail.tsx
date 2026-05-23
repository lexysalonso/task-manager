import { useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { Button } from "@/presentation/components/ui/button";
import { Badge } from "@/presentation/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/presentation/components/ui/tabs";
import { Skeleton } from "@/presentation/components/ui/skeleton";
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from "@/presentation/components/ui/alert-dialog";
import { useAuthStore } from "@/application/store/auth.store";
import { useProject, useDeleteProject, useUpdateProject } from "@/application/hooks/useProjects";
import { TaskList } from "@/presentation/features/tasks/TaskList";
import { MemberList } from "@/presentation/features/members/MemberList";
import { Edit, Trash2, Archive, ArrowLeft } from "lucide-react";

export function ProjectDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const projectId = Number(id);
  const userId = useAuthStore((s) => s.user?.id);
  const { data: project, isLoading, isError } = useProject(projectId);
  const deleteMutation = useDeleteProject(projectId);
  const updateMutation = useUpdateProject(projectId);
  const [activeTab, setActiveTab] = useState("tasks");
  const [archiveOpen, setArchiveOpen] = useState(false);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-4 w-96" />
        <Skeleton className="h-96 w-full" />
      </div>
    );
  }

  if (isError || !project) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold">Proyecto no encontrado</h2>
        <p className="text-muted-foreground mt-2">Este proyecto no existe o no tienes acceso.</p>
        <Link to="/projects" className="mt-4 inline-block">
          <Button variant="outline">
            <ArrowLeft className="mr-2 h-4 w-4" /> Volver a Proyectos
          </Button>
        </Link>
      </div>
    );
  }

  const isOwner = project.owner_id === userId;

  const handleDelete = () => {
    deleteMutation.mutate(undefined, {
      onSuccess: () => navigate("/projects"),
    });
  };

  const handleArchiveToggle = () => {
    updateMutation.mutate({ is_archived: !project.is_archived }, {
      onSuccess: () => setArchiveOpen(false),
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link to="/projects">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="h-4 w-4" />
            </Button>
          </Link>
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-3xl font-bold">{project.name}</h1>
              {project.is_archived && <Badge variant="outline">Archivado</Badge>}
              {isOwner && <Badge>Propietario</Badge>}
            </div>
            {project.description && (
              <p className="text-muted-foreground mt-1">{project.description}</p>
            )}
          </div>
        </div>
        {isOwner && (
          <div className="flex gap-2">
            <Link to={`/projects/${project.id}/edit`}>
              <Button variant="outline" size="sm">
                <Edit className="mr-2 h-4 w-4" /> Editar
              </Button>
            </Link>
            <AlertDialog open={archiveOpen} onOpenChange={setArchiveOpen}>
              <AlertDialogTrigger asChild>
                <Button variant="outline" size="sm">
                  <Archive className="mr-2 h-4 w-4" />
                  {project.is_archived ? "Desarchivar" : "Archivar"}
                </Button>
              </AlertDialogTrigger>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>
                    {project.is_archived ? "¿Desarchivar proyecto?" : "¿Archivar proyecto?"}
                  </AlertDialogTitle>
                  <AlertDialogDescription>
                    {project.is_archived
                      ? `"${project.name}" volverá a estar activo. Los miembros podrán crear y editar tareas nuevamente.`
                      : `"${project.name}" pasará a ser solo lectura. Los miembros no podrán crear, editar ni eliminar tareas. Puedes desarchivarlo en cualquier momento.`
                    }
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>Cancelar</AlertDialogCancel>
                  <AlertDialogAction onClick={handleArchiveToggle}>
                    {updateMutation.isPending ? "Guardando..." : project.is_archived ? "Desarchivar" : "Archivar"}
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
            <AlertDialog>
              <AlertDialogTrigger asChild>
                <Button variant="destructive" size="sm">
                  <Trash2 className="mr-2 h-4 w-4" /> Eliminar
                </Button>
              </AlertDialogTrigger>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>¿Eliminar proyecto?</AlertDialogTitle>
                  <AlertDialogDescription>
                    Esto eliminará permanentemente &quot;{project.name}&quot; y todas sus tareas. Esta acción no se puede deshacer.
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>Cancelar</AlertDialogCancel>
                  <AlertDialogAction onClick={handleDelete} className="bg-destructive text-destructive-foreground">
                    {deleteMutation.isPending ? "Eliminando..." : "Eliminar"}
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          </div>
        )}
      </div>

      {project.is_archived && (
        <div className="bg-muted p-4 rounded-lg flex items-center gap-2 text-muted-foreground">
          <Archive className="h-5 w-5" />
          <p className="text-sm">Este proyecto está archivado. Las tareas son solo de lectura.</p>
        </div>
      )}

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="tasks">Tareas</TabsTrigger>
          <TabsTrigger value="members">Miembros ({project.member_count})</TabsTrigger>
        </TabsList>
        <TabsContent value="tasks" className="mt-4">
          <TaskList projectId={projectId} isOwner={isOwner} isArchived={project.is_archived} />
        </TabsContent>
        <TabsContent value="members" className="mt-4">
          <MemberList projectId={projectId} isOwner={isOwner} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
