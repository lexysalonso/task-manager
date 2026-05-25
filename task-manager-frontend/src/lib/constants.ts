import { TaskStatus, TaskPriority } from "@/domain/types";

export const STORAGE_TOKEN_KEY = "auth-token";
export const STORAGE_USER_KEY = "auth-user";

export const statusLabels: Record<TaskStatus, string> = {
  pending: "Pendiente",
  in_progress: "En Progreso",
  completed: "Completada",
};

export const priorityLabels: Record<TaskPriority, string> = {
  low: "Baja",
  medium: "Media",
  high: "Alta",
};
