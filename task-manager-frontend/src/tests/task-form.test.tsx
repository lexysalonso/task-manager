import { describe, it, expect, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TaskForm } from "@/presentation/features/tasks/task-form";

function renderForm(overrides: {
  mode?: "create" | "edit";
  members?: Array<{ user_id: number; full_name: string; email: string }>;
} = {}) {
  const onSubmit = vi.fn();
  const onCancel = vi.fn();
  const utils = render(
    <TaskForm
      members={overrides.members ?? []}
      onSubmit={onSubmit}
      isPending={false}
      mode={overrides.mode ?? "create"}
      onCancel={onCancel}
    />,
  );
  return { ...utils, onSubmit, onCancel };
}

describe("TaskForm", () => {
  it("renders the form with name field", () => {
    renderForm();
    expect(screen.getByLabelText("Nombre de la tarea")).toBeInTheDocument();
    expect(screen.getByText("Crear Tarea")).toBeInTheDocument();
  });

  it("shows 'Guardar Cambios' button in edit mode", () => {
    renderForm({ mode: "edit" });
    expect(screen.getByText("Guardar Cambios")).toBeInTheDocument();
  });

  it("shows cancel button when onCancel is provided", () => {
    renderForm();
    expect(screen.getByText("Cancelar")).toBeInTheDocument();
  });

  it("calls onCancel when cancel button is clicked", async () => {
    const { onCancel } = renderForm();
    const user = userEvent.setup();
    await user.click(screen.getByText("Cancelar"));
    expect(onCancel).toHaveBeenCalledOnce();
  });

  it("calls onSubmit with form data when valid", async () => {
    const { onSubmit } = renderForm({ members: [{ user_id: 5, full_name: "Alice", email: "a@b.com" }] });
    const user = userEvent.setup();

    await user.type(screen.getByLabelText("Nombre de la tarea"), "Mi nueva tarea");
    await user.click(screen.getByText("Crear Tarea"));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith(
        expect.objectContaining({ name: "Mi nueva tarea" }),
        expect.anything(),
      );
    });
  });

  it("shows validation error when name is too short", async () => {
    renderForm();
    const user = userEvent.setup();

    await user.type(screen.getByLabelText("Nombre de la tarea"), "ab");
    await user.click(screen.getByText("Crear Tarea"));

    expect(await screen.findByText(/3 caracteres/i)).toBeInTheDocument();
  });
});
