"""
API Response models for consistent frontend format.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class CourseSummary(BaseModel):
    """Summary model for course card display."""
    id: str = Field(..., description="Course MongoDB ID")
    topic: str = Field(..., description="Course topic")
    difficulty: str = Field(..., description="Difficulty level")
    complexity_score: Optional[int] = Field(default=None, description="Topic complexity score (1-10)")
    total_chapters: int = Field(..., description="Number of chapters")
    questions_generated: bool = Field(default=False, description="Whether questions have been generated")
    created_at: datetime = Field(..., description="When the course was created")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "abc-123",
                "topic": "AWS Solutions Architect",
                "difficulty": "advanced",
                "complexity_score": 8,
                "total_chapters": 6,
                "questions_generated": False,
                "created_at": "2024-01-15T10:30:00Z"
            }
        }


class MyCoursesResponse(BaseModel):
    """Response for /my-courses endpoint."""
    courses: List[CourseSummary] = Field(..., description="List of enrolled courses")
    total_count: int = Field(..., description="Total number of enrolled courses")

    class Config:
        json_schema_extra = {
            "example": {
                "courses": [
                    {
                        "id": "abc-123",
                        "topic": "AWS Solutions Architect",
                        "difficulty": "advanced",
                        "complexity_score": 8,
                        "total_chapters": 6,
                        "questions_generated": False,
                        "created_at": "2024-01-15T10:30:00Z"
                    }
                ],
                "total_count": 1
            }
        }
