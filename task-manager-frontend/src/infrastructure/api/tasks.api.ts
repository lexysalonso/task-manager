import apiClient from "./client";
import type { Task, TaskStatus, TaskPriority } from "@/domain/types";

export interface CreateTaskPayload {
  name: string;
  assigned_user_id?: number | null;
  priority?: TaskPriority;
}

export interface UpdateTaskPayload {
  name?: string;
  assigned_user_id?: number | null;
  priority?: TaskPriority;
}

export interface ChangeStatusPayload {
  status: TaskStatus;
}

export interface ChangePriorityPayload {
  priority: TaskPriority;
}

export interface TaskListResponse {
  tasks: Task[];
}

export const tasksApi = {
  listByProject: async (projectId: number): Promise<TaskListResponse> => {
    const { data } = await apiClient.get<TaskListResponse>(`/projects/${projectId}/tasks`);
    return data;
  },
  create: async (projectId: number, payload: CreateTaskPayload): Promise<Task> => {
    const { data } = await apiClient.post<Task>(`/projects/${projectId}/tasks`, payload);
    return data;
  },
  update: async (projectId: number, taskId: number, payload: UpdateTaskPayload): Promise<Task> => {
    const { data } = await apiClient.put<Task>(`/projects/${projectId}/tasks/${taskId}`, payload);
    return data;
  },
  changeStatus: async (projectId: number, taskId: number, payload: ChangeStatusPayload): Promise<Task> => {
    const { data } = await apiClient.patch<Task>(`/projects/${projectId}/tasks/${taskId}/status`, payload);
    return data;
  },
  changePriority: async (projectId: number, taskId: number, payload: ChangePriorityPayload): Promise<Task> => {
    const { data } = await apiClient.patch<Task>(`/projects/${projectId}/tasks/${taskId}/priority`, payload);
    return data;
  },
  delete: async (projectId: number, taskId: number): Promise<void> => {
    await apiClient.delete(`/projects/${projectId}/tasks/${taskId}`);
  },
};
