"""Integration tests for SQLAlchemy repositories using an in-memory SQLite database.

These tests exercise the actual repository implementations against a real database,
verifying that SQL queries, constraints, and relationships work correctly.
"""

from datetime import datetime, timezone

import pytest

from src.domain.entities.task import Task, TaskStatus, TaskPriority
from src.domain.entities.project import Project
from src.domain.entities.user import User
from src.infrastructure.db.repositories import (
    SqlAlchemyUserRepository,
    SqlAlchemyProjectRepository,
    SqlAlchemyTaskRepository,
)


# ── User Repository ──────────────────────────────


@pytest.mark.asyncio
async def test_user_repo_create_and_get_by_id(db_session) -> None:
    repo = SqlAlchemyUserRepository(db_session)
    user = User(email="alice@test.com", full_name="Alice", hashed_password="hashed_pwd")

    created = await repo.create(user)
    assert created.id is not None
    assert created.email == "alice@test.com"
    assert created.full_name == "Alice"

    fetched = await repo.get_by_id(created.id)
    assert fetched is not None
    assert fetched.email == "alice@test.com"


@pytest.mark.asyncio
async def test_user_repo_get_by_email(db_session) -> None:
    repo = SqlAlchemyUserRepository(db_session)
    await repo.create(User(email="bob@test.com", full_name="Bob", hashed_password="pwd"))

    fetched = await repo.get_by_email("bob@test.com")
    assert fetched is not None
    assert fetched.full_name == "Bob"

    assert await repo.get_by_email("unknown@test.com") is None


@pytest.mark.asyncio
async def test_user_repo_unique_email_constraint(db_session) -> None:
    repo = SqlAlchemyUserRepository(db_session)
    await repo.create(User(email="dup@test.com", full_name="First", hashed_password="pwd"))

    with pytest.raises(Exception):  # IntegrityError from unique constraint
        await repo.create(User(email="dup@test.com", full_name="Second", hashed_password="pwd"))
        await db_session.flush()


@pytest.mark.asyncio
async def test_user_repo_search(db_session) -> None:
    repo = SqlAlchemyUserRepository(db_session)
    await repo.create(User(email="alice@test.com", full_name="Alice Wonderland", hashed_password="p"))
    await repo.create(User(email="bob@test.com", full_name="Bob Builder", hashed_password="p"))
    await repo.create(User(email="charlie@test.com", full_name="Charlie Chaplin", hashed_password="p"))

    results = await repo.search("bob")
    assert len(results) == 1
    assert results[0].email == "bob@test.com"

    results = await repo.search("test")
    assert len(results) == 3


@pytest.mark.asyncio
async def test_user_repo_get_by_ids(db_session) -> None:
    repo = SqlAlchemyUserRepository(db_session)
    u1 = await repo.create(User(email="a@t.com", full_name="A", hashed_password="p"))
    u2 = await repo.create(User(email="b@t.com", full_name="B", hashed_password="p"))
    u3 = await repo.create(User(email="c@t.com", full_name="C", hashed_password="p"))

    result = await repo.get_by_ids([u1.id, u3.id])
    assert len(result) == 2
    assert result[0].email == "a@t.com"

    assert await repo.get_by_ids([]) == []


# ── Project Repository ───────────────────────────


@pytest.mark.asyncio
async def test_project_repo_create_and_get(db_session) -> None:
    user_repo = SqlAlchemyUserRepository(db_session)
    owner = await user_repo.create(User(email="owner@t.com", full_name="Owner", hashed_password="p"))

    proj_repo = SqlAlchemyProjectRepository(db_session)
    project = Project(name="My Project", description="A test project", owner_id=owner.id)

    created = await proj_repo.create(project)
    assert created.id is not None
    assert created.name == "My Project"
    assert created.owner_id == owner.id

    fetched = await proj_repo.get_by_id(created.id)
    assert fetched is not None
    assert fetched.name == "My Project"
    assert fetched.description == "A test project"

    assert await proj_repo.get_by_id(999) is None


@pytest.mark.asyncio
async def test_project_repo_update(db_session) -> None:
    user_repo = SqlAlchemyUserRepository(db_session)
    owner = await user_repo.create(User(email="o@t.com", full_name="O", hashed_password="p"))

    proj_repo = SqlAlchemyProjectRepository(db_session)
    created = await proj_repo.create(Project(name="Old Name", owner_id=owner.id))

    created.name = "Updated Name"
    created.is_archived = True
    updated = await proj_repo.update(created)

    assert updated.name == "Updated Name"
    assert updated.is_archived is True

    fetched = await proj_repo.get_by_id(created.id)
    assert fetched is not None
    assert fetched.name == "Updated Name"
    assert fetched.is_archived is True


