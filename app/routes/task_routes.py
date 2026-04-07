from flask import jsonify, request
from flask_openapi3 import APIBlueprint

from app.auth import login_required
from app.schemas import (
    CreateTaskBody,
    MoveTaskBody,
    TaskHistoryResponse,
    TaskListResponse,
    TaskResponse,
    UpdateTaskBody,
)
from app.services.task_service import TaskService

task_bp = APIBlueprint("tasks", __name__)


# GET


@task_bp.get("/projects/<int:project_id>/tasks", responses={"200": TaskListResponse})
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


@task_bp.get(
    "/projects/<int:project_id>/tasks/<int:task_id>", responses={"200": TaskResponse}
)
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


@task_bp.get(
    "/projects/<int:project_id>/tasks/<int:task_id>/history",
    responses={"200": TaskHistoryResponse},
)
@login_required
def get_task_history(user_id, project_id, task_id):
    try:
        history = TaskService.get_task_history(
            project_id=project_id,
            task_id=task_id,
            user_id=user_id,
        )
        return (
            jsonify(
                [
                    {
                        "id": h.id,
                        "field": h.field,
                        "old_value": h.old_value,
                        "new_value": h.new_value,
                        "changed_by": h.changed_by,
                        "changed_at": h.changed_at.isoformat(),
                    }
                    for h in history
                ]
            ),
            200,
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 404

    except PermissionError as e:
        return jsonify({"error": str(e)}), 403


# POST


@task_bp.post("/projects/<int:project_id>/tasks", responses={"201": TaskResponse})
@login_required
def create_task(user_id, project_id, body: CreateTaskBody):
    try:
        task = TaskService.create_task(
            project_id=project_id,
            user_id=user_id,
            title=body.title,
            description=body.description,
            priority=body.priority,
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


@task_bp.put(
    "/projects/<int:project_id>/tasks/<int:task_id>",
    responses={"200": TaskResponse},
)
@login_required
def update_task(user_id, project_id, task_id, body: UpdateTaskBody):
    data = body.model_dump(exclude_none=True)

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


@task_bp.patch(
    "/projects/<int:project_id>/tasks/<int:task_id>/move",
    responses={"200": TaskResponse},
)
@login_required
def move_task(user_id, project_id, task_id, body: MoveTaskBody):
    try:
        task = TaskService.move_task(
            project_id=project_id,
            task_id=task_id,
            user_id=user_id,
            new_status=body.status,
            new_position=body.position,
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


@task_bp.delete("/projects/<int:project_id>/tasks/<int:task_id>")
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
