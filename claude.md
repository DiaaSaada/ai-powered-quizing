# CLAUDE.md - AI Learning Platform

## Project Overview

An AI-powered learning platform backend built with FastAPI. The system takes topics or PDF materials, validates them, breaks them into chapters using AI (Claude/OpenAI), generates quiz questions, tracks user progress, and provides personalized mentoring feedback.

## Tech Stack

- **Framework**: FastAPI (Python 3.12)
- **Database**: MongoDB with Motor (async driver)
- **AI Providers**: Anthropic Claude, OpenAI GPT, Mock (for testing)
- **PDF Processing**: PyPDF2, PyMuPDF - NOT YET IMPLEMENTED
- **Validation**: Pydantic v2

## Project Structure

```
be-ready/
├── app/
│   ├── __init__.py
│   ├── config.py                  # Pydantic Settings, AI provider config
│   ├── main.py                    # FastAPI app entry point
│   ├── models/
│   │   ├── __init__.py
│   │   ├── course.py              # Chapter, Course, CourseConfig models
│   │   └── validation.py          # TopicValidationResult, TopicComplexity
│   ├── services/
│   │   ├── __init__.py
│   │   ├── base_ai_service.py     # Abstract base class (interface)
│   │   ├── ai_service_factory.py  # Factory pattern for provider selection
│   │   ├── mock_ai_service.py     # Mock implementation
│   │   ├── claude_ai_service.py   # Anthropic Claude implementation
│   │   ├── openai_ai_service.py   # OpenAI GPT implementation
│   │   ├── topic_validator.py     # Topic validation service
│   │   └── course_configurator.py # Course structure configuration
│   ├── routers/
│   │   ├── __init__.py
│   │   └── courses.py             # Course generation endpoints
│   ├── db/
│   │   ├── __init__.py
│   │   ├── connection.py          # MongoDB connection management
│   │   ├── models.py              # Document models
│   │   └── crud.py                # Database operations
│   └── utils/
│       └── __init__.py
├── tests/
├── uploads/
├── .env
├── .env.example
├── requirements.txt
├── requirements-minimal.txt
├── test_api.py                    # API test suite
└── run.py                         # Application runner
```

## Commands

```bash
# Run the development server
python run.py

# Or using uvicorn directly
uvicorn app.main:app --reload

# Install dependencies
pip install -r requirements-minimal.txt

# Run API tests
python test_api.py
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Welcome message |
| GET | `/health` | Health check (includes DB status) |
| POST | `/api/v1/courses/validate` | Validate topic before generation |
| POST | `/api/v1/courses/generate` | Generate chapters from topic |
| GET | `/api/v1/courses/providers` | Get AI provider config |
| GET | `/api/v1/courses/config-presets` | Get difficulty presets |
| GET | `/api/v1/courses/supported-topics` | Get mock data topics |

## Course Generation Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    POST /api/v1/courses/generate                    │
│                                                                     │
│  Request: { topic, difficulty, skip_validation? }                   │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Step 1: Topic Validation (TopicValidator)                          │
│  ─────────────────────────────────────────                          │
│  • Quick validation: pattern matching for broad/vague topics        │
│  • AI validation: Claude Haiku analyzes complexity                  │
│                                                                     │
│  Outcomes:                                                          │
│  • "accepted" → continue with complexity score                      │
│  • "rejected" → 400 error with suggestions                          │
│  • "needs_clarification" → 422 error with suggestions               │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Step 2: Course Configuration (CourseConfigurator)                  │
│  ────────────────────────────────────────────────                   │
│  • Uses complexity score (1-10) from validation                     │
│  • Combines with difficulty preset (beginner/intermediate/advanced) │
│  • Returns: recommended_chapters, time_per_chapter, chapter_depth   │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Step 3: Cache Check (MongoDB)                                      │
│  ─────────────────────────────                                      │
│  • Check if course exists for topic + difficulty                    │
│  • If cached → return immediately                                   │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Step 4: Chapter Generation (AI Service)                            │
│  ──────────────────────────────────────                             │
│  • AI generates exactly N chapters based on config                  │
│  • Each chapter has: title, summary, key_concepts, time estimate    │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Step 5: Save to Cache & Return                                     │
│  ────────────────────────────────                                   │
│  • Save to MongoDB for future requests                              │
│  • Return enriched response with study time estimates               │
└─────────────────────────────────────────────────────────────────────┘
```

## Topic Validator

The `TopicValidator` ensures topics are appropriate for course generation.

### Quick Validation (No AI Cost)
- Rejects single-word broad topics: "Physics", "Math", "Business", etc.
- Rejects vague terms: "stuff", "things", "about", etc.
- Allows specific known courses: "Python", "Docker", "Calculus"

### AI Validation (Claude Haiku)
- Analyzes topic complexity (score 1-10)
- Determines if topic fits a single course
- Provides alternative suggestions if rejected

