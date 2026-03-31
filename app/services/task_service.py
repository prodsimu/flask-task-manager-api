from app.database.database import db
from app.models import Project, Task, TaskPriority, TaskStatus


class TaskService:

    # CREATE

    @staticmethod
    def create_task(
        project_id: int,
        owner_id: int,
        title: str,
        description: str = None,
        priority: str = TaskPriority.MEDIUM.value,
    ):
        project = db.session.get(Project, project_id)

        if not project:
            raise ValueError("Project not found.")

        if project.owner_id != owner_id:
            raise PermissionError("Access denied.")

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
        db.session.commit()

        return task

    # READ

    @staticmethod
    def list_tasks(
        project_id: int, owner_id: int, status: str = None, priority: str = None
    ):
        project = db.session.get(Project, project_id)

        if not project:
            raise ValueError("Project not found.")

        if project.owner_id != owner_id:
            raise PermissionError("Access denied.")

        if status and status not in [s.value for s in TaskStatus]:
            raise ValueError("Invalid status.")

        if priority and priority not in [p.value for p in TaskPriority]:
            raise ValueError("Invalid priority.")

        query = Task.query.filter_by(project_id=project_id)

        if status:
            query = query.filter_by(status=status)

        if priority:
            query = query.filter_by(priority=priority)

        return query.order_by(Task.status, Task.position).all()

    @staticmethod
    def get_task(project_id: int, task_id: int, owner_id: int):
        project = db.session.get(Project, project_id)

        if not project:
            raise ValueError("Project not found.")

        if project.owner_id != owner_id:
            raise PermissionError("Access denied.")

        task = db.session.get(Task, task_id)

        if not task or task.project_id != project_id:
            raise ValueError("Task not found.")

        return task

    # UPDATE

    @staticmethod
    def update_task(project_id: int, task_id: int, owner_id: int, data: dict):
        task = TaskService.get_task(project_id, task_id, owner_id)

        if "title" in data:
            if not data["title"] or len(data["title"].strip()) == 0:
                raise ValueError("Title is required.")
            if len(data["title"]) > 100:
                raise ValueError("Title must be at most 100 characters.")
            task.title = data["title"].strip()

        if "description" in data:
            if data["description"] and len(data["description"]) > 255:
                raise ValueError("Description must be at most 255 characters.")
            task.description = data["description"]

        if "status" in data:
            if data["status"] not in [s.value for s in TaskStatus]:
                raise ValueError("Invalid status.")
            task.status = data["status"]

        if "priority" in data:
            if data["priority"] not in [p.value for p in TaskPriority]:
                raise ValueError("Invalid priority.")
            task.priority = data["priority"]

        db.session.commit()

        return task

    # DELETE

    @staticmethod
    def delete_task(project_id: int, task_id: int, owner_id: int):
        task = TaskService.get_task(project_id, task_id, owner_id)

        db.session.delete(task)
        db.session.commit()

    # MOVE

    @staticmethod
    def move_task(
        project_id: int, task_id: int, owner_id: int, new_status: str, new_position: int
    ):
        task = TaskService.get_task(project_id, task_id, owner_id)

        if new_status not in [s.value for s in TaskStatus]:
            raise ValueError("Invalid status.")

        if new_position < 0:
            raise ValueError("Position must be a positive number.")

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

        db.session.commit()

        return task
