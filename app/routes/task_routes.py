from flask import Blueprint, jsonify, request

from app.auth import login_required
from app.services.task_service import TaskService

task_bp = Blueprint("tasks", __name__)


# GET


@task_bp.route("/projects/<int:project_id>/tasks", methods=["GET"])
@login_required
def list_tasks(user_id, project_id):
    status = request.args.get("status")
    priority = request.args.get("priority")
    search = request.args.get("search")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    try:
        result = TaskService.list_tasks(
            project_id=project_id,
            user_id=user_id,
            status=status,
            priority=priority,
            search=search,
            page=page,
            per_page=per_page,
        )
        return (
            jsonify(
                {
                    "data": [
                        {
                            "id": t.id,
                            "title": t.title,
                            "description": t.description,
                            "status": t.status,
                            "priority": t.priority,
                            "position": t.position,
                            "created_at": t.created_at.isoformat(),
                        }
                        for t in result["data"]
                    ],
                    "pagination": result["pagination"],
                }
            ),
            200,
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except PermissionError as e:
        return jsonify({"error": str(e)}), 403


@task_bp.route("/projects/<int:project_id>/tasks/<int:task_id>", methods=["GET"])
@login_required
def get_task(user_id, project_id, task_id):
    try:
        task = TaskService.get_task(
            project_id=project_id,
            task_id=task_id,
            user_id=user_id,
        )
        return (
            jsonify(
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "status": task.status,
                    "priority": task.priority,
                    "position": task.position,
                    "created_at": task.created_at.isoformat(),
                }
            ),
            200,
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 404

    except PermissionError as e:
        return jsonify({"error": str(e)}), 403


# POST


@task_bp.route("/projects/<int:project_id>/tasks", methods=["POST"])
@login_required
def create_task(user_id, project_id):
    data = request.get_json()

    try:
        task = TaskService.create_task(
            project_id=project_id,
            user_id=user_id,
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
                    "position": task.position,
                    "created_at": task.created_at.isoformat(),
                }
            ),
            201,
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except PermissionError as e:
        return jsonify({"error": str(e)}), 403


# PUT


@task_bp.route("/projects/<int:project_id>/tasks/<int:task_id>", methods=["PUT"])
@login_required
def update_task(user_id, project_id, task_id):
    data = request.get_json()

    try:
        task = TaskService.update_task(
            project_id=project_id,
            task_id=task_id,
            user_id=user_id,
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
                    "position": task.position,
                    "created_at": task.created_at.isoformat(),
                }
            ),
            200,
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except PermissionError as e:
        return jsonify({"error": str(e)}), 403


# PATCH


@task_bp.route("/projects/<int:project_id>/tasks/<int:task_id>/move", methods=["PATCH"])
@login_required
def move_task(user_id, project_id, task_id):
    data = request.get_json()

    try:
        task = TaskService.move_task(
            project_id=project_id,
            task_id=task_id,
            user_id=user_id,
            new_status=data.get("status"),
            new_position=data.get("position", 0),
        )
        return (
            jsonify(
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "status": task.status,
                    "priority": task.priority,
                    "position": task.position,
                    "created_at": task.created_at.isoformat(),
                }
            ),
            200,
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except PermissionError as e:
        return jsonify({"error": str(e)}), 403


# DELETE


@task_bp.route("/projects/<int:project_id>/tasks/<int:task_id>", methods=["DELETE"])
@login_required
def delete_task(user_id, project_id, task_id):
    try:
        TaskService.delete_task(
            project_id=project_id,
            task_id=task_id,
            user_id=user_id,
        )
        return jsonify({"message": "Task deleted"}), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 404

    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
