from flask import jsonify, request
from flask_openapi3 import APIBlueprint

from app.auth import (
    admin_required,
    generate_token,
    login_required,
    self_or_admin_required,
)
from app.database.database import db
from app.models import User
from app.schemas import (
    LoginBody,
    LoginResponse,
    RegisterBody,
    UpdatePasswordBody,
    UpdateUserBody,
    UserListResponse,
    UserResponse,
)
from app.services.user_service import UserService

user_bp = APIBlueprint("users", __name__)


# GET


@user_bp.get("/users", responses={"200": UserListResponse})
@admin_required
def list_users(user_id):
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    result = UserService.list_users(page=page, per_page=per_page)

    return (
        jsonify(
            {
                "data": [
                    {"id": u.id, "name": u.name, "username": u.username, "role": u.role}
                    for u in result["data"]
                ],
                "pagination": result["pagination"],
            }
        ),
        200,
    )


@user_bp.get("/profile", responses={"200": UserResponse})
@login_required
def profile(user_id):
    user = db.session.get(User, user_id)
    return jsonify(
        {"id": user.id, "name": user.name, "username": user.username, "role": user.role}
    )


# POST


@user_bp.post("/register", responses={"201": UserResponse})
def register(body: RegisterBody):
    try:
        user = UserService.create_user(
            name=body.name,
            username=body.username,
            password=body.password,
        )
        return jsonify({"id": user.id, "username": user.username}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@user_bp.post("/login", responses={"200": LoginResponse})
def login(body: LoginBody):
    try:
        user = UserService.authenticate(
            username=body.username,
            password=body.password,
        )
        token = generate_token(user.id)
        return jsonify(
            {
                "id": user.id,
                "username": user.username,
                "role": user.role,
                "token": token,
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 401


@user_bp.post("/users", responses={"201": UserResponse})
@admin_required
def create_user_admin(user_id, body: RegisterBody):
    try:
        user = UserService.create_user(
            name=body.name,
            username=body.username,
            password=body.password,
        )
        return (
            jsonify({"id": user.id, "username": user.username, "role": user.role}),
            201,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# PUT


@user_bp.put("/profile/password")
@login_required
def update_password(user_id, body: UpdatePasswordBody):
    try:
        UserService.update(user_id, {"password": body.password})
        return {"message": "Password updated"}

    except ValueError as e:
        return {"error": str(e)}, 400


@user_bp.put("/users/<int:target_user_id>", responses={"200": UserResponse})
@self_or_admin_required
def update_user(user_id, target_user_id, body: UpdateUserBody):
    data = body.model_dump(exclude_none=True)

    if "role" in data and user_id == target_user_id:
        return {"error": "You can't change your own role"}, 403

    try:
        user = UserService.update(target_user_id, data)
        return {
            "id": user.id,
            "name": user.name,
            "username": user.username,
            "role": user.role,
        }

    except ValueError as e:
        return {"error": str(e)}, 400


# DELETE


@user_bp.delete("/users/<int:target_user_id>")
@admin_required
def delete_user(user_id, target_user_id):
    try:
        UserService.delete(user_id, target_user_id)
        return {"message": "User deleted"}

    except (ValueError, PermissionError) as e:
        return {"error": str(e)}, 400
