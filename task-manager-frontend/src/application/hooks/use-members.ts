import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { membersApi } from "@/infrastructure/api/members.api";
import { usersApi } from "@/infrastructure/api/users.api";
import { projectsApi } from "@/infrastructure/api/projects.api";
import { AxiosError } from "axios";
import type { ApiError } from "@/domain/types";

export function useProjectMembers(projectId: number) {
  return useQuery({
    queryKey: ["project-members", projectId],
    queryFn: () => membersApi.list(projectId),
    enabled: !!projectId,
  });
}

export function useProjectOwner(projectId: number) {
  return useQuery({
    queryKey: ["project-owner", projectId],
    queryFn: () => projectsApi.getById(projectId).then((p) => p.owner_id),
    enabled: !!projectId,
  });
}

export function useUserSearch(query: string) {
  return useQuery({
    queryKey: ["users-search", query],
    queryFn: () => usersApi.search(query),
    enabled: query.length >= 2,
  });
}

export function useAddMember(projectId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (userId: number) => membersApi.add(projectId, { user_id: userId }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects", projectId] });
      queryClient.invalidateQueries({ queryKey: ["project-members", projectId] });
      toast.success("Miembro agregado");
    },
    onError: (error: AxiosError<ApiError>) => {
      toast.error(error.response?.data?.detail || "Error al agregar miembro");
    },
  });
}

export function useRemoveMember(projectId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (userId: number) => membersApi.remove(projectId, userId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects", projectId] });
      queryClient.invalidateQueries({ queryKey: ["project-members", projectId] });
      queryClient.invalidateQueries({ queryKey: ["tasks", projectId] });
      toast.success("Miembro eliminado. Tareas reasignadas al propietario.");
    },
    onError: (error: AxiosError<ApiError>) => {
      toast.error(error.response?.data?.detail || "Error al eliminar miembro");
    },
  });
}