### Usage

```python
from app.services.topic_validator import get_topic_validator

validator = get_topic_validator()

# Quick check only (free)
result = validator.quick_validate("Physics")
# Returns: TopicValidationResult(status="rejected", reason="too_broad", ...)

# Full validation (quick + AI)
result = await validator.validate("Python Web Development")
# Returns: TopicValidationResult(status="accepted", complexity={score: 6, ...})
```

## Course Configurator

The `CourseConfigurator` determines optimal course structure.

### Difficulty Presets

| Difficulty | Chapters | Time/Chapter | Depth |
|------------|----------|--------------|-------|
| beginner | 4-6 | 25 min | overview |
| intermediate | 6-8 | 45 min | detailed |
| advanced | 8-12 | 90 min | comprehensive |

### Complexity Scaling
- Score 1-3: Use minimum chapters for difficulty
- Score 4-6: Use mid-range chapters
- Score 7-10: Use maximum chapters

### Usage

```python
from app.services.course_configurator import get_course_configurator

configurator = get_course_configurator()
config = configurator.get_config(complexity_score=7, difficulty="intermediate")
# Returns: CourseConfig(
#   recommended_chapters=7,
#   estimated_study_hours=5.25,
#   time_per_chapter_minutes=45,
#   chapter_depth="detailed",
#   difficulty="intermediate"
# )
```

## Example API Requests

### Validate Topic Only

```bash
# Check if topic is valid before generating
curl -X POST "http://localhost:8000/api/v1/courses/validate" \
  -H "Content-Type: application/json" \
  -d '{"topic": "Python Web Development with FastAPI"}'

# Response (accepted):
{
  "status": "accepted",
  "topic": "Python Web Development with FastAPI",
  "normalized_topic": "python web development with fastapi",
  "reason": null,
  "message": "This is a well-scoped topic suitable for a single course.",
  "suggestions": [],
  "complexity": {
    "score": 6,
    "level": "intermediate",
    "estimated_chapters": 6,
    "estimated_hours": 15.0,
    "reasoning": "Covers web framework concepts with practical depth"
  }
}

# Response (rejected):
curl -X POST "http://localhost:8000/api/v1/courses/validate" \
  -H "Content-Type: application/json" \
  -d '{"topic": "Physics"}'

{
  "status": "rejected",
  "topic": "Physics",
  "reason": "too_broad",
  "message": "'Physics' is too broad for a single course.",
  "suggestions": [
    "Classical Mechanics for Engineers",
    "Introduction to Quantum Physics",
    "Thermodynamics Fundamentals"
  ]
}
```

### Generate Course with Difficulty

```bash
# Beginner course (4-6 chapters, 25 min each, overview depth)
curl -X POST "http://localhost:8000/api/v1/courses/generate?provider=mock" \
  -H "Content-Type: application/json" \
  -d '{"topic": "Project Management", "difficulty": "beginner"}'

# Intermediate course (6-8 chapters, 45 min each, detailed depth)
curl -X POST "http://localhost:8000/api/v1/courses/generate?provider=mock" \
  -H "Content-Type: application/json" \
  -d '{"topic": "Python Programming", "difficulty": "intermediate"}'

# Advanced course (8-12 chapters, 90 min each, comprehensive depth)
curl -X POST "http://localhost:8000/api/v1/courses/generate?provider=claude" \
  -H "Content-Type: application/json" \
  -d '{"topic": "Machine Learning Fundamentals", "difficulty": "advanced"}'

# Skip validation (for testing)
curl -X POST "http://localhost:8000/api/v1/courses/generate?provider=mock" \
  -H "Content-Type: application/json" \
  -d '{"topic": "Any Topic", "difficulty": "beginner", "skip_validation": true}'
```

### Response Format

```json
{
  "topic": "Python Programming",
  "difficulty": "intermediate",
  "total_chapters": 6,
  "estimated_study_hours": 4.5,
  "time_per_chapter_minutes": 45,
  "complexity_score": 5,
  "message": "Generated 6 intermediate-level chapters using mock",
  "config": {
    "recommended_chapters": 6,
    "estimated_study_hours": 4.5,
    "time_per_chapter_minutes": 45,
    "chapter_depth": "detailed",
    "difficulty": "intermediate"
  },
  "chapters": [
    {
      "number": 1,
      "title": "Python Basics",
      "summary": "Learn the fundamentals of Python programming...",
      "key_concepts": ["Syntax", "Variables", "Data types"],
      "difficulty": "intermediate",
      "estimated_time_minutes": 45
    }
  ]
}
```

## Architecture

### AI Service Pattern

All AI providers implement `BaseAIService` (abstract base class):

