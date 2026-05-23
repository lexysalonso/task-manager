import { Badge } from "@/presentation/components/ui/badge";
import type { TaskStatus } from "@/domain/types";

const statusStyles: Record<TaskStatus, string> = {
  pending: "bg-gray-100 text-gray-700 hover:bg-gray-100",
  in_progress: "bg-blue-100 text-blue-700 hover:bg-blue-100",
  completed: "bg-green-100 text-green-700 hover:bg-green-100",
};

const statusLabels: Record<TaskStatus, string> = {
  pending: "Pendiente",
  in_progress: "En Progreso",
  completed: "Completada",
};

interface TaskStatusBadgeProps {
  status: TaskStatus;
}

export function TaskStatusBadge({ status }: TaskStatusBadgeProps) {
  return (
    <Badge className={statusStyles[status]} variant="secondary">
      {statusLabels[status]}
    </Badge>
  );
}
