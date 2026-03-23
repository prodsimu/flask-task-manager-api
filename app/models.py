from enum import Enum

from .database import db


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
