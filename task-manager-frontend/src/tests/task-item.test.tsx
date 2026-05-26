import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
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
  return render(
    <TaskItem
      task={task}
      memberName={overrides.memberName ?? "Alice"}
      canEdit={overrides.canEdit ?? true}
      isArchived={overrides.isArchived ?? false}
      onChangeStatus={vi.fn()}
      onChangePriority={vi.fn()}
      onEdit={vi.fn()}
      onDelete={vi.fn()}
    />,
  );
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
    const { container } = renderTaskItem({ canEdit: true, isArchived: false });
    // Edit button contains lucide-square-pen icon, delete has lucide-trash2
    expect(container.querySelector(".lucide-square-pen")).toBeInTheDocument();
    expect(container.querySelector(".lucide-trash2")).toBeInTheDocument();
  });

  it("hides edit/delete buttons when archived", () => {
    const { container } = renderTaskItem({ canEdit: true, isArchived: true });
    expect(container.querySelector(".lucide-square-pen")).not.toBeInTheDocument();
    expect(container.querySelector(".lucide-trash2")).not.toBeInTheDocument();
  });

  it("hides edit/delete buttons when user cannot edit", () => {
    const { container } = renderTaskItem({ canEdit: false, isArchived: false });
    expect(container.querySelector(".lucide-square-pen")).not.toBeInTheDocument();
    expect(container.querySelector(".lucide-trash2")).not.toBeInTheDocument();
  });

  it("applies opacity class when archived", () => {
    const { container } = renderTaskItem({ isArchived: true });
    expect(container.firstChild).toHaveClass("opacity-75");
  });
});
