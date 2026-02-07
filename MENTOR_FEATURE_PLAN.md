# AI Mentor Feedback Feature - Implementation Plan

## Overview

Implement AI Mentor Feedback that triggers after completing N chapters, analyzes quiz results to find weak areas, and generates a Gap Covering Quiz with optional hints.

**Key Decisions:**
- Weak Area Detection: Hybrid (chapter scores + wrong answer analysis)
- Trigger: Backend provides `mentor_available` flag
- Hints: Optional toggle (user chooses to show/hide)
- Scope: Backend only
- **Course Slug**: Courses identified by unique slug (e.g., `python-programming-beginner-a7x3k2`)
- **User-Agnostic Gap Quizzes**: Stored in MongoDB by course slug, reusable across users

---

## Step 1: Add Course Slug

**Files to Modify:**
- `backend/app/models/course.py`
- `backend/app/db/models.py`
- `backend/app/routers/courses.py`

**Changes:**

1. Add slug generation utility:
   ```python
   import secrets
   import re

   def generate_course_slug(topic: str, difficulty: str) -> str:
       """Generate slug like 'python-programming-beginner-a7x3k2'"""
       # Normalize topic: lowercase, replace spaces with hyphens
       base = re.sub(r'[^a-z0-9]+', '-', topic.lower()).strip('-')
       # Truncate to reasonable length
       base = base[:40]
       # Add difficulty and random suffix
       suffix = secrets.token_hex(3)  # 6 alphanumeric chars
       return f"{base}-{difficulty}-{suffix}"
   ```

2. Add `slug` field to Course model:
   ```python
   class Course(BaseModel):
       slug: str  # Unique identifier like "python-programming-beginner-a7x3k2"
       topic: str
       # ... existing fields
   ```

3. Update CourseDocument in db/models.py:
   ```python
   class CourseDocument(BaseModel):
       slug: str = Field(default_factory=lambda: "")  # Generated on create
       # ... existing fields
   ```

4. Update course generation to create slug:
   - In `POST /api/v1/courses/generate`, generate slug before saving
   - Add unique index on `slug` field in MongoDB

5. Add endpoint to get course by slug:
   ```python
   @router.get("/{slug}")
   async def get_course_by_slug(slug: str) -> Course:
       """Get course by unique slug"""
   ```

**Test:** New courses have slugs, existing endpoint works

---

## Step 2: Add Mentor Configuration Settings

**Files to Modify:**
- `backend/app/config.py`

**Changes:**
1. Add settings to `Settings` class:
   ```python
   mentor_chapters_threshold: int = 3
   mentor_weak_score_threshold: float = 0.7
   model_gap_quiz: str = "claude-3-5-haiku-20241022"
   max_tokens_gap_quiz: int = 4000
   ```

2. Add to `UseCase` enum:
   ```python
   GAP_QUIZ_GENERATION = "gap_quiz_generation"
   ```

3. Update `get_model_for_use_case()` and `get_max_tokens_for_use_case()`

**Test:** App starts, settings load from `.env`

---

## Step 3: Create Mentor Data Models

**Files to Create:**
- `backend/app/models/mentor.py`

**Models:**
```python
class WeakConcept(BaseModel):
    chapter_number: int
    chapter_title: str
    concept: str
    wrong_count: int
    total_questions: int
    sample_wrong_questions: List[str]

class WeakArea(BaseModel):
    chapter_number: int
    chapter_title: str
    score: float
    weak_concepts: List[WeakConcept]

class MentorAnalysis(BaseModel):
    user_id: str
    course_slug: str  # Reference by slug
    total_chapters_completed: int
    average_score: float
    weak_areas: List[WeakArea]
    mentor_available: bool

class GapQuizQuestion(BaseModel):
    id: str
    type: Literal["mcq", "true_false"]
    difficulty: QuestionDifficulty
    question_text: str
    options: Optional[List[str]] = None
    correct_answer: Union[str, bool]
    explanation: str
    hint: Optional[str] = None
    source_chapter: int
    source_concept: str

class GapQuiz(BaseModel):
    """User-agnostic gap quiz, stored by course slug"""
    id: str
    course_slug: str  # Links to course, NOT user
    weak_areas_key: str  # Hash of weak areas for lookup
    questions: List[GapQuizQuestion]
    weak_areas_covered: List[str]
    total_questions: int
    include_hints: bool
    created_at: datetime
    provider: str  # AI provider used

class MentorStatusResponse(BaseModel):
    mentor_available: bool
    chapters_completed: int
    chapters_required: int
    average_score: float
    weak_areas_count: int
    course_slug: str

class GenerateGapQuizRequest(BaseModel):
    course_slug: str  # Reference course by slug
    include_hints: bool = False
    max_questions: int = 15

class MentorFeedbackResponse(BaseModel):
    analysis: MentorAnalysis
    feedback: str
    quiz: GapQuiz
    cached: bool  # True if quiz was reused from cache
```

