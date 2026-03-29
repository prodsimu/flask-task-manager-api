import os

from flask import Flask

from app.database.database import db
from app.database.seeds import seed_admin


def create_app():
    app = Flask(__name__)

    secret_key = os.environ.get("SECRET_KEY")
    if not secret_key:
        raise RuntimeError("SECRET_KEY environment variable is not set.")

    app.config["SECRET_KEY"] = secret_key
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    from app.models import User
    from app.routes import user_bp

    app.register_blueprint(user_bp)

    with app.app_context():
        db.create_all()
        created = seed_admin()

        if created:
            print("Admin created: username=admin | password=admin123")

    return app
