"""
Mentor feature data models for weak area analysis and gap quiz generation.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Union, Literal
from datetime import datetime


class WrongAnswer(BaseModel):
    """A wrong answer from a completed quiz - included for free in gap quiz."""
    question_id: str = Field(..., description="Original question ID")
    question_text: str = Field(..., description="The question text")
    question_type: Literal["mcq", "true_false"] = Field(..., description="Question type")
    options: Optional[List[str]] = Field(default=None, description="MCQ options if applicable")
    user_answer: str = Field(..., description="What the user answered")
    correct_answer: Union[str, bool] = Field(..., description="The correct answer")
    explanation: str = Field(..., description="Explanation of the correct answer")
    chapter_number: int = Field(..., description="Source chapter number")
    chapter_title: str = Field(..., description="Source chapter title")
    hint: Optional[str] = Field(default=None, description="Optional hint for the question")


class WeakConcept(BaseModel):
    """A specific concept the user is weak in within a chapter."""
    concept: str = Field(..., description="The concept name/topic")
    wrong_count: int = Field(..., description="Number of wrong answers for this concept")
    total_questions: int = Field(..., description="Total questions on this concept")
    sample_questions: List[str] = Field(default_factory=list, description="Sample wrong question texts")


class WeakArea(BaseModel):
    """A chapter identified as a weak area for the user."""
    chapter_number: int = Field(..., description="Chapter number")
    chapter_title: str = Field(..., description="Chapter title")
    score: float = Field(..., description="User's score on this chapter (0.0 - 1.0)")
    questions_total: int = Field(..., description="Total questions in chapter")
    questions_wrong: int = Field(..., description="Number of wrong answers")
    weak_concepts: List[WeakConcept] = Field(default_factory=list, description="Weak concepts in this chapter")


class MentorAnalysis(BaseModel):
    """Complete analysis of user's weak areas for a course."""
    course_slug: str = Field(..., description="Course slug identifier")
    course_topic: str = Field(..., description="Course topic")
    difficulty: str = Field(..., description="Course difficulty level")
    total_chapters_completed: int = Field(..., description="Number of chapters user completed")
    total_chapters: int = Field(..., description="Total chapters in course")
    average_score: float = Field(..., description="User's average score across all chapters")
    weak_areas: List[WeakArea] = Field(default_factory=list, description="List of weak chapters")
    total_wrong_answers: int = Field(..., description="Total wrong answers across all chapters")
    mentor_available: bool = Field(..., description="Whether mentor feature is available")


class GapQuizQuestion(BaseModel):
    """An AI-generated extra question for the gap quiz."""
    id: str = Field(..., description="Unique question ID")
    question_type: Literal["mcq", "true_false"] = Field(..., description="Question type")
    difficulty: Literal["easy", "medium", "hard"] = Field(..., description="Question difficulty")
    question_text: str = Field(..., description="The question text")
    options: Optional[List[str]] = Field(default=None, description="MCQ options")
    correct_answer: Union[str, bool] = Field(..., description="Correct answer")
    explanation: str = Field(..., description="Explanation of the answer")
    hint: Optional[str] = Field(default=None, description="Optional hint")
    source_chapter: int = Field(..., description="Chapter this targets")
    target_concept: str = Field(..., description="Concept this question reinforces")


class GapQuiz(BaseModel):
    """Complete gap quiz with wrong answers and optional extra questions."""
    id: str = Field(..., description="Unique gap quiz ID")
    course_slug: str = Field(..., description="Course slug identifier")
    user_id: str = Field(..., description="User ID this quiz is for")
    wrong_answers: List[WrongAnswer] = Field(default_factory=list, description="Wrong answers to retry (free)")
    extra_questions: List[GapQuizQuestion] = Field(default_factory=list, description="AI-generated extras (optional)")
    total_questions: int = Field(..., description="Total questions in quiz")
    wrong_answers_count: int = Field(..., description="Number of wrong answer retries")
    extra_questions_count: int = Field(..., description="Number of AI-generated extras")
    include_hints: bool = Field(default=False, description="Whether hints are shown")
    cache_hit: bool = Field(default=False, description="Whether extra questions came from cache")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When quiz was generated")


class MentorStatusResponse(BaseModel):
    """Response for mentor status check endpoint."""
    mentor_available: bool = Field(..., description="Whether mentor feature is available")
    chapters_completed: int = Field(..., description="Number of chapters completed")
    chapters_required: int = Field(..., description="Chapters required to unlock mentor")
    average_score: float = Field(..., description="User's average score")
    weak_areas_count: int = Field(..., description="Number of weak chapters identified")
    total_wrong_answers: int = Field(..., description="Total wrong answers available for review")


class GenerateGapQuizRequest(BaseModel):
    """Request to generate a gap quiz."""
    course_slug: str = Field(..., description="Course slug to generate quiz for")
    include_hints: bool = Field(default=False, description="Include hints in questions")
    generate_extra: bool = Field(default=False, description="Generate AI extra questions")
    extra_questions_count: int = Field(default=5, ge=1, le=20, description="Number of extra questions if generating")


class MentorFeedbackResponse(BaseModel):
    """Complete mentor feedback response with analysis and quiz."""
    analysis: MentorAnalysis = Field(..., description="Weak area analysis")
    feedback_text: str = Field(..., description="AI-generated mentor feedback")
    quiz: GapQuiz = Field(..., description="The gap quiz")
