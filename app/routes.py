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


# AUTH


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


# GET USERS


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


# POST USERS


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
