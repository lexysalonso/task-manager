import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/presentation/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogTrigger,
} from "@/presentation/components/ui/dialog";
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from "@/presentation/components/ui/alert-dialog";
import { Skeleton } from "@/presentation/components/ui/skeleton";
import { Badge } from "@/presentation/components/ui/badge";
import { useFilteredTasks, useCreateTask, useUpdateTask, useDeleteTask, useChangeTaskStatus, useChangeTaskPriority } from "@/application/hooks/use-tasks";
import { useAuthStore } from "@/application/store/auth.store";
import { membersApi } from "@/infrastructure/api/members.api";
import { TaskStatusBadge } from "./task-status-badge";
import { TaskPriorityBadge } from "./task-priority-badge";
import { TaskForm } from "./task-form";
import { TaskStatus, TaskPriority, type Task } from "@/domain/types";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/presentation/components/ui/select";
import { Plus, Trash2, Edit, ClipboardList } from "lucide-react";
import { statusLabels, priorityLabels } from "@/lib/constants";

interface TaskListProps {
  projectId: number;
  isOwner: boolean;
  isArchived: boolean;
}

export function TaskList({ projectId, isOwner, isArchived }: TaskListProps) {
  const userId = useAuthStore((s) => s.user?.id);
  const [statusFilter, setStatusFilter] = useState<TaskStatus | "all">("all");
  const [priorityFilter, setPriorityFilter] = useState<TaskPriority | "all">("all");
  const { tasks, isLoading, isError } = useFilteredTasks(
    projectId,
    statusFilter === "all" ? "" : statusFilter,
    priorityFilter === "all" ? "" : priorityFilter,
  );
  const createMutation = useCreateTask(projectId);
  const updateMutation = useUpdateTask(projectId);
  const deleteMutation = useDeleteTask(projectId);
  const changeStatusMutation = useChangeTaskStatus(projectId);
  const changePriorityMutation = useChangeTaskPriority(projectId);
  const [createOpen, setCreateOpen] = useState(false);
  const [editTask, setEditTask] = useState<Task | null>(null);
  const [deleteTaskId, setDeleteTaskId] = useState<number | null>(null);

  const { data: members = [] } = useQuery({
    queryKey: ["project-members", projectId],
    queryFn: () => membersApi.list(projectId),
    enabled: !!projectId,
  });

  const handleCreate = (data: { name: string; priority?: TaskPriority; assigned_user_id?: number | null }) => {
    createMutation.mutate(data, {
      onSuccess: () => setCreateOpen(false),
    });
  };

  const handleUpdate = (data: { name: string; priority?: TaskPriority; assigned_user_id?: number | null }) => {
    if (!editTask) return;
    updateMutation.mutate(
      { taskId: editTask.id, payload: data },
      { onSuccess: () => setEditTask(null) },
    );
  };

  const handleDelete = (taskId: number) => {
    deleteMutation.mutate(taskId, {
      onSuccess: () => setDeleteTaskId(null),
    });
  };

  const canEdit = (assignedUserId: number | null) => {
    if (isOwner) return true;
    return assignedUserId === userId;
  };

  const getMemberName = (assignedUserId: number | null) => {
    if (!assignedUserId) return "";
    const member = members.find((m) => m.user_id === assignedUserId);
    return member ? member.full_name || member.email : `Usuario #${assignedUserId}`;
  };

  const clearFilters = () => {
    setStatusFilter("all");
    setPriorityFilter("all");
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-20 w-full" />
        <Skeleton className="h-20 w-full" />
      </div>
    );
  }

  if (isError) {
    return (
      <div className="text-center py-8">
        <p className="text-destructive">Error al cargar tareas</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-4 flex-wrap">
        <div className="flex gap-2">
          <Select value={statusFilter} onValueChange={(v) => setStatusFilter(v as TaskStatus | "all")}>
            <SelectTrigger className="h-9 w-[170px]">
              <SelectValue placeholder="Todos los estados" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todos los estados</SelectItem>
              {Object.entries(statusLabels).map(([value, label]) => (
                <SelectItem key={value} value={value}>{label}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select value={priorityFilter} onValueChange={(v) => setPriorityFilter(v as TaskPriority | "all")}>
            <SelectTrigger className="h-9 w-[180px]">
              <SelectValue placeholder="Todas las prioridades" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todas las prioridades</SelectItem>
              {Object.entries(priorityLabels).map(([value, label]) => (
                <SelectItem key={value} value={value}>{label}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          {(statusFilter || priorityFilter) && (
            <Button variant="ghost" size="sm" onClick={clearFilters}>Limpiar</Button>
          )}
        </div>
        {!isArchived && (
          <Dialog open={createOpen} onOpenChange={setCreateOpen}>
            <DialogTrigger asChild>
              <Button size="sm">
                <Plus className="mr-2 h-4 w-4" /> Agregar Tarea
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Crear Tarea</DialogTitle>
                <DialogDescription>
                  Completa los campos para crear una nueva tarea.
                </DialogDescription>
              </DialogHeader>
              <TaskForm
                members={members}
                onSubmit={handleCreate}
                isPending={createMutation.isPending}
                mode="create"
                onCancel={() => setCreateOpen(false)}
              />
            </DialogContent>
          </Dialog>
        )}
      </div>

      {!isArchived && tasks.length > 0 && (
        <p className="text-xs text-muted-foreground">Consejo: Haz clic en la insignia de estado o prioridad para cambiarla</p>
      )}

      {tasks.length === 0 ? (
        <div className="text-center py-12 border rounded-lg">
          <ClipboardList className="mx-auto h-12 w-12 text-muted-foreground" />
          <h3 className="mt-4 text-lg font-semibold">
            {statusFilter || priorityFilter ? "Sin tareas que coincidan" : "Sin tareas aún"}
          </h3>
          <p className="text-muted-foreground mt-2">
            {statusFilter || priorityFilter
              ? "Prueba ajustando los filtros"
              : "Crea tu primera tarea para comenzar."}
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {tasks.map((task) => (
            <div
              key={task.id}
              className={`flex items-center justify-between gap-4 rounded-lg border p-4 ${isArchived ? "opacity-75" : ""}`}
            >
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="font-medium truncate">{task.name}</span>
                  <TaskStatusBadge status={task.status} />
                  <TaskPriorityBadge priority={task.priority} />
                </div>
                {task.assigned_user_id && (
                  <p className="text-sm text-muted-foreground mt-1">
                    Asignada a {getMemberName(task.assigned_user_id)}
                  </p>
                )}
                {!isArchived && canEdit(task.assigned_user_id) && (
                  <div className="flex gap-2 mt-2">
                    <Select
                      value={task.status}
                      onValueChange={(v) =>
                        changeStatusMutation.mutate({
                          taskId: task.id,
                          payload: { status: v as TaskStatus },
                        })
                      }
                    >
                      <SelectTrigger className="h-7 text-xs w-[130px]">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {Object.entries(statusLabels).map(([value, label]) => (
                          <SelectItem key={value} value={value} className="text-xs">{label}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <Select
                      value={task.priority}
                      onValueChange={(v) =>
                        changePriorityMutation.mutate({
                          taskId: task.id,
                          payload: { priority: v as TaskPriority },
                        })
                      }
                    >
                      <SelectTrigger className="h-7 text-xs w-[110px]">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {Object.entries(priorityLabels).map(([value, label]) => (
                          <SelectItem key={value} value={value} className="text-xs">{label}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                )}
              </div>
              {!isArchived && canEdit(task.assigned_user_id) && (
                <div className="flex gap-1 shrink-0">
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8"
                    onClick={() => setEditTask(task)}
                  >
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8"
                    onClick={() => setDeleteTaskId(task.id)}
                  >
                    <Trash2 className="h-4 w-4 text-destructive" />
                  </Button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      <Dialog open={editTask !== null} onOpenChange={(open) => !open && setEditTask(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Editar Tarea</DialogTitle>
            <DialogDescription>
              Modifica los campos de la tarea.
            </DialogDescription>
          </DialogHeader>
          {editTask && (
            <TaskForm
              members={members}
              defaultValues={{
                name: editTask.name,
                priority: editTask.priority,
                assigned_user_id: editTask.assigned_user_id,
              }}
              onSubmit={handleUpdate}
              isPending={updateMutation.isPending}
              mode="edit"
              onCancel={() => setEditTask(null)}
            />
          )}
        </DialogContent>
      </Dialog>

      <AlertDialog open={deleteTaskId !== null} onOpenChange={(open) => !open && setDeleteTaskId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>¿Eliminar tarea?</AlertDialogTitle>
            <AlertDialogDescription>
              Esta acción no se puede deshacer. La tarea será eliminada permanentemente.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancelar</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => deleteTaskId && handleDelete(deleteTaskId)}
              className="bg-destructive text-destructive-foreground"
            >
              {deleteMutation.isPending ? "Eliminando..." : "Eliminar"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
