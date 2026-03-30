from flask import Blueprint, jsonify, request

from app.auth import login_required
from app.services.project_service import ProjectService

project_bp = Blueprint("projects", __name__)


@project_bp.route("/projects", methods=["POST"])
@login_required
def create_project(user_id):
    data = request.get_json()

    try:
        project = ProjectService.create_project(
            owner_id=user_id,
            title=data.get("title"),
            description=data.get("description"),
        )
        return (
            jsonify(
                {
                    "id": project.id,
                    "title": project.title,
                    "description": project.description,
                    "created_at": project.created_at.isoformat(),
                }
            ),
            201,
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@project_bp.route("/projects", methods=["GET"])
@login_required
def list_projects(user_id):
    projects = ProjectService.list_projects(owner_id=user_id)
    return (
        jsonify(
            [
                {
                    "id": p.id,
                    "title": p.title,
                    "description": p.description,
                    "created_at": p.created_at.isoformat(),
                }
                for p in projects
            ]
        ),
        200,
    )


@project_bp.route("/projects/<int:project_id>", methods=["GET"])
@login_required
def get_project(user_id, project_id):
    try:
        project = ProjectService.get_project(project_id=project_id, owner_id=user_id)
        return (
            jsonify(
                {
                    "id": project.id,
                    "title": project.title,
                    "description": project.description,
                    "created_at": project.created_at.isoformat(),
                }
            ),
            200,
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 404

    except PermissionError as e:
        return jsonify({"error": str(e)}), 403


@project_bp.route("/projects/<int:project_id>", methods=["PUT"])
@login_required
def update_project(user_id, project_id):
    data = request.get_json()

    try:
        project = ProjectService.update_project(
            project_id=project_id,
            owner_id=user_id,
            data=data,
        )
        return (
            jsonify(
                {
                    "id": project.id,
                    "title": project.title,
                    "description": project.description,
                    "created_at": project.created_at.isoformat(),
                }
            ),
            200,
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
