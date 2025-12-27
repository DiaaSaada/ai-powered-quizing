"""
Database module for MongoDB integration.
"""
from app.db.connection import MongoDB, get_database
from app.db import crud
from app.db.models import CourseDocument, QuestionDocument, UserProgressDocument

__all__ = [
    "MongoDB",
    "get_database",
    "crud",
    "CourseDocument",
    "QuestionDocument",
    "UserProgressDocument",
]
