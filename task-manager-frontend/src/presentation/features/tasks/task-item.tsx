import { Button } from "@/presentation/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/presentation/components/ui/select";
import { Edit, Trash2 } from "lucide-react";
import { TaskStatusBadge } from "./task-status-badge";
import { TaskPriorityBadge } from "./task-priority-badge";
import { statusLabels, priorityLabels } from "@/lib/constants";
import type { Task, TaskStatus, TaskPriority } from "@/domain/types";

interface TaskItemProps {
  task: Task;
  memberName: string;
  canEdit: boolean;
  isArchived: boolean;
  onChangeStatus: (taskId: number, status: TaskStatus) => void;
  onChangePriority: (taskId: number, priority: TaskPriority) => void;
  onEdit: (task: Task) => void;
  onDelete: (taskId: number) => void;
}

export function TaskItem({
  task,
  memberName,
  canEdit,
  isArchived,
  onChangeStatus,
  onChangePriority,
  onEdit,
  onDelete,
}: TaskItemProps) {
  return (
    <div
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
            Asignada a {memberName}
          </p>
        )}
        {!isArchived && canEdit && (
          <div className="flex gap-2 mt-2">
            <Select
              value={task.status}
              onValueChange={(v) => onChangeStatus(task.id, v as TaskStatus)}
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
              onValueChange={(v) => onChangePriority(task.id, v as TaskPriority)}
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
      {!isArchived && canEdit && (
        <div className="flex gap-1 shrink-0">
          <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => onEdit(task)} aria-label="Editar tarea">
            <Edit className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={() => onDelete(task.id)}
            aria-label="Eliminar tarea"
          >
            <Trash2 className="h-4 w-4 text-destructive" />
          </Button>
        </div>
      )}
    </div>
  );
}
