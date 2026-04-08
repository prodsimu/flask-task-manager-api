from flask import jsonify
from flask_openapi3 import APIBlueprint

from app.auth import login_required
from app.schemas import (
    AddMemberBody,
    MemberResponse,
    UpdateMemberRoleBody,
)
from app.services.member_service import MemberService

member_bp = APIBlueprint("members", __name__)


# GET


@member_bp.get(
    "/projects/<int:project_id>/members",
    responses={"200": MemberResponse},
)
@login_required
def list_members(user_id, project_id):
    try:
        members = MemberService.list_members(
            project_id=project_id,
            requester_id=user_id,
        )
        return (
            jsonify(
                [
                    {
                        "id": m.id,
                        "user_id": m.user_id,
                        "username": m.user.username,
                        "role": m.role,
                        "joined_at": m.joined_at.isoformat(),
                    }
                    for m in members
                ]
            ),
            200,
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 404

    except PermissionError as e:
        return jsonify({"error": str(e)}), 403


# POST


@member_bp.post(
    "/projects/<int:project_id>/members",
    responses={"201": MemberResponse},
)
@login_required
def add_member(user_id, project_id, body: AddMemberBody):
    try:
        member = MemberService.add_member(
            project_id=project_id,
            owner_id=user_id,
            username=body.username,
            role=body.role,
        )
        return (
            jsonify(
                {
                    "id": member.id,
                    "user_id": member.user_id,
                    "username": member.user.username,
                    "role": member.role,
                    "joined_at": member.joined_at.isoformat(),
                }
            ),
            201,
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except PermissionError as e:
        return jsonify({"error": str(e)}), 403


# PUT


@member_bp.put(
    "/projects/<int:project_id>/members/<int:target_user_id>",
    responses={"200": MemberResponse},
)
@login_required
def update_member_role(user_id, project_id, target_user_id, body: UpdateMemberRoleBody):
    try:
        member = MemberService.update_member_role(
            project_id=project_id,
            owner_id=user_id,
            target_user_id=target_user_id,
            role=body.role,
        )
        return (
            jsonify(
                {
                    "id": member.id,
                    "user_id": member.user_id,
                    "username": member.user.username,
                    "role": member.role,
                    "joined_at": member.joined_at.isoformat(),
                }
            ),
            200,
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except PermissionError as e:
        return jsonify({"error": str(e)}), 403


# DELETE


@member_bp.delete("/projects/<int:project_id>/members/<int:target_user_id>")
@login_required
def remove_member(user_id, project_id, target_user_id):
    try:
        MemberService.remove_member(
            project_id=project_id,
            owner_id=user_id,
            target_user_id=target_user_id,
        )
        return jsonify({"message": "Member removed"}), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 404

    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
