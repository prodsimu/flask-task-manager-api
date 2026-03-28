import bcrypt

from app.database.database import db
from app.models import User, UserRole


class UserService:

    # HASH

    @staticmethod
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode(), salt)
        return hashed.decode()

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode(), hashed.encode())

    # CREATE

    @staticmethod
    def create_user(name: str, username: str, password: str):
        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            raise ValueError("Username already exists.")

        if not 8 <= len(password) <= 64:
            raise ValueError("Password must be between 8 and 64 characters.")

        hashed_password = UserService.hash_password(password)

        user = User(
            name=name,
            username=username,
            password=hashed_password,
            role=UserRole.USER.value,
        )

        db.session.add(user)
        db.session.commit()

        return user

    # READ

    @staticmethod
    def list_users():
        return User.query.all()

    # UPDATE

    @staticmethod
    def update(user_id, data):
        user = db.session.get(User, user_id)

        if not user:
            raise ValueError("User not found.")

        ALLOWED_FIELDS = {"name", "username", "password", "role"}

        if "username" in data:
            existing_user = User.query.filter_by(username=data["username"]).first()
            if existing_user and existing_user.id != user.id:
                raise ValueError("Username already in use.")

        if "password" in data:
            if not 8 <= len(data["password"]) <= 64:
                raise ValueError("Password must be between 8 and 64 characters.")

        if "role" in data:
            if data["role"] not in [r.value for r in UserRole]:
                raise ValueError("Invalid role.")

        try:
            for field in ALLOWED_FIELDS:
                if field in data:
                    value = data[field]
                    if field == "password":
                        value = UserService.hash_password(value)
                    setattr(user, field, value)

            db.session.commit()
            return user

        except Exception:
            db.session.rollback()
            raise

    # DELETE

    @staticmethod
    def delete(current_user_id, target_user_id):
        user = db.session.get(User, target_user_id)

        if not user:
            raise ValueError("User not found.")

        if current_user_id == user.id:
            raise PermissionError("You can't delete your own user.")

        db.session.delete(user)
        db.session.commit()

    # AUTH

    @staticmethod
    def authenticate(username: str, password: str):
        user = User.query.filter_by(username=username).first()

        if not user:
            raise ValueError("Invalid credentials.")

        if not UserService.verify_password(password, user.password):
            raise ValueError("Invalid credentials.")

        return user
