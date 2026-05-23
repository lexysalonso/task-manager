import { useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { tasksApi } from "@/infrastructure/api/tasks.api";
import type {
  CreateTaskPayload,
  UpdateTaskPayload,
  ChangeStatusPayload,
  ChangePriorityPayload,
} from "@/infrastructure/api/tasks.api";
import type { TaskStatus, TaskPriority } from "@/domain/types";
import { AxiosError } from "axios";
import type { ApiError } from "@/domain/types";

export function useTasks(projectId: number) {
  return useQuery({
    queryKey: ["tasks", projectId],
    queryFn: () => tasksApi.listByProject(projectId),
    enabled: !!projectId,
  });
}

export function useFilteredTasks(projectId: number, status?: TaskStatus | "", priority?: TaskPriority | "") {
  const { data, ...rest } = useTasks(projectId);

  const filteredTasks = useMemo(() => {
    if (!data?.tasks) return [];
    let tasks = data.tasks;
    if (status) {
      tasks = tasks.filter((t) => t.status === status);
    }
    if (priority) {
      tasks = tasks.filter((t) => t.priority === priority);
    }
    return tasks;
  }, [data, status, priority]);

  return { tasks: filteredTasks, allTasks: data?.tasks || [], ...rest };
}

export function useCreateTask(projectId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: CreateTaskPayload) => tasksApi.create(projectId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks", projectId] });
      toast.success("Tarea creada");
    },
    onError: (error: AxiosError<ApiError>) => {
      toast.error(error.response?.data?.detail || "Error al crear tarea");
    },
  });
}

export function useUpdateTask(projectId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ taskId, payload }: { taskId: number; payload: UpdateTaskPayload }) =>
      tasksApi.update(projectId, taskId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks", projectId] });
      toast.success("Tarea actualizada");
    },
    onError: (error: AxiosError<ApiError>) => {
      toast.error(error.response?.data?.detail || "Error al actualizar tarea");
    },
  });
}

export function useChangeTaskStatus(projectId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ taskId, payload }: { taskId: number; payload: ChangeStatusPayload }) =>
      tasksApi.changeStatus(projectId, taskId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks", projectId] });
      toast.success("Estado actualizado");
    },
    onError: (error: AxiosError<ApiError>) => {
      toast.error(error.response?.data?.detail || "Error al actualizar estado");
    },
  });
}

export function useChangeTaskPriority(projectId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ taskId, payload }: { taskId: number; payload: ChangePriorityPayload }) =>
      tasksApi.changePriority(projectId, taskId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks", projectId] });
      toast.success("Prioridad actualizada");
    },
    onError: (error: AxiosError<ApiError>) => {
      toast.error(error.response?.data?.detail || "Error al actualizar prioridad");
    },
  });
}

export function useDeleteTask(projectId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (taskId: number) => tasksApi.delete(projectId, taskId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks", projectId] });
      toast.success("Tarea eliminada");
    },
    onError: (error: AxiosError<ApiError>) => {
      toast.error(error.response?.data?.detail || "Error al eliminar tarea");
    },
  });
}