```python
class BaseAIService(ABC):
    @abstractmethod
    async def generate_chapters(self, topic: str, config: CourseConfig, content: str = "") -> List[Chapter]

    @abstractmethod
    async def generate_questions(self, chapter: Chapter, num_mcq=5, num_tf=3) -> Dict

    @abstractmethod
    async def generate_feedback(self, user_progress: Dict, weak_areas: List) -> str

    @abstractmethod
    async def check_answer(self, question: str, user_answer: str, correct_answer: str) -> Dict

    @abstractmethod
    async def answer_question(self, question: str, context: str) -> str
```

### Factory Pattern

```python
from app.services.ai_service_factory import AIServiceFactory
from app.config import UseCase

# Get service based on config
service = AIServiceFactory.get_service(UseCase.CHAPTER_GENERATION)

# Override provider
service = AIServiceFactory.get_service(UseCase.CHAPTER_GENERATION, provider_override="mock")
```

### Use Cases (from config.py)

- `UseCase.CHAPTER_GENERATION` - Breaking content into chapters
- `UseCase.QUESTION_GENERATION` - Creating quiz questions
- `UseCase.STUDENT_FEEDBACK` - Personalized feedback
- `UseCase.ANSWER_CHECKING` - Evaluating answers
- `UseCase.RAG_QUERY` - Answering student questions
- `UseCase.TOPIC_VALIDATION` - Validating topics (Claude Haiku)

## Configuration

Environment variables in `.env`:

```env
# API Keys
ANTHROPIC_API_KEY=sk-ant-api03-...
OPENAI_API_KEY=sk-...  # Optional

# Provider selection: mock | claude | openai
DEFAULT_AI_PROVIDER=mock

# Models per use case
MODEL_CHAPTER_GENERATION=mock           # or claude-sonnet-4-20250514
MODEL_QUESTION_GENERATION=mock          # or claude-sonnet-4-20250514
MODEL_STUDENT_FEEDBACK=mock             # or claude-sonnet-4-20250514
MODEL_ANSWER_CHECKING=mock              # or claude-haiku-4-5-20251001
MODEL_RAG_QUERY=mock                    # or claude-haiku-4-5-20251001
MODEL_TOPIC_VALIDATION=mock             # or claude-haiku-3-5-20241022

# Token Limits
MAX_TOKENS_CHAPTER=4000
MAX_TOKENS_QUESTION=2000
MAX_TOKENS_VALIDATION=500

# Database
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=ai_learning_platform
```

## Current Status

### Completed
- FastAPI application setup
- Pydantic models for Course, Chapter, Questions, Validation
- Abstract AI service interface (BaseAIService)
- AI Service Factory with provider routing
- Mock AI service (difficulty-aware)
- Claude AI service implementation
- OpenAI AI service implementation
- Topic Validator with quick + AI validation
- Course Configurator with difficulty presets
- MongoDB integration with caching
- POST /api/v1/courses/generate endpoint
- POST /api/v1/courses/validate endpoint
- GET /api/v1/courses/config-presets endpoint
- Per-use-case model configuration
- Runtime provider override via query parameter
- Comprehensive test suite

### TODO
1. **PDF Upload** - Extract text from PDFs, generate chapters
2. **Question Generation Endpoint** - Generate MCQ/True-False per chapter
3. **Progress Tracking** - Track user answers and scores
4. **AI Mentor Feedback** - Personalized study recommendations
5. **RAG System** - Vector embeddings for document Q&A
6. **User Authentication** - JWT or session-based auth
7. **Frontend** - React/Vue UI

## Code Style

- Use async/await for all I/O operations
- Use Pydantic models for request/response validation
- Follow FastAPI dependency injection patterns
- Use type hints everywhere
- Services go in `app/services/`
- API routes go in `app/routers/`
- Database operations go in `app/db/`

## Key Files to Understand

1. `app/config.py` - All settings, AI model configuration
2. `app/services/base_ai_service.py` - Interface all providers implement
3. `app/services/topic_validator.py` - Topic validation logic
4. `app/services/course_configurator.py` - Course structure configuration
5. `app/routers/courses.py` - Main API endpoints with validation flow
6. `app/models/course.py` - Data structures
7. `app/models/validation.py` - Validation result models

## Adding a New AI Provider

1. Create `app/services/new_provider_service.py`
2. Extend `BaseAIService`
3. Implement all abstract methods
4. Add to factory in `ai_service_factory.py`
5. Update config.py if needed

## Testing

```bash
# Run server first
python run.py

# In another terminal, run test suite
python test_api.py

# Or test individual endpoints with curl
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/courses/providers
curl http://localhost:8000/api/v1/courses/config-presets
```

## Common Issues

**ModuleNotFoundError: No module named 'app'**
→ Run from project root: `cd D:\Projects\be-ready && python run.py`

**ValidationError: Extra inputs are not permitted**
→ Update `.env` file - old variable names don't match new config.py

**OpenAI/Claude API errors**
→ Check API key in `.env`, ensure provider is set correctly

**Topic rejected unexpectedly**
→ Use `skip_validation: true` for testing, or provide more specific topic
