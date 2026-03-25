from flask import Blueprint, jsonify, request

from .auth import generate_token, login_required
from .database import db
from .models import User, UserRole
from .services import UserService

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
@login_required
def list_users(user_id):
    current_user = User.query.get(user_id)

    if current_user.role != UserRole.ADMIN.value:
        return {"error": "Admin access required"}, 403

    users = User.query.all()
    return jsonify(
        [
            {"id": u.id, "name": u.name, "username": u.username, "role": u.role}
            for u in users
        ]
    )


@user_bp.route("/users", methods=["POST"])
@login_required
def create_user_admin(user_id):
    current_user = User.query.get(user_id)

    if current_user.role != UserRole.ADMIN.value:
        return {"error": "Admin access required"}, 403

    data = request.get_json()
    user = UserService.create_user(
        name=data["name"], username=data["username"], password=data["password"]
    )

    return jsonify({"id": user.id, "username": user.username, "role": user.role}), 201


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
    new_password = data.get("password")

    if not new_password or len(new_password) < 8:
        return {"error": "Password too short"}, 400

    user = User.query.get(user_id)
    hashed = UserService.hash_password(new_password)
    user.password = hashed
    db.session.commit()

    return {"message": "Password updated"}


@user_bp.route("/users/<int:target_user_id>", methods=["PUT"])
@login_required
def update_user(user_id, target_user_id):
    current_user = User.query.get(user_id)
    target_user = User.query.get(target_user_id)

    if not target_user:
        return {"error": "User not found"}, 404

    if current_user.role != UserRole.ADMIN.value and user_id != target_user_id:
        return {"error": "Permission denied"}, 403

    data = request.get_json()

    if "name" in data:
        target_user.name = data["name"]

    if "username" in data:
        existing = User.query.filter_by(username=data["username"]).first()
        if existing and existing.id != target_user_id:
            return {"error": "Username already exists"}, 400
        target_user.username = data["username"]

    if "password" in data:
        if len(data["password"]) < 8 or len(data["password"]) > 64:
            return {"error": "Password too short"}, 400
        target_user.password = UserService.hash_password(data["password"])

    if "role" in data:
        if current_user.role != UserRole.ADMIN.value:
            return {"error": "Only admin can change roles"}, 403

        if user_id == target_user_id:
            return {"error": "You can't change your own role"}, 400

        if data["role"] not in [r.value for r in UserRole]:
            return {"error": "Invalid role"}, 400

        target_user.role = data["role"]

    db.session.commit()

    return {
        "id": target_user.id,
        "name": target_user.name,
        "username": target_user.username,
        "role": target_user.role,
    }
