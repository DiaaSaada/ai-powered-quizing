"""
My Courses API Router.
Handles user's enrolled courses endpoints.
"""
from fastapi import APIRouter, Depends
from app.models.responses import CourseSummary, MyCoursesResponse
from app.models.user import UserInDB
from app.dependencies.auth import get_current_user
from app.db import crud


router = APIRouter()


@router.get(
    "/",
    response_model=MyCoursesResponse,
    summary="Get my enrolled courses",
    description="Returns all courses the current user is enrolled in."
)
async def get_my_courses(
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get current user's enrolled courses.

    Returns:
        MyCoursesResponse with list of enrolled courses and total count
    """
    # Get user's enrolled course IDs
    enrolled_ids = current_user.enrolled_courses

    if not enrolled_ids:
        return MyCoursesResponse(courses=[], total_count=0)

    # Fetch course details from database
    courses = await crud.get_courses_by_ids(enrolled_ids)

    # Map to CourseSummary format
    course_summaries = []
    for course in courses:
        summary = CourseSummary(
            id=course.get("id", str(course.get("_id", ""))),
            topic=course.get("original_topic", course.get("topic", "")),
            difficulty=course.get("difficulty", "intermediate"),
            complexity_score=course.get("complexity_score"),
            total_chapters=len(course.get("chapters", [])),
            questions_generated=False,  # TODO: implement later
            created_at=course.get("created_at")
        )
        course_summaries.append(summary)

    return MyCoursesResponse(
        courses=course_summaries,
        total_count=len(course_summaries)
    )
