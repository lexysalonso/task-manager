import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Button } from "@/presentation/components/ui/button";
import { Input } from "@/presentation/components/ui/input";
import { Label } from "@/presentation/components/ui/label";
import { Loader2 } from "lucide-react";

const projectSchema = z.object({
  name: z.string().min(3, "El nombre debe tener al menos 3 caracteres").max(100, "El nombre es demasiado largo"),
  description: z.string().max(500, "La descripción es demasiado larga").optional().default(""),
});

type ProjectFormData = z.infer<typeof projectSchema>;

interface ProjectFormProps {
  defaultValues?: { name: string; description?: string; is_archived?: boolean };
  onSubmit: (data: { name: string; description?: string; is_archived?: boolean }) => void;
  isPending: boolean;
  mode: "create" | "edit";
}

export function ProjectForm({ defaultValues, onSubmit, isPending, mode }: ProjectFormProps) {
  const { register, handleSubmit, formState: { errors } } = useForm<ProjectFormData>({
    resolver: zodResolver(projectSchema),
    defaultValues: { name: defaultValues?.name || "", description: defaultValues?.description || "" },
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div className="space-y-2">
        <Label htmlFor="name">Nombre del proyecto</Label>
        <Input id="name" placeholder="Mi Proyecto" {...register("name")} />
        {errors.name && <p className="text-sm text-destructive">{errors.name.message}</p>}
      </div>
      <div className="space-y-2">
        <Label htmlFor="description">Descripción</Label>
        <textarea
          id="description"
          className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
          placeholder="Breve descripción de tu proyecto (opcional)"
          {...register("description")}
        />
        {errors.description && <p className="text-sm text-destructive">{errors.description.message}</p>}
      </div>
      {mode === "edit" && defaultValues && (
        <div className="space-y-2">
          <Label htmlFor="is_archived">Estado</Label>
          <select
            id="is_archived"
            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 cursor-pointer"
            defaultValue={defaultValues.is_archived ? "archived" : "active"}
            onChange={(e) => {
              const input = document.createElement("input");
              input.name = "is_archived";
              input.value = e.target.value === "archived" ? "true" : "false";
              input.type = "hidden";
              e.target.form?.appendChild(input);
            }}
          >
            <option value="active">Activo</option>
            <option value="archived">Archivado</option>
          </select>
        </div>
      )}
      <Button type="submit" disabled={isPending}>
        {isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
        {mode === "create" ? "Crear Proyecto" : "Guardar Cambios"}
      </Button>
    </form>
  );
}
