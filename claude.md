# CLAUDE.md - AI Learning Platform

## Project Overview

An AI-powered learning platform backend built with FastAPI. The system takes topics or PDF materials, breaks them into chapters using AI (Claude/OpenAI), generates quiz questions, tracks user progress, and provides personalized mentoring feedback.

## Tech Stack

- **Framework**: FastAPI (Python 3.12)
- **Database**: MongoDB with Motor (async driver) - NOT YET IMPLEMENTED
- **AI Providers**: Anthropic Claude, OpenAI GPT, Mock (for testing)
- **PDF Processing**: PyPDF2, PyMuPDF - NOT YET IMPLEMENTED
- **Validation**: Pydantic v2

## Project Structure

```
be-ready/
├── app/
│   ├── __init__.py
│   ├── config.py              # Pydantic Settings, AI provider config
│   ├── main.py                # FastAPI app entry point
│   ├── models/
│   │   ├── __init__.py
│   │   └── course.py          # Pydantic models: Chapter, Course, Request/Response
│   ├── services/
│   │   ├── __init__.py
│   │   ├── base_ai_service.py     # Abstract base class (interface)
│   │   ├── ai_service_factory.py  # Factory pattern for provider selection
│   │   ├── mock_ai_service.py     # Mock implementation
│   │   ├── claude_ai_service.py   # Anthropic Claude implementation
│   │   └── openai_ai_service.py   # OpenAI GPT implementation
│   ├── routers/
│   │   ├── __init__.py
│   │   └── courses.py         # Course generation endpoints
│   ├── db/                    # Database layer (TODO)
│   │   └── __init__.py
│   └── utils/                 # Utilities (TODO)
│       └── __init__.py
├── tests/                     # Tests (TODO)
├── uploads/                   # Uploaded files directory
├── .env                       # Environment configuration
├── .env.example               # Environment template
├── requirements.txt           # Full dependencies
├── requirements-minimal.txt   # Core dependencies
└── run.py                     # Application runner
```

## Commands

```bash
# Run the development server
python run.py

# Or using uvicorn directly
uvicorn app.main:app --reload

# Install dependencies
pip install -r requirements-minimal.txt

# Test project structure
python test_structure.py

# Test API endpoints
python test_api.py
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Welcome message |
| GET | `/health` | Health check |
| POST | `/api/v1/courses/generate` | Generate chapters from topic |
| GET | `/api/v1/courses/providers` | Get AI provider config |
| GET | `/api/v1/courses/supported-topics` | Get mock data topics |

### Generate Chapters

```bash
# Using mock (free, no API key needed)
curl -X POST "http://localhost:8000/api/v1/courses/generate?provider=mock" \
  -H "Content-Type: application/json" \
  -d '{"topic": "Project Management"}'

# Using Claude (requires ANTHROPIC_API_KEY in .env)
curl -X POST "http://localhost:8000/api/v1/courses/generate?provider=claude" \
  -H "Content-Type: application/json" \
  -d '{"topic": "Project Management"}'
```

## Architecture

### AI Service Pattern

All AI providers implement `BaseAIService` (abstract base class):

```python
class BaseAIService(ABC):
    @abstractmethod
    async def generate_chapters(self, topic: str, content: str = "") -> List[Chapter]
    
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

Use `AIServiceFactory` to get the appropriate service:

```python
from app.services.ai_service_factory import AIServiceFactory
from app.config import UseCase

# Get service based on config
service = AIServiceFactory.get_service(UseCase.CHAPTER_GENERATION)

# Override provider
service = AIServiceFactory.get_service(UseCase.CHAPTER_GENERATION, provider_override="mock")

# Use the service
chapters = await service.generate_chapters("Machine Learning")
```

### Use Cases (from config.py)

- `UseCase.CHAPTER_GENERATION` - Breaking content into chapters
- `UseCase.QUESTION_GENERATION` - Creating quiz questions
- `UseCase.STUDENT_FEEDBACK` - Personalized feedback
- `UseCase.ANSWER_CHECKING` - Evaluating answers
- `UseCase.RAG_QUERY` - Answering student questions

## Configuration

Environment variables in `.env`:

```env
# Required for real AI
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

# Database (not yet implemented)
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=ai_learning_platform
```

## Current Status

### ✅ Completed
- FastAPI application setup
- Pydantic models for Course, Chapter, Questions
- Abstract AI service interface (BaseAIService)
- AI Service Factory with provider routing
- Mock AI service (for testing without API costs)
- Claude AI service implementation
- OpenAI AI service implementation
- POST /api/v1/courses/generate endpoint
- Per-use-case model configuration
- Runtime provider override via query parameter

### ❌ TODO
1. **MongoDB Integration** - Save courses, cache generated content
2. **PDF Upload** - Extract text from PDFs, generate chapters
3. **Question Generation Endpoint** - Generate MCQ/True-False per chapter
4. **Progress Tracking** - Track user answers and scores
5. **AI Mentor Feedback** - Personalized study recommendations
6. **RAG System** - Vector embeddings for document Q&A
7. **User Authentication** - JWT or session-based auth
8. **Frontend** - React/Vue UI

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
3. `app/services/ai_service_factory.py` - Routes to correct provider
4. `app/routers/courses.py` - Main API endpoints
5. `app/models/course.py` - Data structures

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

# In another terminal, test with mock
curl -X POST "http://localhost:8000/api/v1/courses/generate?provider=mock" \
  -H "Content-Type: application/json" \
  -d '{"topic": "Python Programming"}'

# Check provider config
curl http://localhost:8000/api/v1/courses/providers
```

## Common Issues

**ModuleNotFoundError: No module named 'app'**
→ Run from project root: `cd D:\Projects\be-ready && python run.py`

**ValidationError: Extra inputs are not permitted**
→ Update `.env` file - old variable names don't match new config.py

**OpenAI/Claude API errors**
→ Check API key in `.env`, ensure provider is set correctly