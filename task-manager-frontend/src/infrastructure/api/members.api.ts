import apiClient from "./client";
import type { ProjectMember } from "@/domain/types";

export interface AddMemberPayload {
  user_id: number;
}

export const membersApi = {
  list: async (projectId: number): Promise<ProjectMember[]> => {
    const { data } = await apiClient.get<ProjectMember[]>(`/projects/${projectId}/members`);
    return data;
  },
  add: async (projectId: number, payload: AddMemberPayload): Promise<void> => {
    await apiClient.post(`/projects/${projectId}/members`, payload);
  },
  remove: async (projectId: number, userId: number): Promise<void> => {
    await apiClient.delete(`/projects/${projectId}/members/${userId}`);
  },
};
