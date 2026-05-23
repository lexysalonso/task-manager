import apiClient from "./client";

export interface UserSearchResult {
  id: number;
  email: string;
  full_name: string;
}

export const usersApi = {
  search: async (q: string): Promise<UserSearchResult[]> => {
    const { data } = await apiClient.get<UserSearchResult[]>("/users/search", {
      params: { q },
    });
    return data;
  },
};
