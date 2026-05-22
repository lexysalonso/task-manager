export enum TaskStatus {
  PENDING = "pending",
  IN_PROGRESS = "in_progress",
  COMPLETED = "completed",
}

export enum TaskPriority {
  LOW = "low",
  MEDIUM = "medium",
  HIGH = "high",
}

export interface User {
  id: number;
  email: string;
  full_name: string;
}

export interface Project {
  id: number;
  name: string;
  description: string;
  is_archived: boolean;
  owner_id: number;
  created_at: string;
  member_count: number;
  member_ids: number[];
}

export interface ProjectMember {
  project_id: number;
  user_id: number;
  user_email: string;
}

export interface Task {
  id: number;
  name: string;
  status: TaskStatus;
  priority: TaskPriority;
  project_id: number;
  assigned_user_id: number | null;
  created_at: string;
  updated_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: {
    id: number;
    email: string;
    full_name: string;
  };
}

export interface ApiError {
  detail: string;
  code: string;
}
