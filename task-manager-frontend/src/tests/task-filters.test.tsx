import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TaskFilters } from "@/presentation/features/tasks/task-filters";
import { TaskStatus, TaskPriority } from "@/domain/types";

function renderFilters(overrides: {
  statusFilter?: TaskStatus | "all";
  priorityFilter?: TaskPriority | "all";
  canCreate?: boolean;
} = {}) {
  const onOpenCreate = vi.fn();
  const onClear = vi.fn();
  const utils = render(
    <TaskFilters
      statusFilter={overrides.statusFilter ?? "all"}
      priorityFilter={overrides.priorityFilter ?? "all"}
      onStatusFilterChange={vi.fn()}
      onPriorityFilterChange={vi.fn()}
      onClear={onClear}
      canCreate={overrides.canCreate ?? true}
      onOpenCreate={onOpenCreate}
    />,
  );
  return { ...utils, onOpenCreate, onClear };
}

describe("TaskFilters", () => {
  it("renders filter selects", () => {
    renderFilters();
    expect(screen.getByText("Todos los estados")).toBeInTheDocument();
    expect(screen.getByText("Todas las prioridades")).toBeInTheDocument();
  });

  it("shows 'Agregar Tarea' button when canCreate is true", () => {
    renderFilters({ canCreate: true });
    expect(screen.getByText("Agregar Tarea")).toBeInTheDocument();
  });

  it("hides 'Agregar Tarea' button when canCreate is false", () => {
    renderFilters({ canCreate: false });
    expect(screen.queryByText("Agregar Tarea")).not.toBeInTheDocument();
  });

  it("shows 'Limpiar' button when a filter is active", () => {
    renderFilters({ statusFilter: TaskStatus.PENDING });
    expect(screen.getByText("Limpiar")).toBeInTheDocument();
  });

  it("hides 'Limpiar' button when no filters are active", () => {
    renderFilters({ statusFilter: "all", priorityFilter: "all" });
    expect(screen.queryByText("Limpiar")).not.toBeInTheDocument();
  });

  it("shows 'Limpiar' when priority filter is active", () => {
    renderFilters({ priorityFilter: TaskPriority.HIGH });
    expect(screen.getByText("Limpiar")).toBeInTheDocument();
  });

  it("calls onOpenCreate when 'Agregar Tarea' is clicked", async () => {
    const { onOpenCreate } = renderFilters({ canCreate: true });
    const user = userEvent.setup();
    await user.click(screen.getByText("Agregar Tarea"));
    expect(onOpenCreate).toHaveBeenCalledOnce();
  });

  it("calls onClear when 'Limpiar' is clicked", async () => {
    const { onClear } = renderFilters({ statusFilter: TaskStatus.PENDING });
    const user = userEvent.setup();
    await user.click(screen.getByText("Limpiar"));
    expect(onClear).toHaveBeenCalledOnce();
  });
});
