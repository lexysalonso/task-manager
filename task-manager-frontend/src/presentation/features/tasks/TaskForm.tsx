import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Button } from "@/presentation/components/ui/button";
import { Input } from "@/presentation/components/ui/input";
import { Label } from "@/presentation/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/presentation/components/ui/select";
import { TaskPriority, TaskStatus } from "@/domain/types";
import { Loader2 } from "lucide-react";

const taskSchema = z.object({
  name: z.string().min(3, "El nombre debe tener al menos 3 caracteres").max(200, "El nombre es demasiado largo"),
  assigned_user_id: z.number().nullable().optional(),
  priority: z.nativeEnum(TaskPriority).optional(),
});

type TaskFormData = z.infer<typeof taskSchema>;

interface MemberOption {
  user_id: number;
  user_email: string;
}

interface TaskFormProps {
  members: MemberOption[];
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
        <select
          id="task-priority"
          className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 cursor-pointer"
          defaultValue={defaultValues?.priority || TaskPriority.MEDIUM}
          onChange={(e) => setValue("priority", e.target.value as TaskPriority)}
        >
          <option value={TaskPriority.LOW}>Baja</option>
          <option value={TaskPriority.MEDIUM}>Media</option>
          <option value={TaskPriority.HIGH}>Alta</option>
        </select>
      </div>
      <div className="space-y-2">
        <Label htmlFor="task-assign">Asignar a</Label>
        <select
          id="task-assign"
          className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 cursor-pointer"
          defaultValue={defaultValues?.assigned_user_id || ""}
          onChange={(e) => setValue("assigned_user_id", e.target.value ? Number(e.target.value) : null)}
        >
          <option value="">Sin asignar</option>
          {members.map((m) => (
            <option key={m.user_id} value={m.user_id}>{m.user_email}</option>
          ))}
        </select>
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
