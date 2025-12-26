"""
Courses API Router
Handles all course-related endpoints with configurable AI providers.
"""
from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional
from app.models.course import GenerateCourseRequest, GenerateCourseResponse
from app.services.ai_service_factory import AIServiceFactory
from app.config import UseCase

# Create router
router = APIRouter()


@router.post(
    "/generate",
    response_model=GenerateCourseResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate course chapters from a topic",
    description="Takes a topic as input and generates a structured course with multiple chapters. Supports multiple AI providers."
)
async def generate_course(
    request: GenerateCourseRequest,
    provider: Optional[str] = Query(
        None, 
        description="AI provider to use: 'claude', 'openai', or 'mock'. If not specified, uses default from config."
    )
):
    """
    Generate a course with chapters based on the provided topic.
    
    Args:
        request: Request body containing the topic
        provider: Optional AI provider override (claude/openai/mock)
        
    Returns:
        GenerateCourseResponse with generated chapters
        
    Raises:
        HTTPException: If topic is invalid or generation fails
        
    Examples:
        # Use default provider (from config)
        POST /api/v1/courses/generate
        {"topic": "Project Management"}
        
        # Force use of mock provider
        POST /api/v1/courses/generate?provider=mock
        {"topic": "Project Management"}
        
        # Use Claude specifically
        POST /api/v1/courses/generate?provider=claude
        {"topic": "Project Management"}
    """
    try:
        # Validate topic
        if not request.topic or not request.topic.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Topic cannot be empty"
            )
        
        # Get the appropriate AI service
        ai_service = AIServiceFactory.get_service(
            use_case=UseCase.CHAPTER_GENERATION,
            provider_override=provider
        )
        
        # Generate chapters
        chapters = await ai_service.generate_chapters(request.topic)
        
        # Determine which provider was actually used
        actual_provider = ai_service.get_provider_name()
        
        # Create response
        response = GenerateCourseResponse(
            topic=request.topic,
            total_chapters=len(chapters),
            chapters=chapters,
            message=f"Generated {len(chapters)} chapters for '{request.topic}' using {actual_provider}"
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
        
    Example Response:
        {
            "default_provider": "claude",
            "available_providers": ["mock", "claude"],
            "models": {
                "chapter_generation": "claude-sonnet-4-20250514",
                "question_generation": "claude-sonnet-4-20250514",
                ...
            }
        }
    """
    return AIServiceFactory.get_provider_info()


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