**Test:** Models import without errors

---

## Step 4: Add Gap Quiz MongoDB Storage

**Files to Modify:**
- `backend/app/db/models.py`
- `backend/app/db/crud.py`

**Add GapQuizDocument:**
```python
class GapQuizDocument(BaseModel):
    """Gap quiz stored by course, user-agnostic"""
    course_slug: str  # Links to course
    weak_areas_key: str  # Hash of weak chapter numbers for lookup
    questions: List[Dict[str, Any]]
    weak_areas_covered: List[str]
    include_hints: bool
    provider: str
    created_at: datetime
    updated_at: datetime
```

**Add CRUD operations:**
```python
# Collection: gap_quizzes

async def get_gap_quiz_by_course(
    course_slug: str,
    weak_areas_key: str,
    include_hints: bool
) -> Optional[Dict]:
    """Get cached gap quiz if exists"""

async def save_gap_quiz(quiz: GapQuizDocument) -> str:
    """Save gap quiz, return ID"""

async def list_gap_quizzes_for_course(course_slug: str) -> List[Dict]:
    """List all gap quizzes for a course"""
```

**MongoDB Index:**
```python
# Compound index for fast lookup
gap_quizzes.create_index([
    ("course_slug", 1),
    ("weak_areas_key", 1),
    ("include_hints", 1)
], unique=True)
```

**Test:** Gap quizzes save and retrieve correctly

---

## Step 5: Create Weak Area Analyzer Service

**Files to Create:**
- `backend/app/services/weak_area_analyzer.py`

**Key Methods:**
```python
class WeakAreaAnalyzer:
    async def analyze_user_progress(
        self, user_id: str, course_slug: str
    ) -> MentorAnalysis:
        """
        1. Get course by slug to find topic/difficulty
        2. Fetch all progress records for user/course
        3. Filter chapters with score < threshold (0.7)
        4. For weak chapters, analyze wrong answers
        5. Return MentorAnalysis
        """

    def _identify_weak_chapters(self, progress_records: List[Dict]) -> List[Dict]:
        """Find chapters with score < mentor_weak_score_threshold"""

    def _extract_concepts_from_wrong_answers(
        self, answers: List[Dict], chapter_key_concepts: List[str]
    ) -> List[WeakConcept]:
        """Map wrong answers to key_concepts using text matching"""

    def is_mentor_available(self, chapters_completed: int) -> bool:
        """Check if chapters_completed >= threshold"""

    def generate_weak_areas_key(self, weak_areas: List[WeakArea]) -> str:
        """Generate hash key from weak chapter numbers for cache lookup"""
        chapters = sorted([wa.chapter_number for wa in weak_areas])
        return "-".join(map(str, chapters))

def get_weak_area_analyzer() -> WeakAreaAnalyzer:
    """Singleton factory"""
```

**Test:** Analyzer returns valid MentorAnalysis with mock data

---

## Step 6: Add Gap Quiz Generation to AI Services

**Files to Modify:**
- `backend/app/services/base_ai_service.py` - Add abstract method
- `backend/app/services/mock_ai_service.py` - Implement
- `backend/app/services/claude_ai_service.py` - Implement
- `backend/app/services/openai_ai_service.py` - Implement
- `backend/app/services/gemini_ai_service.py` - Implement

