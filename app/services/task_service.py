from app.database.database import db
from app.models import (
    MemberRole,
    Project,
    ProjectMember,
    Task,
    TaskHistory,
    TaskPriority,
    TaskStatus,
)


class TaskService:

    @staticmethod
    def _check_access(project_id: int, user_id: int, require_editor: bool = False):
        project = db.session.get(Project, project_id)

        if not project:
            raise ValueError("Project not found.")

        is_owner = project.owner_id == user_id

        if is_owner:
            return project

        member = ProjectMember.query.filter_by(
            project_id=project_id,
            user_id=user_id,
        ).first()

        if not member:
            raise PermissionError("Access denied.")

        if require_editor and member.role != MemberRole.EDITOR.value:
            raise PermissionError("Editor access required.")

        return project

    @staticmethod
    def _record_history(task_id: int, user_id: int, changes: dict):
        for field, (old_value, new_value) in changes.items():
            entry = TaskHistory(
                task_id=task_id,
                changed_by=user_id,
                field=field,
                old_value=str(old_value) if old_value is not None else None,
                new_value=str(new_value) if new_value is not None else None,
            )
            db.session.add(entry)

    # CREATE

    @staticmethod
    def create_task(
        project_id: int,
        user_id: int,
        title: str,
        description: str = None,
        priority: str = TaskPriority.MEDIUM.value,
    ):
        TaskService._check_access(project_id, user_id, require_editor=True)

        if not title or len(title.strip()) == 0:
            raise ValueError("Title is required.")

        if len(title) > 100:
            raise ValueError("Title must be at most 100 characters.")

        if description and len(description) > 255:
            raise ValueError("Description must be at most 255 characters.")

        if priority not in [p.value for p in TaskPriority]:
            raise ValueError("Invalid priority.")

        last_task = (
            Task.query.filter_by(project_id=project_id, status=TaskStatus.TODO.value)
            .order_by(Task.position.desc())
            .first()
        )
        position = (last_task.position + 1) if last_task else 0

        task = Task(
            title=title.strip(),
            description=description,
            priority=priority,
            position=position,
            project_id=project_id,
        )

        db.session.add(task)
        db.session.flush()

        TaskService._record_history(
            task.id,
            user_id,
            {
                "title": (None, task.title),
                "status": (None, task.status),
                "priority": (None, task.priority),
            },
        )

        db.session.commit()

        return task

    # READ

    @staticmethod
    def list_tasks(
        project_id: int,
        user_id: int,
        status: str = None,
        priority: str = None,
        search: str = None,
        page: int = 1,
        per_page: int = 20,
    ):
        TaskService._check_access(project_id, user_id)

        if status and status not in [s.value for s in TaskStatus]:
            raise ValueError("Invalid status.")

        if priority and priority not in [p.value for p in TaskPriority]:
            raise ValueError("Invalid priority.")

        query = Task.query.filter_by(project_id=project_id)

        if status:
            query = query.filter_by(status=status)

        if priority:
            query = query.filter_by(priority=priority)

        if search:
            query = query.filter(Task.title.ilike(f"%{search}%"))

        pagination = query.order_by(Task.status, Task.position).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return {
            "data": pagination.items,
            "pagination": {
                "page": pagination.page,
                "per_page": pagination.per_page,
                "total": pagination.total,
                "pages": pagination.pages,
            },
        }

    @staticmethod
    def get_task(project_id: int, task_id: int, user_id: int):
        TaskService._check_access(project_id, user_id)

        task = db.session.get(Task, task_id)

        if not task or task.project_id != project_id:
            raise ValueError("Task not found.")

        return task

    @staticmethod
    def get_task_history(project_id: int, task_id: int, user_id: int):
        TaskService._check_access(project_id, user_id)

        task = db.session.get(Task, task_id)

        if not task or task.project_id != project_id:
            raise ValueError("Task not found.")

        return (
            TaskHistory.query.filter_by(task_id=task_id)
            .order_by(TaskHistory.changed_at.desc())
            .all()
        )

    # UPDATE

    @staticmethod
    def update_task(project_id: int, task_id: int, user_id: int, data: dict):
        TaskService._check_access(project_id, user_id, require_editor=True)

        task = db.session.get(Task, task_id)

        if not task or task.project_id != project_id:
            raise ValueError("Task not found.")

        changes = {}

        if "title" in data:
            if not data["title"] or len(data["title"].strip()) == 0:
                raise ValueError("Title is required.")
            if len(data["title"]) > 100:
                raise ValueError("Title must be at most 100 characters.")
            changes["title"] = (task.title, data["title"].strip())
            task.title = data["title"].strip()

        if "description" in data:
            if data["description"] and len(data["description"]) > 255:
                raise ValueError("Description must be at most 255 characters.")
            changes["description"] = (task.description, data["description"])
            task.description = data["description"]

        if "status" in data:
            if data["status"] not in [s.value for s in TaskStatus]:
                raise ValueError("Invalid status.")
            changes["status"] = (task.status, data["status"])
            task.status = data["status"]

        if "priority" in data:
            if data["priority"] not in [p.value for p in TaskPriority]:
                raise ValueError("Invalid priority.")
            changes["priority"] = (task.priority, data["priority"])
            task.priority = data["priority"]

        if changes:
            TaskService._record_history(task.id, user_id, changes)

        db.session.commit()

        return task

    # MOVE

    @staticmethod
    def move_task(
        project_id: int, task_id: int, user_id: int, new_status: str, new_position: int
    ):
        TaskService._check_access(project_id, user_id, require_editor=True)

        task = db.session.get(Task, task_id)

        if not task or task.project_id != project_id:
            raise ValueError("Task not found.")

        if new_status not in [s.value for s in TaskStatus]:
            raise ValueError("Invalid status.")

        if new_position < 0:
            raise ValueError("Position must be a positive number.")

        changes = {}

        if task.status != new_status:
            changes["status"] = (task.status, new_status)

        if task.position != new_position:
            changes["position"] = (task.position, new_position)

        column_tasks = (
            Task.query.filter_by(project_id=project_id, status=new_status)
            .filter(Task.id != task_id)
            .order_by(Task.position)
            .all()
        )

        column_tasks.insert(new_position, task)

        for index, t in enumerate(column_tasks):
            t.position = index

        task.status = new_status

        if changes:
            TaskService._record_history(task.id, user_id, changes)

        db.session.commit()

        return task

    # DELETE

    @staticmethod
    def delete_task(project_id: int, task_id: int, user_id: int):
        TaskService._check_access(project_id, user_id, require_editor=True)

        task = db.session.get(Task, task_id)

        if not task or task.project_id != project_id:
            raise ValueError("Task not found.")

        db.session.delete(task)
        db.session.commit()
