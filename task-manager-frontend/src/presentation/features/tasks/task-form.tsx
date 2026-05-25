import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Button } from "@/presentation/components/ui/button";
import { Input } from "@/presentation/components/ui/input";
import { Label } from "@/presentation/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/presentation/components/ui/select";
import { TaskPriority, type ProjectMember } from "@/domain/types";
import { priorityLabels } from "@/lib/constants";
import { Loader2 } from "lucide-react";

const taskSchema = z.object({
  name: z.string().min(3, "El nombre debe tener al menos 3 caracteres").max(200, "El nombre es demasiado largo"),
  assigned_user_id: z.number().nullable().optional(),
  priority: z.nativeEnum(TaskPriority).optional(),
});

type TaskFormData = z.infer<typeof taskSchema>;

interface TaskFormProps {
  members: ProjectMember[];
  defaultValues?: { name?: string; priority?: TaskPriority; assigned_user_id?: number | null };
  onSubmit: (data: { name: string; priority?: TaskPriority; assigned_user_id?: number | null }) => void;
  isPending: boolean;
  mode: "create" | "edit";
  onCancel?: () => void;
}

export function TaskForm({ members, defaultValues, onSubmit, isPending, mode, onCancel }: TaskFormProps) {
  const { register, handleSubmit, setValue, formState: { errors } } = useForm<TaskFormData>({
    resolver: zodResolver(taskSchema),
    defaultValues: {
      name: defaultValues?.name || "",
      priority: defaultValues?.priority || TaskPriority.MEDIUM,
      assigned_user_id: defaultValues?.assigned_user_id || null,
    },
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="task-name">Nombre de la tarea</Label>
        <Input id="task-name" placeholder="Implementar inicio de sesión" {...register("name")} />
        {errors.name && <p className="text-sm text-destructive">{errors.name.message}</p>}
      </div>
      <div className="space-y-2">
        <Label htmlFor="task-priority">Prioridad</Label>
        <Select
          defaultValue={defaultValues?.priority || TaskPriority.MEDIUM}
          onValueChange={(v) => setValue("priority", v as TaskPriority)}
        >
          <SelectTrigger id="task-priority">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {Object.entries(priorityLabels).map(([value, label]) => (
              <SelectItem key={value} value={value}>{label}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div className="space-y-2">
        <Label htmlFor="task-assign">Asignar a</Label>
        <Select
          defaultValue={String(defaultValues?.assigned_user_id || "none")}
          onValueChange={(v) => setValue("assigned_user_id", v === "none" ? null : Number(v))}
        >
          <SelectTrigger id="task-assign">
            <SelectValue placeholder="Sin asignar" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="none">Sin asignar</SelectItem>
            {members.map((m) => (
              <SelectItem key={m.user_id} value={String(m.user_id)}>{m.full_name || m.email}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div className="flex gap-2 justify-end">
        {onCancel && (
          <Button type="button" variant="outline" onClick={onCancel}>Cancelar</Button>
        )}
        <Button type="submit" disabled={isPending}>
          {isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          {mode === "create" ? "Crear Tarea" : "Guardar Cambios"}
        </Button>
      </div>
    </form>
  );
}
