import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/presentation/components/ui/button";
import { Input } from "@/presentation/components/ui/input";
import { Badge } from "@/presentation/components/ui/badge";
import { Avatar, AvatarFallback } from "@/presentation/components/ui/avatar";
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from "@/presentation/components/ui/alert-dialog";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/presentation/components/ui/dialog";
import { Skeleton } from "@/presentation/components/ui/skeleton";
import { useQueryClient } from "@tanstack/react-query";
import { useAuthStore } from "@/application/store/auth.store";
import { useAddMember, useRemoveMember } from "@/application/hooks/useMembers";
import { projectsApi } from "@/infrastructure/api/projects.api";
import { membersApi } from "@/infrastructure/api/members.api";
import { UserPlus, Trash2, Shield, Mail } from "lucide-react";

interface MemberListProps {
  projectId: number;
  isOwner: boolean;
}

interface MemberInfo {
  user_id: number;
  user_email: string;
}

export function MemberList({ projectId, isOwner }: MemberListProps) {
  const userId = useAuthStore((s) => s.user?.id);
  const queryClient = useQueryClient();
  const [addOpen, setAddOpen] = useState(false);
  const [removeId, setRemoveId] = useState<number | null>(null);
  const [newUserId, setNewUserId] = useState("");
  const addMutation = useAddMember(projectId);
  const removeMutation = useRemoveMember(projectId);

  // Fetch project which includes member info via member_ids
  const { data: project, isLoading } = useQuery({
    queryKey: ["projects", projectId],
    queryFn: () => projectsApi.getById(projectId),
    enabled: !!projectId,
  });

  // Fetch members list properly
  const { data: membersData, isLoading: membersLoading, refetch } = useQuery({
    queryKey: ["project-members", projectId],
    queryFn: async () => {
      // Since we don't have a direct endpoint for listing members with emails,
      // we'll use the project data which has member_ids
      const p = await projectsApi.getById(projectId);
      return {
        members: (p.member_ids || []).map((id: number) => ({
          user_id: id,
          user_email: id === p.owner_id ? `Owner #${id}` : `User #${id}`,
        })),
        ownerId: p.owner_id,
      };
    },
    enabled: !!projectId,
  });

  const handleAdd = () => {
    const uid = Number(newUserId);
    if (!uid) return;
    addMutation.mutate(uid, {
      onSuccess: () => {
        setAddOpen(false);
        setNewUserId("");
        refetch();
        queryClient.invalidateQueries({ queryKey: ["projects", projectId] });
      },
    });
  };

  const handleRemove = (uid: number) => {
    removeMutation.mutate(uid, {
      onSuccess: () => {
        setRemoveId(null);
        refetch();
        queryClient.invalidateQueries({ queryKey: ["projects", projectId] });
      },
    });
  };

  if (isLoading || membersLoading) {
    return (
      <div className="space-y-3">
        <Skeleton className="h-12 w-full" />
        <Skeleton className="h-12 w-full" />
      </div>
    );
  }

  const members = membersData?.members || [];
  const ownerId = membersData?.ownerId;

  return (
    <div className="space-y-4">
      {isOwner && (
        <div className="flex justify-end">
          <Dialog open={addOpen} onOpenChange={setAddOpen}>
            <DialogTrigger asChild>
              <Button size="sm">
                <UserPlus className="mr-2 h-4 w-4" /> Agregar Miembro
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Agregar Miembro</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">ID de Usuario</label>
                  <Input
                    type="number"
                    placeholder="Ingresa el ID del usuario"
                    value={newUserId}
                    onChange={(e) => setNewUserId(e.target.value)}
                  />
                  <p className="text-xs text-muted-foreground">
                    Ingresa el ID del usuario para agregarlo a este proyecto.
                  </p>
                </div>
                <div className="flex justify-end gap-2">
                  <Button variant="outline" onClick={() => setAddOpen(false)}>Cancelar</Button>
                  <Button onClick={handleAdd} disabled={!newUserId || addMutation.isPending}>
                    {addMutation.isPending ? "Agregando..." : "Agregar"}
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      )}

      <div className="space-y-2">
        {members.length === 0 ? (
          <p className="text-center text-muted-foreground py-8">No se encontraron miembros</p>
        ) : (
          members.map((member: MemberInfo) => (
            <div
              key={member.user_id}
              className="flex items-center justify-between rounded-lg border p-4"
            >
              <div className="flex items-center gap-3">
                <Avatar className="h-9 w-9">
                  <AvatarFallback>
                    {member.user_email
                      .split("@")[0]
                      .slice(0, 2)
                      .toUpperCase() || "U"}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-sm">{member.user_email}</span>
                    {member.user_id === ownerId && (
                      <Badge variant="default" className="text-xs h-5">
                        <Shield className="mr-1 h-3 w-3" /> Propietario
                      </Badge>
                    )}
                    {member.user_id === userId && member.user_id !== ownerId && (
                      <Badge variant="secondary" className="text-xs h-5">Tú</Badge>
                    )}
                  </div>
                </div>
              </div>
              {isOwner && member.user_id !== ownerId && (
                <AlertDialog
                  open={removeId === member.user_id}
                  onOpenChange={(open) => !open && setRemoveId(null)}
                >
                  <AlertDialogTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8 text-destructive"
                      onClick={() => setRemoveId(member.user_id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </AlertDialogTrigger>
                  <AlertDialogContent>
                    <AlertDialogHeader>
                    <AlertDialogTitle>¿Eliminar miembro?</AlertDialogTitle>
                    <AlertDialogDescription className="space-y-2">
                      <p>
                        ¿Estás seguro de que deseas eliminar a <strong>{member.user_email}</strong> de este proyecto?
                      </p>
                      <p className="font-semibold text-destructive">
                        ⚠️ Al eliminar este miembro, todas sus tareas se reasignarán al propietario del proyecto.
                      </p>
                      </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                      <AlertDialogCancel>Cancelar</AlertDialogCancel>
                      <AlertDialogAction
                        onClick={() => handleRemove(member.user_id)}
                        className="bg-destructive text-destructive-foreground"
                      >
                        {removeMutation.isPending ? "Eliminando..." : "Eliminar"}
                      </AlertDialogAction>
                    </AlertDialogFooter>
                  </AlertDialogContent>
                </AlertDialog>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