@pytest.mark.asyncio
async def test_project_repo_delete(db_session) -> None:
    user_repo = SqlAlchemyUserRepository(db_session)
    owner = await user_repo.create(User(email="o@t.com", full_name="O", hashed_password="p"))

    proj_repo = SqlAlchemyProjectRepository(db_session)
    created = await proj_repo.create(Project(name="To Delete", owner_id=owner.id))

    await proj_repo.delete(created.id)
    assert await proj_repo.get_by_id(created.id) is None


@pytest.mark.asyncio
async def test_project_repo_members(db_session) -> None:
    user_repo = SqlAlchemyUserRepository(db_session)
    owner = await user_repo.create(User(email="owner@t.com", full_name="Owner", hashed_password="p"))
    member1 = await user_repo.create(User(email="m1@t.com", full_name="Member 1", hashed_password="p"))
    member2 = await user_repo.create(User(email="m2@t.com", full_name="Member 2", hashed_password="p"))

    proj_repo = SqlAlchemyProjectRepository(db_session)
    project = await proj_repo.create(Project(name="Team Project", owner_id=owner.id))

    await proj_repo.add_member(project.id, member1.id)
    await proj_repo.add_member(project.id, member2.id)

    members = await proj_repo.get_members(project.id)
    assert len(members) == 2
    emails = {m.user_email for m in members}
    assert emails == {"m1@t.com", "m2@t.com"}

    assert await proj_repo.is_member(project.id, member1.id) is True
    assert await proj_repo.is_member(project.id, 999) is False

    await proj_repo.remove_member(project.id, member2.id)
    members = await proj_repo.get_members(project.id)
    assert len(members) == 1

    # list_for_user: owner sees it, member1 sees it, member2 does not
    owner_projects = await proj_repo.list_for_user(owner.id)
    assert len(owner_projects) == 1

    m1_projects = await proj_repo.list_for_user(member1.id)
    assert len(m1_projects) == 1

    m2_projects = await proj_repo.list_for_user(member2.id)
    assert len(m2_projects) == 0


# ── Task Repository ──────────────────────────────


@pytest.mark.asyncio
async def test_task_repo_create_and_get(db_session) -> None:
    user_repo = SqlAlchemyUserRepository(db_session)
    owner = await user_repo.create(User(email="o@t.com", full_name="O", hashed_password="p"))

    proj_repo = SqlAlchemyProjectRepository(db_session)
    project = await proj_repo.create(Project(name="P", owner_id=owner.id))

    task_repo = SqlAlchemyTaskRepository(db_session)
    task = Task(name="Test Task", project_id=project.id, assigned_user_id=owner.id)

    created = await task_repo.create(task)
    assert created.id is not None
    assert created.name == "Test Task"
    assert created.project_id == project.id
    assert created.assigned_user_id == owner.id
    assert created.status == TaskStatus.PENDING

    fetched = await task_repo.get_by_id(created.id)
    assert fetched is not None
    assert fetched.name == "Test Task"

    assert await task_repo.get_by_id(999) is None


@pytest.mark.asyncio
async def test_task_repo_list_by_project_with_pagination(db_session) -> None:
    user_repo = SqlAlchemyUserRepository(db_session)
    owner = await user_repo.create(User(email="o@t.com", full_name="O", hashed_password="p"))

    proj_repo = SqlAlchemyProjectRepository(db_session)
    project = await proj_repo.create(Project(name="P", owner_id=owner.id))

    task_repo = SqlAlchemyTaskRepository(db_session)
    for i in range(10):
        await task_repo.create(
            Task(name=f"Task {i}", project_id=project.id, assigned_user_id=owner.id)
        )

    # Get all
    all_tasks = await task_repo.list_by_project(project.id, limit=50, offset=0)
    assert len(all_tasks) == 10

    # With pagination
    page = await task_repo.list_by_project(project.id, limit=3, offset=0)
    assert len(page) == 3

    page2 = await task_repo.list_by_project(project.id, limit=3, offset=3)
    assert len(page2) == 3

    # Empty page
    empty = await task_repo.list_by_project(project.id, limit=10, offset=100)
    assert len(empty) == 0

    assert await task_repo.count_by_project(project.id) == 10
    assert await task_repo.count_by_project(999) == 0


