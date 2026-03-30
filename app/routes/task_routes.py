from flask import Blueprint, jsonify, request

from app.auth import login_required
from app.services.task_service import TaskService

task_bp = Blueprint("tasks", __name__)


@task_bp.route("/projects/<int:project_id>/tasks", methods=["POST"])
@login_required
def create_task(user_id, project_id):
    data = request.get_json()

    try:
        task = TaskService.create_task(
            project_id=project_id,
            owner_id=user_id,
            title=data.get("title"),
            description=data.get("description"),
            priority=data.get("priority", "medium"),
        )
        return (
            jsonify(
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "status": task.status,
                    "priority": task.priority,
                    "created_at": task.created_at.isoformat(),
                }
            ),
            201,
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except PermissionError as e:
        return jsonify({"error": str(e)}), 403


@task_bp.route("/projects/<int:project_id>/tasks", methods=["GET"])
@login_required
def list_tasks(user_id, project_id):
    try:
        tasks = TaskService.list_tasks(project_id=project_id, owner_id=user_id)
        return (
            jsonify(
                [
                    {
                        "id": t.id,
                        "title": t.title,
                        "description": t.description,
                        "status": t.status,
                        "priority": t.priority,
                        "created_at": t.created_at.isoformat(),
                    }
                    for t in tasks
                ]
            ),
            200,
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 404

    except PermissionError as e:
        return jsonify({"error": str(e)}), 403


@task_bp.route("/projects/<int:project_id>/tasks/<int:task_id>", methods=["GET"])
@login_required
def get_task(user_id, project_id, task_id):
    try:
        task = TaskService.get_task(
            project_id=project_id,
            task_id=task_id,
            owner_id=user_id,
        )
        return (
            jsonify(
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "status": task.status,
                    "priority": task.priority,
                    "created_at": task.created_at.isoformat(),
                }
            ),
            200,
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 404

    except PermissionError as e:
        return jsonify({"error": str(e)}), 403


@task_bp.route("/projects/<int:project_id>/tasks/<int:task_id>", methods=["PUT"])
@login_required
def update_task(user_id, project_id, task_id):
    data = request.get_json()

    try:
        task = TaskService.update_task(
            project_id=project_id,
            task_id=task_id,
            owner_id=user_id,
            data=data,
        )
        return (
            jsonify(
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "status": task.status,
                    "priority": task.priority,
                    "created_at": task.created_at.isoformat(),
                }
            ),
            200,
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
