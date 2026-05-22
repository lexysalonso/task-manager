import apiClient from "./client";
import type { Project, AuthResponse } from "@/domain/types";

export interface CreateProjectPayload {
  name: string;
  description?: string;
}

export interface UpdateProjectPayload {
  name?: string;
  description?: string;
  is_archived?: boolean;
}

export interface ProjectListResponse {
  projects: Project[];
}

export const projectsApi = {
  list: async (): Promise<ProjectListResponse> => {
    const { data } = await apiClient.get<ProjectListResponse>("/projects");
    return data;
  },
  getById: async (id: number): Promise<Project> => {
    const { data } = await apiClient.get<Project>(`/projects/${id}`);
    return data;
  },
  create: async (payload: CreateProjectPayload): Promise<Project> => {
    const { data } = await apiClient.post<Project>("/projects", payload);
    return data;
  },
  update: async (id: number, payload: UpdateProjectPayload): Promise<Project> => {
    const { data } = await apiClient.put<Project>(`/projects/${id}`, payload);
    return data;
  },
  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/projects/${id}`);
  },
};
