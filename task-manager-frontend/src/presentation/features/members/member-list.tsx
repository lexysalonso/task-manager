import { useState, useRef, useEffect } from "react";
import { Button } from "@/presentation/components/ui/button";
import { Input } from "@/presentation/components/ui/input";
import { Badge } from "@/presentation/components/ui/badge";
import { Avatar, AvatarFallback } from "@/presentation/components/ui/avatar";
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from "@/presentation/components/ui/alert-dialog";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogTrigger } from "@/presentation/components/ui/dialog";
import { Skeleton } from "@/presentation/components/ui/skeleton";
import { useAuthStore } from "@/application/store/auth.store";
import { useAddMember, useRemoveMember, useProjectMembers, useUserSearch } from "@/application/hooks/use-members";
import { UserPlus, Trash2, Shield, Loader2, Search } from "lucide-react";
import { getInitials } from "@/lib/utils";

interface MemberListProps {
    projectId: number;
    isOwner: boolean;
    ownerId?: number | null;
}

export function MemberList({ projectId, isOwner, ownerId }: MemberListProps) {
    const userId = useAuthStore((s) => s.user?.id);
    const [addOpen, setAddOpen] = useState(false);
    const [removeId, setRemoveId] = useState<number | null>(null);
    const [rawSearch, setRawSearch] = useState("");
    const [selectedUserId, setSelectedUserId] = useState<number | null>(null);
    const debounceRef = useRef<ReturnType<typeof setTimeout>>();
    const addMutation = useAddMember(projectId);
    const removeMutation = useRemoveMember(projectId);

    const [searchQuery, setSearchQuery] = useState("");
    useEffect(() => {
        if (debounceRef.current) clearTimeout(debounceRef.current);
        debounceRef.current = setTimeout(() => setSearchQuery(rawSearch), 300);
        return () => { if (debounceRef.current) clearTimeout(debounceRef.current); };
    }, [rawSearch]);

    const { data: members = [], isLoading, isError: membersError } = useProjectMembers(projectId);
    const { data: searchResults = [], isFetching: searching } = useUserSearch(searchQuery);

    const existingMemberIds = new Set(members.map((m) => m.user_id));

    const handleSearchChange = (value: string) => {
        setRawSearch(value);
        setSelectedUserId(null);
    };

    const handleAdd = () => {
        if (!selectedUserId) return;
        addMutation.mutate(selectedUserId, {
            onSuccess: () => {
                setAddOpen(false);
                setRawSearch("");
                setSelectedUserId(null);
            },
        });
    };

    const handleRemove = (uid: number) => {
        removeMutation.mutate(uid, {
            onSuccess: () => setRemoveId(null),
        });
    };

    if (isLoading) {
        return (
            <div className="space-y-3">
                <Skeleton className="h-12 w-full" />
                <Skeleton className="h-12 w-full" />
            </div>
        );
    }

    if (membersError) {
        return (
            <div className="text-center py-8">
                <p className="text-destructive">Error al cargar miembros</p>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            {isOwner && (
                <div className="flex justify-end">
                    <Dialog open={addOpen} onOpenChange={(open) => { setAddOpen(open); if (!open) { setRawSearch(""); setSelectedUserId(null); } }}>
                        <DialogTrigger asChild>
                            <Button size="sm">
                                <UserPlus className="mr-2 h-4 w-4" /> Agregar Miembro
                            </Button>
                        </DialogTrigger>
                        <DialogContent>
                            <DialogHeader>
                                <DialogTitle>Agregar Miembro</DialogTitle>
                                <DialogDescription>
                                    Busca un usuario por nombre o correo para agregarlo al proyecto.
                                </DialogDescription>
                            </DialogHeader>
                            <div className="space-y-4">
                                <div className="space-y-2">
                                    <label className="text-sm font-medium">Buscar usuario</label>
                                    <div className="relative">
                                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                                        <Input
                                            placeholder="Buscar por nombre o correo..."
                                            className="pl-9"
                                            value={rawSearch}
                                            onChange={(e) => handleSearchChange(e.target.value)}
                                        />
                                    </div>
                                    <div>
                                        {searchQuery.length < 2 ? (
                                            <p className="text-xs text-muted-foreground">Escribe al menos 2 caracteres para buscar usuarios.</p>
                                        ) : searching ? (
                                            <div className="flex items-center gap-2 text-sm text-muted-foreground py-4">
                                                <Loader2 className="h-3 w-3 animate-spin" /> Buscando...
                                            </div>
                                        ) : searchResults.length > 0 ? (
                                            <div className="max-h-48 overflow-y-auto border rounded-md">
                                                {searchResults.map((user) => {
                                                    const isMember = existingMemberIds.has(user.id);
                                                    const isOwnerUser = user.id === ownerId;
                                                    const selected = selectedUserId === user.id;
                                                    return (
                                                        <button
                                                            key={user.id}
                                                            type="button"
                                                            disabled={isMember || isOwnerUser}
                                                            className={`w-full text-left px-3 py-2 text-sm transition-colors
                              ${selected ? "bg-primary/10" : "hover:bg-muted"}
                              ${isMember || isOwnerUser ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}
                            `}
                                                            onClick={() => setSelectedUserId(user.id)}
                                                        >
                                                            <span className="font-medium">{user.full_name}</span>
                                                            <span className="text-muted-foreground ml-2">({user.email})</span>
                                                            {isMember && <span className="text-xs text-muted-foreground ml-2">— ya es miembro</span>}
                                                            {isOwnerUser && <span className="text-xs text-muted-foreground ml-2">— es el propietario</span>}
                                                        </button>
                                                    );
                                                })}
                                            </div>
                                        ) : (
                                            <p className="text-sm text-muted-foreground pt-4">No se encontraron usuarios</p>
                                        )}
                                    </div>
                                </div>
                                <div className="flex justify-end gap-2">
                                    <Button variant="outline" onClick={() => { setAddOpen(false); setRawSearch(""); setSelectedUserId(null); }}>Cancelar</Button>
                                    <Button onClick={handleAdd} disabled={!selectedUserId || addMutation.isPending}>
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
                    members.map((member) => (
                        <div
                            key={member.user_id}
                            className="flex items-center justify-between rounded-lg border p-4"
                        >
                            <div className="flex items-center gap-3">
                                <Avatar className="h-9 w-9">
                                    <AvatarFallback>
                                        {getInitials(member.full_name || member.email)}
                                    </AvatarFallback>
                                </Avatar>
                                <div>
                                    <div className="flex items-center gap-2">
                                        <span className="font-medium text-sm">{member.full_name || member.email}</span>
                                        {member.user_id === ownerId && (
                                            <Badge variant="default" className="text-xs h-5">
                                                <Shield className="mr-1 h-3 w-3" /> Propietario
                                            </Badge>
                                        )}
                                        {member.user_id === userId && member.user_id !== ownerId && (
                                            <Badge variant="secondary" className="text-xs h-5">Tú</Badge>
                                        )}
                                    </div>
                                    {member.full_name && (
                                        <p className="text-xs text-muted-foreground">{member.email}</p>
                                    )}
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
                                            <AlertDialogDescription>
                                                ¿Estás seguro de que deseas eliminar a <strong>{member.full_name || member.email}</strong> de este proyecto?
                                            </AlertDialogDescription>
                                            <p className="text-sm font-semibold text-destructive">
                                                ⚠️ Al eliminar este miembro, todas sus tareas se reasignarán al propietario del proyecto.
                                            </p>
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
