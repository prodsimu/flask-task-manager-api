from app.database.database import db
from app.models import MemberRole, Project, ProjectMember


class ProjectService:

    @staticmethod
    def _get_member(project_id: int, user_id: int):
        return ProjectMember.query.filter_by(
            project_id=project_id,
            user_id=user_id,
        ).first()

    # CREATE

    @staticmethod
    def create_project(owner_id: int, title: str, description: str = None):
        if not title or len(title.strip()) == 0:
            raise ValueError("Title is required.")

        if len(title) > 100:
            raise ValueError("Title must be at most 100 characters.")

        if description and len(description) > 255:
            raise ValueError("Description must be at most 255 characters.")

        project = Project(
            title=title.strip(),
            description=description,
            owner_id=owner_id,
        )

        db.session.add(project)
        db.session.commit()

        return project

    # READ

    @staticmethod
    def list_projects(owner_id: int):
        return Project.query.filter_by(owner_id=owner_id).all()

    @staticmethod
    def get_project(project_id: int, owner_id: int):
        project = db.session.get(Project, project_id)

        if not project:
            raise ValueError("Project not found.")

        if project.owner_id != owner_id:
            raise PermissionError("Access denied.")

        return project

    # UPDATE

    @staticmethod
    def update_project(project_id: int, owner_id: int, data: dict):
        project = ProjectService.get_project(project_id, owner_id)

        if "title" in data:
            if not data["title"] or len(data["title"].strip()) == 0:
                raise ValueError("Title is required.")
            if len(data["title"]) > 100:
                raise ValueError("Title must be at most 100 characters.")
            project.title = data["title"].strip()

        if "description" in data:
            if data["description"] and len(data["description"]) > 255:
                raise ValueError("Description must be at most 255 characters.")
            project.description = data["description"]

        db.session.commit()

        return project

    # DELETE

    @staticmethod
    def delete_project(project_id: int, owner_id: int):
        project = ProjectService.get_project(project_id, owner_id)

        db.session.delete(project)
        db.session.commit()
