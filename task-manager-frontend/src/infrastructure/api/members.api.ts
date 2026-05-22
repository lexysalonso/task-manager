import apiClient from "./client";

export interface AddMemberPayload {
  user_id: number;
}

export interface MemberResponse {
  project_id: number;
  user_id: number;
  user_email: string;
}

export interface MemberListResponse {
  members: MemberResponse[];
}

export const membersApi = {
  add: async (projectId: number, payload: AddMemberPayload): Promise<void> => {
    await apiClient.post(`/projects/${projectId}/members`, payload);
  },
  remove: async (projectId: number, userId: number): Promise<void> => {
    await apiClient.delete(`/projects/${projectId}/members/${userId}`);
  },
};