**Add to BaseAIService:**
```python
@abstractmethod
async def generate_gap_quiz(
    self,
    weak_areas: List[WeakArea],
    course_topic: str,
    difficulty: str,
    include_hints: bool = False,
    max_questions: int = 15,
    user_id: Optional[str] = None,
    context: Optional[str] = None
) -> Dict[str, Any]:
    """Generate targeted quiz for weak areas with optional hints."""
    pass
```

**Mock Implementation:** Return template questions based on weak_areas

**Claude/OpenAI/Gemini Prompt:**
```
Generate {max_questions} quiz questions targeting these weak areas:
{weak_areas_json}

For each question:
- Focus on the specific weak concepts listed
- Mix MCQ and True/False types
- Include difficulty levels (easy/medium/hard)
- Provide clear explanations
{if include_hints: "- Include a helpful hint for each question"}

Return JSON: { "questions": [...], "coverage_summary": "..." }
```

**Test:** `?provider=mock` returns valid gap quiz

---

## Step 7: Add Token Usage Operation Type

**Files to Modify:**
- `backend/app/models/token_usage.py`

**Change:**
```python
class OperationType(str, Enum):
    # ... existing
    GAP_QUIZ_GENERATION = "GAP_QUIZ_GENERATION"
```

**Test:** Token usage logged for gap quiz generation

---

## Step 8: Create Mentor Router

**Files to Create:**
- `backend/app/routers/mentor.py`

**Endpoints:**

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/mentor/{course_slug}/status` | Check if mentor available |
| GET | `/api/v1/mentor/{course_slug}/analysis` | Get detailed weak area analysis |
| POST | `/api/v1/mentor/{course_slug}/generate-quiz` | Generate gap covering quiz |
| GET | `/api/v1/mentor/config` | Get mentor configuration |

```python
@router.get("/{course_slug}/status")
async def get_mentor_status(
    course_slug: str,
    current_user = Depends(get_current_user)
) -> MentorStatusResponse:
    """Returns mentor_available flag for frontend"""

@router.get("/{course_slug}/analysis")
async def get_mentor_analysis(
    course_slug: str,
    current_user = Depends(get_current_user)
) -> MentorAnalysis:
    """Returns detailed weak areas analysis for this user"""

@router.post("/{course_slug}/generate-quiz")
async def generate_gap_quiz(
    course_slug: str,
    request: GenerateGapQuizRequest,
    provider: Optional[str] = None,
    current_user = Depends(get_current_user)
) -> MentorFeedbackResponse:
    """
    1. Get weak area analysis for user
    2. Check cache for existing gap quiz (user-agnostic)
    3. If cached, return it with cached=True
    4. If not, generate via AI and save to cache
    5. Generate personalized feedback
    6. Return combined response
    """

@router.get("/config")
async def get_mentor_config():
    """Return current mentor settings"""
```

**Cache Logic in generate_gap_quiz:**
```python
# Generate weak areas key from user's weak chapters
weak_areas_key = analyzer.generate_weak_areas_key(analysis.weak_areas)

# Check cache (user-agnostic)
cached_quiz = await get_gap_quiz_by_course(
    course_slug=course_slug,
    weak_areas_key=weak_areas_key,
    include_hints=request.include_hints
)

if cached_quiz:
    # Reuse existing quiz
    return MentorFeedbackResponse(
        analysis=analysis,
        feedback=await ai_service.generate_feedback(...),
        quiz=cached_quiz,
        cached=True
    )

# Generate new quiz and cache it
new_quiz = await ai_service.generate_gap_quiz(...)
await save_gap_quiz(new_quiz)
return MentorFeedbackResponse(..., cached=False)
```

**Test:** All endpoints respond correctly, caching works

---

## Step 9: Register Mentor Router

**Files to Modify:**
- `backend/app/main.py`

**Changes:**
```python
from app.routers import mentor

