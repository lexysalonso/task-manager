import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { membersApi } from "@/infrastructure/api/members.api";
import { AxiosError } from "axios";
import type { ApiError } from "@/domain/types";

export function useMembers(projectId: number) {
  return useQuery({
    queryKey: ["members", projectId],
    queryFn: () => {
      // Members are fetched as part of the project detail
      // This is a placeholder - the actual members come from the project query
      return { members: [] };
    },
    enabled: false,
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
      queryClient.invalidateQueries({ queryKey: ["tasks", projectId] });
      toast.success("Miembro eliminado. Tareas reasignadas al propietario.");
    },
    onError: (error: AxiosError<ApiError>) => {
      toast.error(error.response?.data?.detail || "Error al eliminar miembro");
    },
  });
}
