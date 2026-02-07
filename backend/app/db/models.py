"""
MongoDB document models.
These define the structure of documents stored in MongoDB collections.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class ChapterDocument(BaseModel):
    """Chapter subdocument embedded in Course."""
    number: int
    title: str
    summary: str
    key_concepts: List[str] = []
    difficulty: str


class CourseDocument(BaseModel):
    """
    Course document model for MongoDB.
    Stores generated courses for caching.
    """
    slug: str = Field(..., description="Unique course slug (e.g., 'python-programming-beginner-a7x3k2')")
    topic: str = Field(..., description="Normalized topic name (lowercase)")
    original_topic: str = Field(..., description="Original topic as provided by user")
    difficulty: str = Field(..., description="Difficulty level: beginner, intermediate, advanced")
    chapters: List[ChapterDocument] = Field(default_factory=list)
    provider: str = Field(..., description="AI provider used to generate")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "slug": "project-management-beginner-a7x3k2",
                "topic": "project management",
                "original_topic": "Project Management",
                "difficulty": "beginner",
                "chapters": [
                    {
                        "number": 1,
                        "title": "Introduction",
                        "summary": "Learn the basics",
                        "key_concepts": ["Planning", "Execution"],
                        "difficulty": "beginner"
                    }
                ],
                "provider": "claude",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }


class QuestionDocument(BaseModel):
    """
    Question document model for MongoDB.
    Stores generated questions for chapters.
    """
    course_topic: str = Field(..., description="Normalized topic of the parent course")
    difficulty: str = Field(..., description="Course difficulty level")
    chapter_number: int = Field(..., description="Chapter number these questions belong to")
    chapter_title: str = Field(..., description="Chapter title")
    mcq: List[Dict[str, Any]] = Field(default_factory=list, description="Multiple choice questions")
    true_false: List[Dict[str, Any]] = Field(default_factory=list, description="True/False questions")
    provider: str = Field(..., description="AI provider used to generate")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "course_topic": "project management",
                "difficulty": "beginner",
                "chapter_number": 1,
                "chapter_title": "Introduction to Project Management",
                "mcq": [
                    {
                        "id": "mcq_1",
                        "question": "What is a project?",
                        "options": ["A) Temporary endeavor", "B) Ongoing operation"],
                        "correct_answer": "A",
                        "explanation": "A project is temporary."
                    }
                ],
                "true_false": [
                    {
                        "id": "tf_1",
                        "question": "Projects have a defined end.",
                        "correct_answer": True,
                        "explanation": "True, projects are temporary."
                    }
                ],
                "provider": "claude"
            }
        }


class UserProgressDocument(BaseModel):
    """
    User progress document model for MongoDB.
    Tracks user answers and scores per course/chapter.
    """
    user_id: str = Field(..., description="User identifier")
    course_topic: str = Field(..., description="Normalized topic of the course")
    difficulty: str = Field(..., description="Course difficulty level")
    chapter_number: int = Field(..., description="Chapter number")
    answers: List[Dict[str, Any]] = Field(default_factory=list, description="User's answers")
    score: float = Field(default=0.0, description="Score for this chapter (0.0-1.0)")
    total_questions: int = Field(default=0, description="Total questions attempted")
    correct_answers: int = Field(default=0, description="Number of correct answers")
    completed: bool = Field(default=False, description="Whether chapter is completed")
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "course_topic": "project management",
                "difficulty": "beginner",
                "chapter_number": 1,
                "answers": [
                    {"question_id": "mcq_1", "user_answer": "A", "is_correct": True}
                ],
                "score": 0.85,
                "total_questions": 8,
                "correct_answers": 7,
                "completed": True
            }
        }
