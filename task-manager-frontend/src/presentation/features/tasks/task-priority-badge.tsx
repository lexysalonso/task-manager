import { Badge } from "@/presentation/components/ui/badge";
import type { TaskPriority } from "@/domain/types";
import { priorityLabels } from "@/lib/constants";

const priorityStyles: Record<TaskPriority, string> = {
  low: "bg-green-100 text-green-700 hover:bg-green-100",
  medium: "bg-yellow-100 text-yellow-700 hover:bg-yellow-100",
  high: "bg-red-100 text-red-700 hover:bg-red-100",
};

interface TaskPriorityBadgeProps {
  priority: TaskPriority;
}

export function TaskPriorityBadge({ priority }: TaskPriorityBadgeProps) {
  return (
    <Badge className={priorityStyles[priority]} variant="secondary">
      {priorityLabels[priority]}
    </Badge>
  );
}
