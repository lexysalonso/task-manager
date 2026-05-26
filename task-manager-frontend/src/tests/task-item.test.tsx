import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TaskItem } from "@/presentation/features/tasks/task-item";
import { TaskStatus, TaskPriority, type Task } from "@/domain/types";

const baseTask: Task = {
  id: 1,
  name: "Test Task",
  status: TaskStatus.PENDING,
  priority: TaskPriority.MEDIUM,
  project_id: 1,
  assigned_user_id: 1,
  created_at: "2024-01-01T00:00:00Z",
  updated_at: "2024-01-01T00:00:00Z",
};

function renderTaskItem(overrides: Partial<{
  task: Partial<Task>;
  memberName: string;
  canEdit: boolean;
  isArchived: boolean;
}> = {}) {
  const task = { ...baseTask, ...overrides.task };
  const onEdit = vi.fn();
  const onDelete = vi.fn();
  const utils = render(
    <TaskItem
      task={task}
      memberName={overrides.memberName ?? "Alice"}
      canEdit={overrides.canEdit ?? true}
      isArchived={overrides.isArchived ?? false}
      onChangeStatus={vi.fn()}
      onChangePriority={vi.fn()}
      onEdit={onEdit}
      onDelete={onDelete}
    />,
  );
  return { ...utils, onEdit, onDelete };
}

describe("TaskItem", () => {
  it("renders the task name", () => {
    renderTaskItem();
    expect(screen.getByText("Test Task")).toBeInTheDocument();
  });

  it("renders member name when task is assigned", () => {
    renderTaskItem({ memberName: "Alice" });
    expect(screen.getByText(/Asignada a/)).toHaveTextContent("Asignada a Alice");
  });

  it("does not show assigned section when task has no assignee", () => {
    renderTaskItem({ task: { assigned_user_id: null } });
    expect(screen.queryByText(/Asignada a/)).not.toBeInTheDocument();
  });

  it("shows edit and delete buttons when canEdit and not archived", () => {
    renderTaskItem({ canEdit: true, isArchived: false });
    expect(screen.getByRole("button", { name: /editar tarea/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /eliminar tarea/i })).toBeInTheDocument();
  });

  it("hides edit/delete buttons when archived", () => {
    renderTaskItem({ canEdit: true, isArchived: true });
    expect(screen.queryByRole("button", { name: /editar tarea/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /eliminar tarea/i })).not.toBeInTheDocument();
  });

  it("hides edit/delete buttons when user cannot edit", () => {
    renderTaskItem({ canEdit: false, isArchived: false });
    expect(screen.queryByRole("button", { name: /editar tarea/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /eliminar tarea/i })).not.toBeInTheDocument();
  });

  it("calls onEdit when edit button is clicked", async () => {
    const { onEdit } = renderTaskItem({ canEdit: true, isArchived: false });
    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: /editar tarea/i }));
    expect(onEdit).toHaveBeenCalledWith(expect.objectContaining({ id: 1, name: "Test Task" }));
  });

  it("calls onDelete when delete button is clicked", async () => {
    const { onDelete } = renderTaskItem({ canEdit: true, isArchived: false });
    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: /eliminar tarea/i }));
    expect(onDelete).toHaveBeenCalledWith(1);
  });

  it("applies opacity class when archived", () => {
    const { container } = renderTaskItem({ isArchived: true });
    expect(container.firstChild).toHaveClass("opacity-75");
  });
});