app.include_router(
    mentor.router,
    prefix="/api/v1/mentor",
    tags=["mentor"]
)
```

**Test:** `/docs` shows mentor endpoints, API calls work

---

## Step 10: Update .env.example

**Files to Modify:**
- `backend/.env.example`

**Add:**
```env
# Mentor Configuration
MENTOR_CHAPTERS_THRESHOLD=3
MENTOR_WEAK_SCORE_THRESHOLD=0.7
MODEL_GAP_QUIZ=claude-3-5-haiku-20241022
MAX_TOKENS_GAP_QUIZ=4000
```

**Test:** New users know available config options

---

## Files Summary

### New Files:
| File | Purpose |
|------|---------|
| `app/models/mentor.py` | Mentor Pydantic models |
| `app/services/weak_area_analyzer.py` | Weak area detection service |
| `app/routers/mentor.py` | Mentor API endpoints |

### Modified Files:
| File | Changes |
|------|---------|
| `app/models/course.py` | Add slug field, slug generator |
| `app/db/models.py` | Add slug to CourseDocument, add GapQuizDocument |
| `app/db/crud.py` | Add gap quiz CRUD operations |
| `app/routers/courses.py` | Generate slug on create, add get by slug |
| `app/config.py` | Add mentor settings, UseCase |
| `app/services/base_ai_service.py` | Add `generate_gap_quiz()` abstract |
| `app/services/mock_ai_service.py` | Implement `generate_gap_quiz()` |
| `app/services/claude_ai_service.py` | Implement `generate_gap_quiz()` |
| `app/services/openai_ai_service.py` | Implement `generate_gap_quiz()` |
| `app/services/gemini_ai_service.py` | Implement `generate_gap_quiz()` |
| `app/models/token_usage.py` | Add GAP_QUIZ_GENERATION |
| `app/main.py` | Register mentor router |
| `.env.example` | Document new settings |

---

## API Flow

```
User completes chapter N
        |
        v
Frontend calls GET /api/v1/mentor/{course_slug}/status
        |
        v
Backend returns { mentor_available: true/false, course_slug, ... }
        |
        v (if available)
User clicks "Get Mentor Feedback"
        |
        v
Frontend calls POST /api/v1/mentor/{course_slug}/generate-quiz
  { include_hints: true/false }
        |
        v
Backend:
  1. WeakAreaAnalyzer.analyze_user_progress(user_id, course_slug)
  2. Generate weak_areas_key from weak chapters
  3. Check cache: get_gap_quiz_by_course(course_slug, weak_areas_key, hints)
  4. If cached -> reuse quiz (no AI cost)
  5. If not -> AIService.generate_gap_quiz() and save to cache
  6. AIService.generate_feedback() (always personalized)
        |
        v
Returns MentorFeedbackResponse:
  - analysis (user's weak areas)
  - feedback (personalized AI mentor text)
  - quiz (gap covering questions - may be cached)
  - cached (true if quiz was reused)
```

---

## MongoDB Collections

### Existing:
- `courses` - Add `slug` field
- `user_progress` - No changes

### New:
- `gap_quizzes` - User-agnostic gap quiz cache

```javascript
// gap_quizzes document structure
{
  "_id": ObjectId,
  "course_slug": "python-programming-beginner-a7x3k2",
  "weak_areas_key": "1-3-5",  // Chapters 1, 3, 5 are weak
  "questions": [...],
  "weak_areas_covered": ["Variables", "Functions", "Classes"],
  "include_hints": true,
  "provider": "claude",
  "created_at": ISODate,
  "updated_at": ISODate
}

// Index for fast lookup
db.gap_quizzes.createIndex(
  { "course_slug": 1, "weak_areas_key": 1, "include_hints": 1 },
  { unique: true }
)
```

---

## Testing After Each Step

| Step | Command | Expected |
|------|---------|----------|
| 1 | Create course, check slug | Slug like `topic-difficulty-abc123` |
| 2 | `python run.py` | Starts without error |
| 3 | `python -c "from app.models.mentor import *"` | No import error |
| 4 | Save/get gap quiz from MongoDB | CRUD works |
| 5 | Unit test analyzer | Correct analysis |
| 6 | `curl /api/v1/mentor/.../generate-quiz?provider=mock` | Returns quiz |
| 7 | Check MongoDB `token_usage` | GAP_QUIZ logged |
| 8 | `curl /api/v1/mentor/{slug}/status` | Returns status |
| 9 | Open `/docs` | Mentor endpoints visible |
| 10 | Check `.env.example` | New vars documented |
