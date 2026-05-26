import { Button } from "@/presentation/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/presentation/components/ui/select";
import { Plus } from "lucide-react";
import { statusLabels, priorityLabels } from "@/lib/constants";
import type { TaskStatus, TaskPriority } from "@/domain/types";

interface TaskFiltersProps {
  statusFilter: TaskStatus | "all";
  priorityFilter: TaskPriority | "all";
  onStatusFilterChange: (value: TaskStatus | "all") => void;
  onPriorityFilterChange: (value: TaskPriority | "all") => void;
  onClear: () => void;
  canCreate: boolean;
  onOpenCreate: () => void;
}

export function TaskFilters({
  statusFilter,
  priorityFilter,
  onStatusFilterChange,
  onPriorityFilterChange,
  onClear,
  canCreate,
  onOpenCreate,
}: TaskFiltersProps) {
  return (
    <div className="flex items-center justify-between gap-4 flex-wrap">
      <div className="flex gap-2">
        <Select value={statusFilter} onValueChange={(v) => onStatusFilterChange(v as TaskStatus | "all")}>
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
        <Select value={priorityFilter} onValueChange={(v) => onPriorityFilterChange(v as TaskPriority | "all")}>
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
        {(statusFilter !== "all" || priorityFilter !== "all") && (
          <Button variant="ghost" size="sm" onClick={onClear}>Limpiar</Button>
        )}
      </div>
      {canCreate && (
        <Button size="sm" onClick={onOpenCreate}>
          <Plus className="mr-2 h-4 w-4" /> Agregar Tarea
        </Button>
      )}
    </div>
  );
}
