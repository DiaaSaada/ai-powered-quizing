"""
Courses API Router
Handles all course-related endpoints with configurable AI providers.
"""
from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional
from app.models.course import (
    GenerateCourseRequest,
    GenerateCourseResponse,
    Chapter,
    CourseConfig
)
from app.models.validation import TopicValidationResult
from app.services.ai_service_factory import AIServiceFactory
from app.services.topic_validator import get_topic_validator
from app.services.course_configurator import get_course_configurator
from app.config import UseCase
from app.db import crud

# Create router
router = APIRouter()


@router.post(
    "/generate",
    response_model=GenerateCourseResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate course chapters from a topic",
    description="Takes a topic and difficulty as input, validates the topic, configures optimal course structure, and generates chapters using AI."
)
async def generate_course(
    request: GenerateCourseRequest,
    provider: Optional[str] = Query(
        None,
        description="AI provider to use: 'claude', 'openai', or 'mock'. If not specified, uses default from config."
    )
):
    """
    Generate a course with chapters based on the provided topic and difficulty.

    Flow:
    1. Validate topic using TopicValidator (unless skip_validation=True)
    2. Get optimal course configuration from CourseConfigurator
    3. Check cache for existing course
    4. Generate chapters using AI with the configuration
    5. Save to cache and return enriched response

    Args:
        request: Request body containing topic, difficulty, and skip_validation flag
        provider: Optional AI provider override (claude/openai/mock)

    Returns:
        GenerateCourseResponse with chapters and study time estimates

    Raises:
        HTTPException 400: If topic is rejected (too broad, inappropriate, etc.)
        HTTPException 422: If topic needs clarification
        HTTPException 500: If generation fails
    """
    try:
        # Validate topic is not empty
        if not request.topic or not request.topic.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Topic cannot be empty"
            )

        complexity_score = None

        # Step 1: Validate topic (unless skipped for testing)
        if not request.skip_validation:
            validator = get_topic_validator()
            validation_result = await validator.validate(request.topic)

            if validation_result.status == "rejected":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "topic_rejected",
                        "reason": validation_result.reason,
                        "message": validation_result.message,
                        "suggestions": validation_result.suggestions
                    }
                )

            if validation_result.status == "needs_clarification":
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={
                        "error": "topic_needs_clarification",
                        "reason": validation_result.reason,
                        "message": validation_result.message,
                        "suggestions": validation_result.suggestions
                    }
                )

            # Extract complexity score from validation
            if validation_result.complexity:
                complexity_score = validation_result.complexity.score

        # Step 2: Get optimal course configuration
        configurator = get_course_configurator()
        # Use complexity score from validation, default to 5 if not available
        config = configurator.get_config(
            complexity_score=complexity_score or 5,
            difficulty=request.difficulty
        )

        # Step 3: Check cache first
        cached_course = await crud.get_course_by_topic(request.topic, request.difficulty)
        if cached_course:
            # Return cached course with enriched response
            chapters = [Chapter(**ch) for ch in cached_course["chapters"]]
            return GenerateCourseResponse(
                topic=cached_course["original_topic"],
                difficulty=request.difficulty,
                total_chapters=len(chapters),
                estimated_study_hours=config.estimated_study_hours,
                time_per_chapter_minutes=config.time_per_chapter_minutes,
                complexity_score=complexity_score,
                chapters=chapters,
                config=config,
                message=f"Retrieved {len(chapters)} {request.difficulty}-level chapters for '{request.topic}' from cache"
            )

        # Step 4: Get the appropriate AI service and generate chapters
        ai_service = AIServiceFactory.get_service(
            use_case=UseCase.CHAPTER_GENERATION,
            provider_override=provider
        )

        # Generate chapters with configuration
        chapters = await ai_service.generate_chapters(
            topic=request.topic,
            config=config
        )

        # Determine which provider was actually used
        actual_provider = ai_service.get_provider_name()

        # Step 5: Save to cache (non-blocking, don't fail if DB is down)
        await crud.save_course(
            topic=request.topic,
            difficulty=request.difficulty,
            chapters=chapters,
            provider=actual_provider
        )

        # Create enriched response
        response = GenerateCourseResponse(
            topic=request.topic,
            difficulty=request.difficulty,
            total_chapters=len(chapters),
            estimated_study_hours=config.estimated_study_hours,
            time_per_chapter_minutes=config.time_per_chapter_minutes,
            complexity_score=complexity_score,
            chapters=chapters,
            config=config,
            message=f"Generated {len(chapters)} {request.difficulty}-level chapters for '{request.topic}' using {actual_provider}"
        )

        return response

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except ValueError as e:
        # Handle configuration errors (e.g., missing API keys)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Catch any other errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate course: {str(e)}"
        )