@pytest.mark.asyncio
async def test_task_repo_update(db_session) -> None:
    user_repo = SqlAlchemyUserRepository(db_session)
    owner = await user_repo.create(User(email="o@t.com", full_name="O", hashed_password="p"))

    proj_repo = SqlAlchemyProjectRepository(db_session)
    project = await proj_repo.create(Project(name="P", owner_id=owner.id))

    task_repo = SqlAlchemyTaskRepository(db_session)
    created = await task_repo.create(
        Task(name="Original", project_id=project.id, assigned_user_id=owner.id)
    )

    created.name = "Updated"
    created.status = TaskStatus.IN_PROGRESS
    updated = await task_repo.update(created)

    assert updated.name == "Updated"
    assert updated.status == TaskStatus.IN_PROGRESS

    fetched = await task_repo.get_by_id(created.id)
    assert fetched is not None
    assert fetched.name == "Updated"
    assert fetched.status == TaskStatus.IN_PROGRESS


@pytest.mark.asyncio
async def test_task_repo_delete(db_session) -> None:
    user_repo = SqlAlchemyUserRepository(db_session)
    owner = await user_repo.create(User(email="o@t.com", full_name="O", hashed_password="p"))

    proj_repo = SqlAlchemyProjectRepository(db_session)
    project = await proj_repo.create(Project(name="P", owner_id=owner.id))

    task_repo = SqlAlchemyTaskRepository(db_session)
    created = await task_repo.create(
        Task(name="To Delete", project_id=project.id, assigned_user_id=owner.id)
    )

    await task_repo.delete(created.id)
    assert await task_repo.get_by_id(created.id) is None


@pytest.mark.asyncio
async def test_task_repo_cascade_on_project_delete(db_session) -> None:
    """When a project is deleted, all its tasks should be cascade-deleted."""
    user_repo = SqlAlchemyUserRepository(db_session)
    owner = await user_repo.create(User(email="o@t.com", full_name="O", hashed_password="p"))

    proj_repo = SqlAlchemyProjectRepository(db_session)
    project = await proj_repo.create(Project(name="P", owner_id=owner.id))

    task_repo = SqlAlchemyTaskRepository(db_session)
    t1 = await task_repo.create(Task(name="T1", project_id=project.id, assigned_user_id=owner.id))
    t2 = await task_repo.create(Task(name="T2", project_id=project.id, assigned_user_id=owner.id))
    assert t1.id is not None
    assert t2.id is not None

    await proj_repo.delete(project.id)
    await db_session.flush()

    assert await task_repo.get_by_id(t1.id) is None
    assert await task_repo.get_by_id(t2.id) is None


@pytest.mark.asyncio
async def test_task_repo_reassign_by_user(db_session) -> None:
    user_repo = SqlAlchemyUserRepository(db_session)
    owner = await user_repo.create(User(email="o@t.com", full_name="O", hashed_password="p"))
    member = await user_repo.create(User(email="m@t.com", full_name="M", hashed_password="p"))

    proj_repo = SqlAlchemyProjectRepository(db_session)
    project = await proj_repo.create(Project(name="P", owner_id=owner.id))
    await proj_repo.add_member(project.id, member.id)

    task_repo = SqlAlchemyTaskRepository(db_session)
    t1 = await task_repo.create(Task(name="T1", project_id=project.id, assigned_user_id=member.id))
    t2 = await task_repo.create(Task(name="T2", project_id=project.id, assigned_user_id=member.id))
    t3 = await task_repo.create(Task(name="T3", project_id=project.id, assigned_user_id=owner.id))

    await task_repo.reassign_by_user(project.id, member.id, owner.id)

    updated_t1 = await task_repo.get_by_id(t1.id)
    updated_t2 = await task_repo.get_by_id(t2.id)
    updated_t3 = await task_repo.get_by_id(t3.id)

    assert updated_t1 is not None and updated_t1.assigned_user_id == owner.id
    assert updated_t2 is not None and updated_t2.assigned_user_id == owner.id
    # t3 was already owned by owner — should remain unchanged
    assert updated_t3 is not None and updated_t3.assigned_user_id == owner.id
