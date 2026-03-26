import bcrypt

from .database.database import db
from .models import User, UserRole


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
        user = User.query.get_or_404(user_id)

        ALLOWED_FIELDS = {"name", "username", "password", "role"}

        try:
            if "username" in data:
                existing_user = User.query.filter_by(username=data["username"]).first()
                if existing_user and existing_user.id != user.id:
                    raise ValueError("Username already in use")

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
    def delete(user_id):
        user = User.query.get_or_404(user_id)
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