@router.post(
    "/validate",
    response_model=TopicValidationResult,
    status_code=status.HTTP_200_OK,
    summary="Validate a topic before course generation",
    description="Checks if a topic is suitable for course generation. Returns validation status, suggestions, and complexity assessment."
)
async def validate_topic(
    request: GenerateCourseRequest
):
    """
    Validate a topic before generating a course.

    This endpoint allows the frontend to check if a topic is valid
    before submitting for course generation. Useful for real-time
    validation and providing user feedback.

    Args:
        request: Request body containing the topic

    Returns:
        TopicValidationResult with status, suggestions, and complexity

    Examples:
        POST /api/v1/courses/validate
        {"topic": "Python Web Development", "difficulty": "beginner"}
        -> {"status": "accepted", "complexity": {...}}

        POST /api/v1/courses/validate
        {"topic": "Physics", "difficulty": "beginner"}
        -> {"status": "rejected", "reason": "too_broad", "suggestions": [...]}
    """
    validator = get_topic_validator()
    return await validator.validate(request.topic)


@router.post(
    "/validate-topic",
    response_model=TopicValidationResult,
    status_code=status.HTTP_200_OK,
    summary="Validate a topic (alias)",
    description="Alias for /validate endpoint.",
    include_in_schema=False  # Hide from docs, use /validate instead
)
async def validate_topic_alias(request: GenerateCourseRequest):
    """Alias for /validate endpoint for backwards compatibility."""
    return await validate_topic(request)


@router.get(
    "/providers",
    response_model=dict,
    summary="Get AI provider configuration",
    description="Returns information about available AI providers and current configuration."
)
async def get_provider_info():
    """
    Get information about configured AI providers.

    Returns:
        Dictionary with provider configuration and availability
    """
    return AIServiceFactory.get_provider_info()


@router.get(
    "/config-presets",
    response_model=dict,
    summary="Get course configuration presets",
    description="Returns the difficulty presets used for course configuration."
)
async def get_config_presets():
    """
    Get course configuration presets for each difficulty level.

    Returns:
        Dictionary with presets for beginner, intermediate, and advanced
    """
    configurator = get_course_configurator()
    return {
        "presets": configurator.get_all_presets(),
        "description": {
            "beginner": "Shorter chapters with high-level overviews",
            "intermediate": "Balanced depth with practical examples",
            "advanced": "Comprehensive coverage with expert-level content"
        }
    }


@router.get(
    "/supported-topics",
    response_model=dict,
    summary="Get list of topics with specific mock data",
    description="Returns topics that have predefined mock data (only relevant when using mock provider)."
)
async def get_supported_topics():
    """
    Get list of topics that have specific mock data.
    Only relevant when using the mock provider.

    Returns:
        Dictionary with list of supported topics
    """
    # Get mock service to check supported topics
    mock_service = AIServiceFactory.get_service(
        use_case=UseCase.CHAPTER_GENERATION,
        provider_override="mock"
    )

    topics = mock_service.get_supported_topics()

    return {
        "supported_topics": topics,
        "note": "These topics have specific mock data. Other topics will use generic templates. Only applies to mock provider."
    }
