import { useState } from "react";
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
import { useFilteredTasks, useCreateTask, useUpdateTask, useDeleteTask, useChangeTaskStatus, useChangeTaskPriority } from "@/application/hooks/use-tasks";
import { useProjectMembers } from "@/application/hooks/use-members";
import { useAuthStore } from "@/application/store/auth.store";
import { TaskForm } from "./task-form";
import { TaskFilters } from "./task-filters";
import { TaskItem } from "./task-item";
import { TaskStatus, TaskPriority, type Task } from "@/domain/types";
import { ClipboardList } from "lucide-react";

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

  const { data: members = [] } = useProjectMembers(projectId);

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

  const getMemberName = (assignedUserId: number | null) => {
    if (!assignedUserId) return "";
    const member = members.find((m) => m.user_id === assignedUserId);
    return member ? member.full_name || member.email : `Usuario #${assignedUserId}`;
  };

  const canEditTask = (task: Task) => {
    if (isOwner) return true;
    return task.assigned_user_id === userId;
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
      <TaskFilters
        statusFilter={statusFilter}
        priorityFilter={priorityFilter}
        onStatusFilterChange={setStatusFilter}
        onPriorityFilterChange={setPriorityFilter}
        onClear={() => { setStatusFilter("all"); setPriorityFilter("all"); }}
        canCreate={!isArchived}
        onOpenCreate={() => setCreateOpen(true)}
      />

      {tasks.length === 0 ? (
        <div className="text-center py-12 border rounded-lg">
          <ClipboardList className="mx-auto h-12 w-12 text-muted-foreground" />
          <h3 className="mt-4 text-lg font-semibold">
            {statusFilter !== "all" || priorityFilter !== "all" ? "Sin tareas que coincidan" : "Sin tareas aún"}
          </h3>
          <p className="text-muted-foreground mt-2">
            {statusFilter !== "all" || priorityFilter !== "all"
              ? "Prueba ajustando los filtros"
              : "Crea tu primera tarea para comenzar."}
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {tasks.map((task) => (
            <TaskItem
              key={task.id}
              task={task}
              memberName={getMemberName(task.assigned_user_id)}
              canEdit={canEditTask(task)}
              isArchived={isArchived}
              onChangeStatus={(taskId, status) =>
                changeStatusMutation.mutate({ taskId, payload: { status } })
              }
              onChangePriority={(taskId, priority) =>
                changePriorityMutation.mutate({ taskId, payload: { priority } })
              }
              onEdit={setEditTask}
              onDelete={(taskId) => setDeleteTaskId(taskId)}
            />
          ))}
        </div>
      )}

      <Dialog open={createOpen} onOpenChange={setCreateOpen}>
        <DialogTrigger asChild>
          <span />
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
