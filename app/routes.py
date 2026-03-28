from flask import Blueprint, jsonify, request

from app.auth import (
    admin_required,
    generate_token,
    login_required,
    self_or_admin_required,
)
from app.models import User
from app.services import UserService

user_bp = Blueprint("users", __name__)


@user_bp.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        user = UserService.create_user(
            name=data["name"],
            username=data["username"],
            password=data["password"],
        )
        return jsonify({"id": user.id, "username": user.username}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@user_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        user = UserService.authenticate(
            username=data["username"], password=data["password"]
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


@user_bp.route("/users", methods=["GET"])
@admin_required
def list_users(user_id):
    users = UserService.list_users()
    return (
        jsonify(
            [
                {"id": u.id, "name": u.name, "username": u.username, "role": u.role}
                for u in users
            ]
        ),
        200,
    )


@user_bp.route("/users", methods=["POST"])
@admin_required
def create_user_admin(user_id):
    data = request.get_json()
    try:
        user = UserService.create_user(
            name=data["name"],
            username=data["username"],
            password=data["password"],
        )
        return (
            jsonify({"id": user.id, "username": user.username, "role": user.role}),
            201,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@user_bp.route("/profile", methods=["GET"])
@login_required
def profile(user_id):
    user = User.query.get(user_id)
    return jsonify(
        {"id": user.id, "name": user.name, "username": user.username, "role": user.role}
    )


@user_bp.route("/profile/password", methods=["PUT"])
@login_required
def update_password(user_id):
    data = request.get_json()

    if not data.get("password"):
        return {"error": "Password is required"}, 400

    try:
        UserService.update(user_id, {"password": data["password"]})
        return {"message": "Password updated"}

    except ValueError as e:
        return {"error": str(e)}, 400


@user_bp.route("/users/<int:target_user_id>", methods=["PUT"])
@self_or_admin_required
def update_user(user_id, target_user_id):
    data = request.get_json()

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


@user_bp.route("/users/<int:target_user_id>", methods=["DELETE"])
@admin_required
def delete_user(user_id, target_user_id):
    try:
        UserService.delete(user_id, target_user_id)
        return {"message": "User deleted"}

    except (ValueError, PermissionError) as e:
        return {"error": str(e)}, 400
