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
