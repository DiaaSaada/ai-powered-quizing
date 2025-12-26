# Claude Code - Quick Reference Guide

## 🎯 Project: AI Learning Platform (be-ready)

**Location:** `D:\Projects\be-ready`

---

## Current Status

✅ Step 1: Project Foundation - COMPLETE
✅ Step 2: Mock Chapter Generation - COMPLETE  
✅ Step 3: Configurable AI Architecture - COMPLETE
⏳ Step 4: MongoDB Integration - TODO
⏳ Step 5: PDF Processing - TODO
⏳ Step 6: Question Generation - TODO
⏳ Step 7: Progress Tracking - TODO
⏳ Step 8: AI Mentor Feedback - TODO

---

## Quick Start Commands

```bash
# Navigate to project
cd D:\Projects\be-ready

# Run server
python run.py

# Test endpoint
curl -X POST "http://localhost:8000/api/v1/courses/generate?provider=mock" -H "Content-Type: application/json" -d "{\"topic\": \"Python\"}"

# API Docs
# http://localhost:8000/docs
```

---

## File Overview

### Core Files:
- `app/config.py` - All configuration (AI providers, models, tokens)
- `app/main.py` - FastAPI app entry point
- `app/models/course.py` - Pydantic models (Chapter, Course, etc.)
- `app/routers/courses.py` - API endpoints

### AI Services:
- `app/services/base_ai_service.py` - Abstract interface (ABC)
- `app/services/ai_service_factory.py` - Routes to correct provider
- `app/services/mock_ai_service.py` - Mock (no API calls)
- `app/services/claude_ai_service.py` - Claude/Anthropic
- `app/services/openai_ai_service.py` - OpenAI/GPT

### Config Files:
- `.env` - Your actual configuration
- `.env.example` - Template with all options
- `requirements.txt` - Full dependencies
- `requirements-minimal.txt` - Core dependencies only

---

## Architecture Pattern

```
Endpoint → Router → Factory → AI Service → Response
                       ↓
                   UseCase
                       ↓
              Config (which model?)
                       ↓
            Claude / OpenAI / Mock
```

---

## Key Interfaces

### BaseAIService Methods (all providers implement these):
```python
async def generate_chapters(topic: str, content: str = "") -> List[Chapter]
async def generate_questions(chapter: Chapter, num_mcq=5, num_tf=3) -> Dict
async def generate_feedback(user_progress: Dict, weak_areas: List) -> str
async def check_answer(question: str, user_answer: str, correct_answer: str) -> Dict
async def answer_question(question: str, context: str) -> str
```

### Using the Factory:
```python
from app.services.ai_service_factory import AIServiceFactory
from app.config import UseCase

# Get service for specific use case
service = AIServiceFactory.get_service(UseCase.CHAPTER_GENERATION)

# Override provider
service = AIServiceFactory.get_service(UseCase.CHAPTER_GENERATION, provider_override="mock")

# Generate chapters
chapters = await service.generate_chapters("Machine Learning")
```

---

## Environment Variables (.env)

```env
# Must set for real AI
ANTHROPIC_API_KEY=sk-ant-api03-...

# Provider: mock | claude | openai
DEFAULT_AI_PROVIDER=mock

# Models per use case
MODEL_CHAPTER_GENERATION=mock        # or claude-sonnet-4-20250514
MODEL_QUESTION_GENERATION=mock       # or claude-sonnet-4-20250514
MODEL_ANSWER_CHECKING=mock           # or claude-haiku-4-5-20251001
```

---

## Next Step: MongoDB Integration

### What to Add:
1. MongoDB connection in `app/db/connection.py`
2. Database models in `app/db/models.py`
3. CRUD operations in `app/db/crud.py`
4. Update routers to save/retrieve from DB
5. Add caching to avoid regenerating same topics

### Suggested Schema:
```python
# Courses collection
{
    "_id": ObjectId,
    "topic": "Project Management",
    "material_hash": "sha256...",  # For PDF caching
    "chapters": [...],
    "created_at": datetime
}

# User Progress collection
{
    "_id": ObjectId,
    "user_id": "user_123",
    "course_id": ObjectId,
    "chapter_progress": {
        "1": {"score": 0.85, "attempts": 2}
    },
    "overall_score": 0.75
}
```

---

## Common Issues & Fixes

**Issue:** `ModuleNotFoundError: No module named 'app'`
**Fix:** Run from project root: `cd D:\Projects\be-ready && python run.py`

**Issue:** `ValidationError: Extra inputs are not permitted`
**Fix:** Update `.env` file with new variable names (see .env.example)

**Issue:** `ANTHROPIC_API_KEY not set`
**Fix:** Add your API key to `.env` file

---

## Useful Prompts for Claude Code

### Add MongoDB:
```
Add MongoDB integration to the project:
- Use motor for async MongoDB
- Create connection in app/db/
- Add caching for generated courses
- Save courses by topic hash
```

### Add PDF Upload:
```
Add PDF upload endpoint:
- POST /api/v1/courses/upload
- Accept PDF file
- Extract text using PyPDF2
- Generate chapters from PDF content
- Return course with chapters
```

### Add Question Generation:
```
Add question generation endpoint:
- POST /api/v1/courses/{course_id}/chapters/{chapter_num}/questions
- Use AI service to generate MCQ and True/False
- Save questions to database
- Return generated questions
```

---

**Good luck with Claude Code! 🚀**