import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { projectsApi } from "@/infrastructure/api/projects.api";
import type { CreateProjectPayload, UpdateProjectPayload } from "@/infrastructure/api/projects.api";
import { AxiosError } from "axios";
import type { ApiError } from "@/domain/types";

export function useProjects() {
  return useQuery({
    queryKey: ["projects"],
    queryFn: projectsApi.list,
  });
}

export function useProject(id: number) {
  return useQuery({
    queryKey: ["projects", id],
    queryFn: () => projectsApi.getById(id),
    enabled: !!id,
  });
}

export function useCreateProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: CreateProjectPayload) => projectsApi.create(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
      toast.success("Proyecto creado");
    },
    onError: (error: AxiosError<ApiError>) => {
      toast.error(error.response?.data?.detail || "Error al crear proyecto");
    },
  });
}

export function useUpdateProject(projectId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: UpdateProjectPayload) => projectsApi.update(projectId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
      queryClient.invalidateQueries({ queryKey: ["projects", projectId] });
      toast.success("Proyecto actualizado");
    },
    onError: (error: AxiosError<ApiError>) => {
      toast.error(error.response?.data?.detail || "Error al actualizar proyecto");
    },
  });
}

export function useDeleteProject(projectId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => projectsApi.delete(projectId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
      toast.success("Proyecto eliminado");
    },
    onError: (error: AxiosError<ApiError>) => {
      toast.error(error.response?.data?.detail || "Error al eliminar proyecto");
    },
  });
}
